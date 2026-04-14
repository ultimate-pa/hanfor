import logging
from threading import Event
from flask_socketio import SocketIO
from ai_addons.threading_ai_socketio import send_ai_update
from ai_addons.ai_addon_handler import AiAddonAbstractClass
from ai_request.ai_core_requests import AiRequest
from lib_core.pattern import APattern
from thread_handling.threading_core import SchedulingClass, ThreadTask, ThreadGroup, ThreadHandler

import json
from dataclasses import dataclass


@dataclass
class Option:
    id: str
    answer: str
    next_node: "Node | Leaf"
    parent: "Node"


@dataclass
class Node:
    id: str
    question: str
    answers: list[Option]
    parent: "Node | None" = None


@dataclass
class Leaf:
    id: str
    pattern_name: str
    pattern: APattern
    parent: "Node | None" = None


class Tree:

    def __init__(self):
        self.root: Node | Leaf | None = None
        self.id_map: dict[int, int] = {}
        self.load("hanfor/ai_addons/pattern_prediction/pattern_tree_first_test.json")

    def load(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        self.id_map[0] = 0
        self.root = self._parse_node(data["root"], 0)

    def _parse_node(self, data: dict, depth: int) -> Node | Leaf:
        self.id_map.setdefault(depth, 0)
        node_id = f"_D-{hex(depth)}_W-{hex(self.id_map[depth])}"

        if "pattern" in data:
            self.id_map[depth] += 1
            patterns = APattern().get_patterns()
            pattern = APattern().get_patterns()[data["pattern"]] if data["pattern"] in patterns.keys() else APattern()
            return Leaf(id="p" + node_id, pattern_name=data["pattern"], pattern=pattern)

        node = Node(id="q" + node_id, question=data["question"], answers=[])
        self.id_map[depth] += 1
        for ans in data.get("answers", []):
            next_node = self._parse_node(ans["next"], depth + 1)
            option = Option(
                id=f"a{node_id}_{ans['answer'].replace(' ', '_')}",
                answer=ans["answer"],
                next_node=next_node,
                parent=node,
            )
            next_node.parent = node
            node.answers.append(option)
        return node

    def to_dict(self, node: "Node | Leaf | None" = None) -> dict:

        if node is None:
            node = self.root

        if isinstance(node, Leaf):
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
    pattern: APattern
    final_node: "Leaf | None" = None


class PatternPrediction(AiAddonAbstractClass):
    required_dependencies = ["thread_handler", "ai_request", "socketio"]

    def __init__(self, thread_handler: ThreadHandler, ai_request: AiRequest, socketio: SocketIO):
        self.prediction_tree = Tree()
        self.thread_handler = thread_handler
        self.ai_request = ai_request
        self.socketio = socketio
        self.requirement_data: dict[str, PatternPredictedRequirement] = {}
        self.socketio_data: dict[str, list[str]] = {}

    @property
    def addon_name(self) -> str:
        return "Pattern Prediction"

    @property
    def addon_description(self) -> str:
        return "Using a decision tree, a requirement can be assigned to a pattern with the help of an AI."

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

    def set_sid_for_req(self, req, sid):
        if req not in self.socketio_data:
            self.socketio_data[req] = []
        self.socketio_data[req].append(sid)

    def clear_sid_for_req(self, req, sid):
        if req in self.socketio_data:
            self.socketio_data[req].remove(sid)
            if not self.socketio_data[req]:
                self.socketio_data.pop(req)

    def update_trace_frontend(self, req_id: str):
        if req_id not in self.requirement_data:
            return

        pattern_data = self.requirement_data[req_id]

        steps = [
            {"nodeId": step["nodeId"], "answer": step["chosen"], "confidences": step["scores"]}
            for step in pattern_data.trace
        ]

        if isinstance(pattern_data.final_node, Leaf):
            steps.append({"nodeId": pattern_data.final_node.id, "answer": None, "confidences": {}})

        payload = {
            "trace": {
                "id": req_id,
                "desc": pattern_data.description,
                "pattern": pattern_data.pattern.get_text(),
                "steps": steps,
            }
        }

        for sid in self.socketio_data.get(req_id, []):
            send_ai_update(payload, self.socketio, sid)

    def predict_pattern_for_requirement(self, req_id: str, req_desc: str, stop_event: Event):
        node = self.prediction_tree.root
        trace = []

        while isinstance(node, Node):
            if stop_event.is_set():
                self.requirement_data[req_id] = PatternPredictedRequirement(req_id, req_desc, trace, APattern(), None)
                self.update_trace_frontend(req_id)
                return

            options = "\n".join(f"{o.answer}" for o in node.answers)

            trace_context = ""
            if trace:
                trace_context = "Decisions made so far:\n"
                trace_context += "\n".join(f"  - {t['question']} → {t['chosen']}" for t in trace)
                trace_context += "\n\n"

            query = (
                f"Requirement: {req_desc}\n\n"
                f"{trace_context}"
                f"Current question: {node.question}\n"
                f"Options:\n{options}\n\n"
                "Respond ONLY with lines in the exact format:\n"
                "<answer>:<score>\n\n"
                "Rules:\n"
                "- One line per answer option.\n"
                "- Score must be a number between 0 and 1.\n"
                "- No explanations.\n"
                "- No additional text.\n"
                "- Output ONLY the answer lines.\n\n"
                "Example:\n"
                "Yes:0.7\n"
                "No:0.3\n"
            )

            answer_options = [o.answer for o in node.answers]

            task_results = [self.ai_request.ask_ai(query, None, SchedulingClass.CALLER_DEPTH_2) for _ in range(5)]

            result = {a: 0 for a in answer_options}

            for task_result in task_results:

                if stop_event.is_set():
                    self.requirement_data[req_id] = PatternPredictedRequirement(
                        req_id, req_desc, trace, APattern(), None
                    )
                    self.update_trace_frontend(req_id)
                    return

                ai_response = task_result.result()[0]
                if not ai_response:
                    continue
                for line in ai_response.splitlines():
                    if ":" not in line:
                        continue
                    try:
                        ai_answer, score = line.split(":", 1)
                        ai_answer = ai_answer.strip()
                        score = float(score.replace(",", "."))
                    except:
                        logging.warning("Couldn't parse AI response:" + task_result.result()[0])
                        continue

                    if ai_answer in answer_options:
                        result[ai_answer] += score

            for k in result:
                result[k] /= len(task_results)

            best_key = max(result, key=result.get)
            trace.append({"nodeId": node.id, "question": node.question, "scores": result.copy(), "chosen": best_key})

            self.requirement_data[req_id] = PatternPredictedRequirement(req_id, req_desc, trace, APattern(), None)
            self.update_trace_frontend(req_id)

            for answer in node.answers:
                if answer.answer == best_key:
                    node = answer.next_node
                    break

        self.requirement_data[req_id] = PatternPredictedRequirement(req_id, req_desc, trace, node.pattern, node)
        self.update_trace_frontend(req_id)
