from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from pysmt.environment import Environment
from pysmt.fnode import FNode

from req_simulator.utils import load_json_or_yaml_file, parse_json_or_yaml_string, save_json_file, dump_json_string


@dataclass
class Configuration:
    time: float
    variables: dict[FNode, FNode | None]


class Scenario:

    def __init__(self, smt_env: Environment, times=None, variables=None):
        self.__smt_env = smt_env
        self.__tmgr = self.__smt_env.type_manager
        self.__fmgr = self.__smt_env.formula_manager
        self.times: list[float] = times if times else []
        self.variables: dict[FNode, list[FNode | None]] = variables if variables else {}
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

    def get_configuration(self, time: float) -> Configuration | None:
        result = None

        for i in range(len(self.times) - 1):
            if self.times[i] <= time < self.times[i + 1]:
                result = Configuration(
                    time=self.times[i + 1], variables={k: v[i + 1] for k, v in self.variables.items()}
                )

        return result

    def from_object(self, object: Any) -> Scenario | None:
        if object is None:
            return None

        var_map = {
            "Bool": lambda v: self.__fmgr.Symbol(v, self.__tmgr.BOOL()),
            "Int": lambda v: self.__fmgr.Symbol(v, self.__tmgr.INT()),
            "Real": lambda v: self.__fmgr.Symbol(v, self.__tmgr.REAL()),
        }

        const_map = {
            "Bool": lambda v: self.__fmgr.Bool(v == 1),
            "Int": lambda v: self.__fmgr.Int(v),
            "Real": lambda v: self.__fmgr.Real(v),
        }

        self.times = object["head"]["times"] + [object["head"]["duration"]]
        self.variables = {
            var_map[v["type"]](k): [None] + [const_map[v["type"]](vv) for vv in v["values"]]
            for k, v in object["data"].items()
        }
        self.types = {k: k.symbol_type() for k in self.variables}
        return self

    def to_object(self) -> Any:
        const_map = {
            self.__tmgr.BOOL(): lambda v: v == self.__fmgr.TRUE(),
            self.__tmgr.INT(): lambda v: int(str(v)),
            self.__tmgr.REAL(): lambda v: float(Fraction(str(v))),
        }

        head = dict()
        head["duration"] = self.times[-1]
        head["times"] = [v for v in self.times[:-1]]

        data = defaultdict(dict[str, Any])
        for k, v in self.variables.items():
            data[str(k)]["type"] = str(k.get_type())
            data[str(k)]["values"] = [const_map[self.types[k]](v_) for v_ in v[1:]]

        return {"head": head, "data": data}

    def from_json_string(self, str: str) -> Scenario:
        self.from_object(parse_json_or_yaml_string(str))
        return self

    def to_json_string(self) -> str:
        return dump_json_string(self.to_object())

    def load_from_file(self, path: str) -> Scenario:
        self.from_object(load_json_or_yaml_file(path))
        return self

    def save_to_file(self, path: str, sort_keys: bool = False) -> None:
        save_json_file(self.to_object(), path, sort_keys=sort_keys)
