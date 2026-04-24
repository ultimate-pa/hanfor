import logging
from os import path, listdir
from threading import Event

from flask_socketio import SocketIO

from ai_addons.threading_ai_socketio import send_ai_update
from ai_addons.ai_addon_handler import AiAddonAbstractClass
from ai_request.ai_core_requests import AiRequest
from hanfor_flask import current_app
from lib_core.data import Requirement
from lib_core.pattern import APattern
from thread_handling.threading_core import SchedulingClass, ThreadTask, ThreadGroup, ThreadHandler, TaskResult

import json
from dataclasses import dataclass


@dataclass
class PatternPredictionTreeOption:
    id: str
    answer: str
    next_node: "PatternPredictionTreeNode | PatternPredictionTreeLeaf"
    parent: "PatternPredictionTreeNode"


@dataclass
class PatternPredictionTreeNode:
    id: str
    question: str
    answers: list[PatternPredictionTreeOption]
    parent: "PatternPredictionTreeNode | None" = None


@dataclass
class PatternPredictionTreeLeaf:
    id: str
    pattern_name: str
    pattern: APattern
    parent: "PatternPredictionTreeNode | None" = None


class Tree:

    def __init__(self, tree_path: str):
        self.root: PatternPredictionTreeNode | PatternPredictionTreeLeaf | None = None
        self.id_map: dict[int, int] = {}
        base_dir = path.join(path.dirname(path.abspath(__file__)), "tree")
        self.load(path.join(base_dir, tree_path))

    def load(self, tree_path: str):
        with open(tree_path, encoding="utf-8") as f:
            data = json.load(f)

        self.id_map[0] = 0
        self.root = self._parse_node(data["root"], 0)

    def _parse_node(self, data: dict, depth: int) -> PatternPredictionTreeNode | PatternPredictionTreeLeaf:
        self.id_map.setdefault(depth, 0)
        node_id = f"_D-{hex(depth)}_W-{hex(self.id_map[depth])}"

        if "pattern" in data:
            # Leaf node - no further branching
            self.id_map[depth] += 1
            patterns = APattern().get_patterns()
            pattern = patterns[data["pattern"]] if data["pattern"] in patterns.keys() else APattern()
            return PatternPredictionTreeLeaf(id="p" + node_id, pattern_name=data["pattern"], pattern=pattern)

        # Inner node - recurse into answers
        node = PatternPredictionTreeNode(id="q" + node_id, question=data["question"], answers=[])
        self.id_map[depth] += 1
        for ans in data.get("answers", []):
            next_node = self._parse_node(ans["next"], depth + 1)
            option = PatternPredictionTreeOption(
                id=f"a{node_id}_{ans['answer'].replace(' ', '_')}",
                answer=ans["answer"],
                next_node=next_node,
                parent=node,
            )
            next_node.parent = node
            node.answers.append(option)
        return node

    def to_dict(self, node: "PatternPredictionTreeNode | PatternPredictionTreeLeaf | None" = None) -> dict:

        if node is None:
            node = self.root
        if node is None:
            return {}

        if isinstance(node, PatternPredictionTreeLeaf):
            return {"id": node.id, "pattern": node.pattern.get_text()}

        return {
            "id": node.id,
            "question": node.question,
            "answers": [
                {"answer": opt.answer, "id": opt.id, "next": self.to_dict(opt.next_node)} for opt in node.answers
            ],
        }


@dataclass
class PatternPredictedRequirement:
    id: str
    description: str
    trace: list[dict]
    detailed_trace: list[dict]
    pattern: APattern
    pattern_name: str
    final_node: "PatternPredictionTreeLeaf | None" = None


