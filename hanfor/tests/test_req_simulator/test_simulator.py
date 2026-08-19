from unittest import TestCase

from parameterized import parameterized
from pysmt.environment import Environment

from lib_core.data import Requirement, Formalization
from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import PeaBuilder
from lib_pea.utils import get_countertrace_parser
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from tests.test_req_simulator import test_counter_trace

testcases = [
    (
        "false",
        lambda smt_env, fmgr, tmgr: (
            test_counter_trace.pattern_cases(smt_env, "false")[0],
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
     }""",
        ),
    ),
    (
        "absence_globally",
        lambda smt_env, fmgr, tmgr: (
            test_counter_trace.pattern_cases(smt_env, "absence_globally")[0],
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
     }""",
        ),
    ),
    (
        "absence_before",
        lambda smt_env, fmgr, tmgr: (
            test_counter_trace.pattern_cases(smt_env, "absence_before")[0],
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
     }""",
        ),
    ),
    (
        "response_delay_globally",
        lambda smt_env, fmgr, tmgr: (
            {
                "R": fmgr.Equals(fmgr.Symbol("x", tmgr.INT()), fmgr.Int(5)),
                "S": fmgr.GE(fmgr.Symbol("y", tmgr.REAL()), fmgr.Real(3.14)),
                "T": fmgr.Real(5.0),
            },
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
     }""",
        ),
    ),
]


class TestSimulator(TestCase):

    @parameterized.expand(testcases)
    def test_simulator(self, pattern_name, tgen):
        smt_env: Environment = Environment()
        expressions, yaml_str = tgen(smt_env, smt_env.formula_manager, smt_env.type_manager)
        _, ct_str, _ = test_counter_trace.pattern_cases(smt_env, pattern_name)

        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))
        pea = PeaBuilder(smt_env).build_automaton(ct)

        # TODO: Fix this hack.
        pea.requirement = Requirement(rid="0", description="", type_in_csv="", csv_row={}, pos_in_csv=0)
        pea.formalization = Formalization(fid=0)
        pea.countertrace_id = 0

        scenario = Scenario(smt_env).from_json_string(yaml_str)
        simulator = Simulator(smt_env, [pea], scenario, test=True)

        actual = False
        for i in range(len(scenario.times)):
            actual = False

            if not simulator.check_sat():
                break

            if i == len(scenario.times) - 1:
                actual = True
                break

            simulator.step_next(0)

        self.assertEqual(True, actual, msg="Error while simulating scenario.")
