from unittest import TestCase

from lark import Lark
from parameterized import parameterized
from pysmt.fnode import FNode
from pysmt.shortcuts import Real, Symbol, GE, Int, Equals
from pysmt.typing import REAL, INT

from req_simulator.counter_trace import CounterTraceTransformer
from req_simulator.phase_event_automaton import build_automaton
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from tests.test_req_simulator import test_counter_trace

parser = Lark.open('../../req_simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace',
                   parser='lalr')

testcases = [
    ('false',
     test_counter_trace.testcases['false'].expressions,
     """{
        "head": {
            "duration": 6,
            "types": {"R": "bool"}
        },
        "data": {
            "0": {"R": false},
            "5": {"R": true}
        }
     }""",
     True),

    ('true',
     test_counter_trace.testcases['true'].expressions,
     """{
        "head": {
            "duration": 5,
            "types": {"nonsense_bool": "bool", "nonsense_int": "int"}
        },
        "data": {
            "0": {"nonsense_bool": false, "nonsense_int": 5},
            "2": {"nonsense_int": 3}
        }
     }""",
     False),

    ('true_lower_bound_empty',
     test_counter_trace.testcases['true_lower_bound_empty'].expressions,
     """{
        "head": {
            "duration": 6,
            "types": {"nonsense_bool": "bool", "nonsense_real": "real"}
        },
        "data": {
            "0": {"nonsense_bool": true, "nonsense_real": -1.1},
            "5": {"nonsense_real": 3.2}
        }
     }""",
     False),

    ('absence_globally',
     test_counter_trace.testcases['absence_globally'].expressions,
     """{
        "head": {
            "duration": 6,
            "types": {"R": "bool"}
        },
        "data": {
            "0": {"R": false},
            "5": {"R": false}
        }
     }""",
     True),

    ('absence_globally',
     test_counter_trace.testcases['absence_globally'].expressions,
     """{
        "head": {
            "duration": 6,
            "types": {"R": "bool"}
        },
        "data": {
            "0": {"R": false},
            "5": {"R": true}
        }
     }""",
     False),

    ('absence_before',
     test_counter_trace.testcases['absence_before'].expressions,
     """{
        "head": {
            "duration": 8,
            "types": {"P": "bool", "R": "bool"}
        },
        "data": {
            "0": {"P": false, "R": false},
            "3": {"P": true},
            "7": {"R": true}
        }
     }""",
     True),

    ('absence_before',
     test_counter_trace.testcases['absence_before'].expressions,
     """{
        "head": {
            "duration": 7,
            "types": {"P": "bool", "R": "bool"}
        },
        "data": {
            "0": {"P": false, "R": true},
            "6": {"R": true}
        }
     }""",
     False),

    ('response_delay_globally',
     {'R': Equals(Symbol('x', INT), Int(17)), 'S': GE(Symbol('y', REAL), Real(3.14)), 'T': Symbol('T', REAL)},
     """{
        "head": {
            "duration": 7,
            "types": {"x": "int", "y": "real"}
        },
        "data": {
            "0": {"x": 3, "y": 0},
            "1": {"x": 17, "y": 2.14},
            "5": {"x": 7, "y": 2.14},
            "6": {"x": 7, "y": 3.14}
        }
     }""",
     True),
]


class TestSimulator(TestCase):

    @parameterized.expand(testcases)
    def test_simulator(self, pattern_name: str, expressions: dict[str, FNode], yaml_str: str, expected: bool):
        _, ct_str, _ = test_counter_trace.testcases[pattern_name]
        expressions['T'] = Real(5)

        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        pea = build_automaton(ct)
        scenario = Scenario.parse_from_yaml_or_json_string(yaml_str)
        simulator = Simulator([ct], [pea], scenario)

        actual = False
        for i in range(len(scenario.valuations)):
            actual = False
            transitions = simulator.check_sat()

            if len(transitions) == 0 or len(transitions) > 1:
                break

            if len(transitions) == 1:
                simulator.walk_transitions(transitions[0])
                actual = True

        self.assertEqual(expected, actual, msg="Error while simulating scenario.")