class PatternPrediction(AiAddonAbstractClass):
    required_dependencies = ["thread_handler", "ai_request", "socketio"]
    thread_handler: ThreadHandler
    ai_request: AiRequest
    socketio: SocketIO

    def _do_initialize(self):
        self.__tree_path = "pattern_tree_longer_questions.json"
        self.__export_to_file = False
        self.requirement_data: dict[str, PatternPredictedRequirement] = {}
        self.socketio_data: dict[str, list[str]] = {}
        self.prediction_tree = None
        self.selected_ensemble: list[dict[str, str | int | float]] = [
            {"id": 1, "provider": "", "model": "", "count": 1, "weight": 1.0}
        ]

        for provider_name, provider_data in self.ai_request.ai_model_catalog().items():
            if provider_data.default_provider:
                self.selected_ensemble[0]["provider"] = provider_name
                self.selected_ensemble[0]["model"] = provider_data.default_model
        self.prediction_tree = Tree(self.__tree_path)
        for req_id, requirement in current_app.db.get_objects(Requirement).items():
            self.requirement_data[str(req_id)] = PatternPredictedRequirement(
                str(req_id), requirement.description, [], [], APattern(), "", None
            )

    @property
    def addon_name(self) -> str:
        return "Pattern Prediction"

    @property
    def addon_description(self) -> str:
        return "Using a decision tree, a requirement can be assigned to a pattern with the help of an AI."

    @property
    def addon_js(self) -> str:
        return "dist/pattern_prediction-bundle.js"

    @property
    def addon_html(self) -> str:
        return "ai_addons/pattern_prediction.html"

    @AiAddonAbstractClass.requires_enabled
    def predict_patterns_for_all_requirements(self, requirements, stop_event: Event):
        for req_id, requirement in requirements.items():
            if stop_event.is_set():
                break
            task = ThreadTask(
                self.predict_pattern_for_requirement,
                SchedulingClass.CALLER_DEPTH_1,
                ThreadGroup.PATTERN_PREDICTION,
                None,
                None,
                (req_id, requirement.description),
                {},
            )
            self.thread_handler.submit(task)

    @AiAddonAbstractClass.requires_enabled
    def set_selected_ensemble(self, ensemble: list[dict]):
        self.selected_ensemble = ensemble
        send_ai_update({"ensemble": self.selected_ensemble}, "socket_pattern_prediction_ensemble", self.socketio)

    @AiAddonAbstractClass.requires_enabled
    def get_selected_ensemble(self) -> list[dict]:
        return self.selected_ensemble

    @AiAddonAbstractClass.requires_enabled
    def set_sid_for_req(self, req, sid):
        if req not in self.socketio_data:
            self.socketio_data[req] = []
        self.socketio_data[req].append(sid)
        self.update_trace_frontend(req)

    @AiAddonAbstractClass.requires_enabled
    def clear_sid_for_req(self, req, sid):
        if req in self.socketio_data:
            self.socketio_data[req].remove(sid)
            if not self.socketio_data[req]:
                self.socketio_data.pop(req)

    @AiAddonAbstractClass.requires_enabled
    def update_trace_frontend(self, req_id: str, status=None):
        if status is None:
            status = {}
        if req_id not in self.requirement_data:
            return

        pattern_data = self.requirement_data[req_id]

        steps = [
            {"nodeId": step["nodeId"], "answer": step["chosen"], "confidences": step["scores"]}
            for step in pattern_data.trace
        ]

        if isinstance(pattern_data.final_node, PatternPredictionTreeLeaf):
            steps.append({"nodeId": pattern_data.final_node.id, "answer": None, "confidences": {}})

        payload = {
            "id": req_id,
            "desc": pattern_data.description,
            "pattern": pattern_data.pattern.get_text(),
            "steps": steps,
        }
        for sid in self.socketio_data.get(req_id, []):
            if status:
                send_ai_update(status, "socket_pattern_prediction_error", self.socketio, sid)
            else:
                send_ai_update(payload, "socket_pattern_prediction", self.socketio, sid)

    @AiAddonAbstractClass.requires_enabled
    def predict_pattern_for_requirement(self, req_id: str, req_desc: str, stop_event: Event):
        node = self.prediction_tree.root
        trace = []
        detailed_trace = []

        while isinstance(node, PatternPredictionTreeNode):
            if stop_event.is_set():
                self._abort_prediction(req_id, trace)
                return

            query = self._build_query(req_desc, node)
            answer_options = [o.answer for o in node.answers]

            task_results: list[tuple[TaskResult, float, str]] = []

            for entry in self.selected_ensemble:
                for _ in range(int(entry["count"])):
                    task_results.append(
                        (
                            self.ai_request.ask_ai(
                                query,
                                None,
                                SchedulingClass.CALLER_DEPTH_2,
                                str(entry["provider"]),
                                str(entry["model"]),
                            ),
                            float(entry["weight"]),
                            f"{entry['provider']}-{entry['model']}",
                        )
                    )

            if stop_event.is_set():
                self._abort_prediction(req_id, trace)
                return

            result, ai_status, model_ansers = self._collect_scores(task_results, answer_options)
            if result is None:
                self._abort_prediction(req_id, trace, error=ai_status)
                return

            best_key = max(result, key=lambda k: result[k])
            trace.append({"nodeId": node.id, "question": node.question, "scores": result.copy(), "chosen": best_key})
            detailed_trace.append(
                {
                    "nodeId": node.id,
                    "question": node.question,
                    "scores": result.copy(),
                    "chosen": best_key,
                    "model_answers": model_ansers,
                }
            )

            data = self.requirement_data[req_id]
            data.trace = trace
            data.detailed_trace = detailed_trace
            data.pattern = APattern()
            data.final_node = None
            self.update_trace_frontend(req_id)

            next_node = next((a.next_node for a in node.answers if a.answer == best_key), None)
            if next_node is not None:
                node = next_node

        # Leaf reached - store final pattern
        data = self.requirement_data[req_id]
        data.trace = trace
        data.pattern = node.pattern
        data.pattern_name = node.pattern_name
        data.final_node = node
        self.update_trace_frontend(req_id)

    @AiAddonAbstractClass.requires_enabled
    def get_all_detailed_traces_as_file(self) -> dict:

        traces = {}

        for req_id, req_data in self.requirement_data.items():
            trace = req_data.detailed_trace
            if trace is not None:
                traces[req_id] = {
                    "detailed_trace": trace,
                    "chosen Pattern": f"{req_data.pattern_name}: {req_data.pattern.get_text()}",
                }

        return traces

    def _abort_prediction(self, req_id: str, trace: list, error: str | None = None):
        """Reset requirement state and notify frontend on prediction abort."""
        data = self.requirement_data[req_id]
        data.trace = trace
        data.pattern = APattern()
        data.final_node = None
        self.update_trace_frontend(req_id, {"error": error} if error else None)

    @staticmethod
    def _build_query(req_desc: str, node: PatternPredictionTreeNode) -> str:
        """Build the AI prompt for a given requirement and decision tree node"""
        options = "\n".join(o.answer for o in node.answers)
        return (
            f"Requirement: {req_desc}\n\n"
            f"Current question: {node.question}\n"
            f"Options:\n{options}\n\n"
            "Respond ONLY with lines in the exact format:\n"
            "<answer>:<score>\n\n"
            "Rules:\n"
            "- One line per answer option.\n"
            "- Score must be a number between 0 and 1.\n"
            "- No explanations.\n"
            "- No additional text.\n"
            "- all scores must be addup to exactly 1"
            "- Output ONLY the answer lines.\n\n"
            "Example:\n"
            "Yes:0.7\n"
            "No:0.3\n"
        )

    @staticmethod
    def _collect_scores(
        task_results: list[tuple[TaskResult, float, str]], answer_options: list[str]
    ) -> tuple[dict[str, float] | None, str | None, None | list]:
        """Aggregate and normalize scores from all AI responses. Returns None on error."""
        result = {a: 0.0 for a in answer_options}
        model_ansers = []
        successful = 0

        for task_result, weight, provider_model_pair in task_results:
            if not task_result:
                continue

            ai_response, ai_status = task_result.result()

            if isinstance(ai_status, str) and ai_status.startswith("error"):
                logging.warning(f"AI request failed: {ai_status}")
                return None, ai_status, None

            if isinstance(ai_status, str) and ai_status == "cancelled":
                logging.warning(f"AI request cancelled!")
                return None, ai_status, None

            if not ai_response:
                continue

            model_ansers_model_response = {"provider-model": provider_model_pair, "weight": weight, "answers": []}

            for line in ai_response.splitlines():
                if ":" not in line:
                    continue
                try:
                    ai_answer, score = line.split(":", 1)
                    ai_answer = ai_answer.strip()
                    score = float(score.replace(",", "."))
                except (ValueError, AttributeError) as e:
                    logging.warning(
                        f"Couldn't parse AI response line '{line}': {e}\nFull answer: {ai_response}, status: {ai_status}"
                    )
                    continue

                if ai_answer in answer_options:
                    model_ansers_model_response["answers"].append((ai_answer, score))
                    result[ai_answer] += score * weight
            successful += 1 * weight
            model_ansers.append(model_ansers_model_response)

        # Normalize across successful responses
        for k in result:
            result[k] /= max(successful, 1)

        return result, None, model_ansers

    @AiAddonAbstractClass.requires_enabled
    def get_all_tree_file(self):
        tree_dir = path.join(str(path.dirname(__file__)), "tree")
        return [f for f in listdir(str(tree_dir)) if path.isfile(path.join(str(tree_dir), f))]

    @AiAddonAbstractClass.requires_enabled
    def get_tree_file_name(self):
        return self.__tree_path

    @AiAddonAbstractClass.requires_enabled
    def select_tree_file(self, tree_path: str):
        self.__tree_path = tree_path
        self.thread_handler.stop_group(ThreadGroup.PATTERN_PREDICTION)

        self.prediction_tree = Tree(self.__tree_path)

        send_ai_update(
            {"file": self.get_tree_file_name(), "tree": self.prediction_tree.to_dict()},
            "socket_pattern_prediction_new_tree",
            self.socketio,
        )
