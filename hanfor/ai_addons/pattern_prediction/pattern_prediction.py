import logging
import random
from threading import Event

from ai_request.ai_core_requests import AiRequest
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
    pattern: str
    parent: "Node | None" = None


class Tree:

    def __init__(self):
        self.root: Node | Leaf | None = None
        self.id_map: dict[int, int] = {}
        self.load("hanfor/ai_addons/pattern_prediction/pattern_tree.json")

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
            return Leaf(id="p" + node_id, pattern=data["pattern"])

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
            return {"id": node.id, "pattern": node.pattern}

        return {
            "id": node.id,
            "question": node.question,
            "answers": [
                {"answer": opt.answer, "id": opt.id, "next": self.to_dict(opt.next_node)} for opt in node.answers
            ],
        }


class PatternPrediction:

    def __init__(self, thread_handler: ThreadHandler, ai_request: AiRequest):
        self.prediction_tree = Tree()
        self.thread_handler = thread_handler
        self.ai_request = ai_request

    def predict_patterns_for_all_requirements(self, requirements):
        for req_id, requirement in requirements.items():
            task = ThreadTask(
                self.predict_pattern_for_requirement,
                SchedulingClass.CALLER_DEPTH_1,
                ThreadGroup.PATTERN_PREDICTION,
                None,
                self.print_pattern,
                (req_id, requirement.description),
                {},
            )
            self.thread_handler.submit(task)

    def print_pattern(self, result):
        print(result)

    def predict_pattern_for_requirement_mock(self, req_id: str, req_desc: str, stop_event: Event):
        node = self.prediction_tree.root
        trace = []

        while isinstance(node, Node):
            if random.randint(0, 5) == 3:
                break
            answer_options = [o.answer for o in node.answers]

            raw_scores = [random.random() for _ in answer_options]
            total = sum(raw_scores)
            result = {a: round(s / total, 3) for a, s in zip(answer_options, raw_scores)}

            best_key = max(result, key=result.get)

            trace.append({"nodeId": node.id, "question": node.question, "scores": result.copy(), "chosen": best_key})

            for answer in node.answers:
                if answer.answer == best_key:
                    node = answer.next_node
                    break

        return req_id, node, trace

    def predict_pattern_for_requirement(self, req_id: str, req_desc: str, stop_event: Event):
        node = self.prediction_tree.root
        trace = []

        while isinstance(node, Node):
            options = "\n".join(f"{o.answer}" for o in node.answers)

            query = (
                f"Requirement: {req_desc}\n"
                f"Question: {node.question}\n"
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
                "No:0.3"
            )

            answer_options = [o.answer for o in node.answers]

            task_results = [self.ai_request.ask_ai(query, None, SchedulingClass.CALLER_DEPTH_2) for _ in range(5)]

            result = {a: 0 for a in answer_options}

            for task_result in task_results:
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

            trace.append({"question": node.question, "scores": result.copy(), "chosen": best_key})

            for answer in node.answers:
                if answer.answer == best_key:
                    node = answer.next_node
                    break

        return req_id, node, trace
