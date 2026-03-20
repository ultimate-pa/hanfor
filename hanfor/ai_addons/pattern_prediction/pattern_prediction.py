import json
import logging
from dataclasses import dataclass

from hanfor_flask import current_app
from ressources.queryapi import Query


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
        self.load("./pattern_tree.json")

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

    def __init__(self):
        self.prediction_tree = Tree()

    def predict_pattern_for_requirement(self, req_desc=str):
        node = self.prediction_tree.root

        while isinstance(node, Node):
            options = "\n".join(f"{i+1}. {o.answer}" for i, o in enumerate(node.answers))
            query = (
                f"Requirement: {req_desc}\n"
                f"Question: {node.question}\n"
                f"Options:\n{options}\n\n"
                f"Only answer with the number of the best matching option."
            )
            print(query)
            # response = current_app.ai_request.ask_ai(query)
            # idx = int(response.strip()) - 1
            node = node.answers[1].next_node

        return node


if __name__ == "__main__":
    pattern_predict = PatternPrediction()
    pattern_predict.predict_pattern_for_requirement("Test Requirement")
