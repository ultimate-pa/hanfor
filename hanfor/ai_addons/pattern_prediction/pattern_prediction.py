import json
import logging
from dataclasses import dataclass
from threading import Event

from ai_request.ai_core_requests import AiRequest
from thread_handling.threading_core import SchedulingClass, ThreadTask, ThreadGroup, ThreadHandler


@dataclass
class Option:
    answer: str
    next_node: "Node | str"


@dataclass
class Node:
    question: str
    answers: list[Option]


class Tree:
    def __init__(self):
        self.root: Node | None = None
        self.load("hanfor/ai_addons/pattern_prediction/pattern_tree.json")

    def load(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.root = self._parse_node(data["root"])

    def _parse_node(self, data: dict) -> "Node | str":
        if "pattern" in data:
            return data["pattern"]

        answers = []
        for opt in data["answers"]:
            answers.append(
                Option(
                    opt["answer"],
                    self._parse_node(opt["next"]),
                )
            )
        node = Node(data["question"], answers)
        return node

    def print(self, node: "Node | str" = None, prefix: str = "", is_last: bool = True) -> None:
        if node is None:
            node = self.root

        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        if isinstance(node, str):
            logging.info(prefix + connector + f"★ {node}")
            return

        logging.info(prefix + connector + node.question)

        for i, option in enumerate(node.answers):
            is_last_option = i == len(node.answers) - 1
            option_connector = "└─ " if is_last_option else "├─ "
            logging.info(prefix + extension + option_connector + f"[{option.answer}]")
            child_prefix = prefix + extension + ("    " if is_last_option else "│   ")
            self.print(option.next_node, child_prefix, True)


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
