from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, Real, Bool, Int, TRUE
from pysmt.typing import BOOL, INT, REAL

from req_simulator.utils import load_json_or_yaml_file, parse_json_or_yaml_string, save_json_file, dump_json_string


@dataclass
class Configuration:
    time: float
    variables: dict[FNode, FNode]


@dataclass
class Scenario:
    times: list[float]
    variables: dict[FNode, list[FNode]]
    types: dict[FNode, BOOL | INT | REAL] = field(init=False)

    def __post_init__(self):
        self.types = {k: k.symbol_type() for k in self.variables}

    def remove_variable(self, variable: FNode) -> None:
        self.variables.pop(variable)
        self.types.pop(variable)

        if len(self.variables) <= 0:
            self.times.clear()

    def remove_variables(self, variables: list[FNode]) -> None:
        for v in variables:
            self.remove_variable(v)

    def difference(self, variables: list[FNode]) -> list[FNode]:
        return [k for k in self.variables if k not in variables]

    def get_configuration(self, time: float) -> Configuration:
        result = None

        for i in range(len(self.times) - 1):
            if self.times[i] <= time < self.times[i + 1]:
                result = Configuration(
                    time=self.times[i + 1], variables={k: v[i + 1] for k, v in self.variables.items()}
                )

        return result

    @staticmethod
    def from_object(object: Any) -> Scenario | None:
        if object is None:
            return None

        var_map = {
            "Bool": lambda v: Symbol(v, BOOL),
            "Int": lambda v: Symbol(v, INT),
            "Real": lambda v: Symbol(v, REAL),
        }

        const_map = {"Bool": lambda v: Bool(v == 1), "Int": lambda v: Int(v), "Real": lambda v: Real(v)}

        scenario = Scenario(
            object["head"]["times"] + [object["head"]["duration"]],
            {
                var_map[v["type"]](k): [None] + [const_map[v["type"]](vv) for vv in v["values"]]
                for k, v in object["data"].items()
            },
        )

        return scenario

    @staticmethod
    def to_object(scenario: Scenario) -> Any:
        if scenario is None:
            return None

        const_map = {
            BOOL: lambda v: v == TRUE(),
            INT: lambda v: int(str(v)),
            REAL: lambda v: float(Fraction(str(v))),
        }

        head = {}
        head["duration"] = scenario.times[-1]
        head["times"] = [v for v in scenario.times[:-1]]

        data = defaultdict(dict)
        for k, v in scenario.variables.items():
            data[str(k)]["type"] = str(k.get_type())
            data[str(k)]["values"] = [const_map[scenario.types[k]](v_) for v_ in v[1:]]

        return {"head": head, "data": data}

    @staticmethod
    def from_json_string(str: str) -> Scenario:
        return Scenario.from_object(parse_json_or_yaml_string(str))

    @staticmethod
    def to_json_string(scenario: Scenario) -> str:
        return dump_json_string(Scenario.to_object(scenario))

    @staticmethod
    def load_from_file(path: str) -> Scenario:
        return Scenario.from_object(load_json_or_yaml_file(path))

    @staticmethod
    def save_to_file(scenario: Scenario, path: str, sort_keys: bool = False) -> None:
        save_json_file(Scenario.to_object(scenario), path)


def main():
    scenario = Scenario(
        [0.0, 1.0, 2.0, 3.0],
        {
            Symbol("A"): [None, TRUE(), TRUE(), TRUE()],
            Symbol("B", INT): [None, Int(5), Int(10), Int(0)],
            Symbol("C", REAL): [None, Real(5.0), Real(10.0), Real(0.0)],
        },
    )

    Scenario.save_to_file(scenario, "/home/ubuntu/Desktop/test_scenario.json")
    scenario = Scenario.load_from_file("/home/ubuntu/Desktop/test_scenario.json")


if __name__ == "__main__":
    main()
