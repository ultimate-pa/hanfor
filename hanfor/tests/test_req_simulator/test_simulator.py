from unittest import TestCase

from parameterized import parameterized
from pysmt.fnode import FNode
from pysmt.shortcuts import Real, Symbol, GE, Int, Equals
from pysmt.typing import REAL, INT

from lib_pea.countertrace import CountertraceTransformer
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from lib_pea.utils import get_countertrace_parser
from reqtransformer import Requirement, Formalization
from tests.test_req_simulator import test_counter_trace
from lib_pea import build_automaton

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
     {'R': Equals(Symbol('x', INT), Int(5)), 'S': GE(Symbol('y', REAL), Real(3.14)), 'T': Real(5.0)},
     """{
        "head": {
            "duration": 11,
            "times": [0.0, 5.0, 7.0, 10.0]
        },
        "data": {
            "x": {
                "type": "Int",
                "values": [5, 5, 5, 0]
            },
            "y": {
                "type": "Real",
                "values": [0.0, 3.14, 0.0, 0.0]
            }
        }
     }"""),
]


class TestSimulator(TestCase):

    @parameterized.expand(testcases)
    def test_simulator(self, pattern_name: str, expressions: dict[str, FNode], yaml_str: str):
        _, ct_str, _ = test_counter_trace.testcases[pattern_name]
        #expressions['T'] = Real(5)

        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
        pea = build_automaton(ct)

        # TODO: Fix this hack.
        pea.requirement = Requirement(id='0', description='', type_in_csv='', csv_row={}, pos_in_csv=0)
        pea.formalization = Formalization(id=0)
        pea.countertrace_id = 0

        scenario = Scenario.from_json_string(yaml_str)
        simulator = Simulator([pea], scenario, test=True)

        actual = False
        for i in range(len(scenario.times)):
            actual = False

            if not simulator.check_sat():
                break

            #if len(simulator.sat_results) != 1:
            #    break

            if i == len(scenario.times) - 1:
                actual = True
                break

            simulator.step_next(0)



        self.assertEqual(True, actual, msg="Error while simulating scenario.")
