from unittest import TestCase

from parameterized import parameterized
from pysmt.fnode import FNode
from pysmt.shortcuts import Real, Symbol, GE, Int, Equals
from pysmt.typing import REAL, INT

from req_simulator.countertrace import CountertraceTransformer
from req_simulator.phase_event_automaton import build_automaton
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from req_simulator.utils import get_countertrace_parser
from tests.test_req_simulator import test_counter_trace

testcases = [
    ('false',
     test_counter_trace.testcases['false'].expressions,
     """{
        "head": {
            "duration": 6,
            "times": [0.0, 5.0]
        },
        "data": {
            "R": {
                "type": "Bool",
                "values": [false, true]
            }
        }
     }"""),

    ('absence_globally',
     test_counter_trace.testcases['absence_globally'].expressions,
     """{
        "head": {
            "duration": 6,
            "times": [0.0, 5.0]
        },
        "data": {
            "R": {
                "type": "Bool",
                "values": [false, false]
            }
        }
     }"""),

    ('absence_before',
     test_counter_trace.testcases['absence_before'].expressions,
     """{
        "head": {
            "duration": 8,
            "times": [0.0, 3.0, 7.0]
        },
        "data": {
            "P": {
                "type": "Bool",
                "values": [false, true, false]
            },
            "R": {
                "type": "Bool",
                "values": [false, false, true]
            }
        }
     }"""),

    ('response_delay_globally',
     {'R': Equals(Symbol('x', INT), Int(17)), 'S': GE(Symbol('y', REAL), Real(3.14)), 'T': Symbol('T', REAL)},
     """{
        "head": {
            "duration": 7,
            "times": [0.0, 1.0, 5.0, 6.0]
        },
        "data": {
            "x": {
                "type": "Int",
                "values": [3, 17, 7, 7]
            },
            "y": {
                "type": "Real",
                "values": [0.0, 2.14, 2.14, 3.14]
            }
        }
     }"""),
]


class TestSimulator(TestCase):

    @parameterized.expand(testcases)
    def test_simulator(self, pattern_name: str, expressions: dict[str, FNode], yaml_str: str):
        _, ct_str, _ = test_counter_trace.testcases[pattern_name]
        expressions['T'] = Real(5)

        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
        pea = build_automaton(ct)
        scenario = Scenario.from_json_string(yaml_str)
        simulator = Simulator([pea], scenario, test=True)

        actual = False
        for i in range(len(scenario.times)):
            actual = False

            if not simulator.check_sat():
                break

            if len(simulator.sat_results) != 1:
                break

            if i == len(scenario.times) - 1:
                actual = True



        self.assertEqual(True, actual, msg="Error while simulating scenario.")
