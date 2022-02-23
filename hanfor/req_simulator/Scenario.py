from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, Real, Bool, Int
from pysmt.typing import BOOL, INT, REAL

from req_simulator.utils import load_yaml_or_json_file, parse_yaml_string, save_json_file


@dataclass
class Scenario:
    variables: set[FNode] = field(default_factory=set)
    values: dict[float, dict[FNode, FNode]] = field(default_factory=dict)
    duration: float = 0.0

    def get_time_index(self, time) -> tuple[int, int]:
        return (list(self.values).index(time) if time in self.values else -1, len(self.values))

    @staticmethod
    def from_object(obj: Any) -> Scenario:
        type_mapping = {
            'bool': BOOL,
            'int': INT,
            'real': REAL
        }

        const_mapping = {
            BOOL: Bool,
            INT: Int,
            REAL: Real
        }

        scenario = Scenario()
        scenario.variables = {Symbol(k, type_mapping[v]) for k, v in obj['head']['types'].items()}
        scenario.duration = obj['head']['duration']

        prev_t = -1.0
        data_sorted = dict(sorted(obj['data'].items()))
        for t, values in data_sorted.items():
            t = float(t)
            scenario.values[t] = dict.fromkeys(scenario.variables, None) if prev_t < 0.0 else scenario.values[
                prev_t].copy()
            prev_t = t

            if values is None:
                continue

            for k, v in values.items():
                variable = Symbol(k, type_mapping[obj['head']['types'][k]])
                value = const_mapping[variable.symbol_type()](v) if v is not None else v
                scenario.values[t][variable] = value

        return scenario

    @staticmethod
    def to_object(scenario: Scenario) -> Any:
        type_mapping = {
            BOOL: 'bool',
            INT: 'int',
            REAL: 'real'
        }

        const_mapping = {
            BOOL: eval,
            INT: int,
            REAL: lambda v: float(Fraction(v))
        }


        head = {'duration': scenario.duration, 'types': {}}
        head['types'] = {v.symbol_name(): type_mapping[v.symbol_type()] for v in scenario.variables}

        data = {}
        for time, value in scenario.values.items():
            data[time] = {str(k): None if v is None else const_mapping[k.symbol_type()](str(v)) for k, v in
                          value.items()}

        return {'head': head, 'data': data}

    @staticmethod
    def parse_from_yaml_string(yaml_str: str) -> Scenario:
        return Scenario.from_object(parse_yaml_string(yaml_str))

    @staticmethod
    def load_from_file(path: str) -> Scenario:
        return Scenario.from_object(load_yaml_or_json_file(path))

    @staticmethod
    def save_to_file(scenario: Scenario, path: str, sort_keys: bool = False) -> None:
        save_json_file(Scenario.to_object(scenario), path)
