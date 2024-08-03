import logging
from io import StringIO
from unittest import TestCase

from parameterized import parameterized
from pysmt.shortcuts import Real, Symbol, Int, Equals, Implies, LT, GT, Plus, Or, And
from pysmt.typing import REAL, INT, BOOL

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.utils import get_countertrace_parser
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from reqtransformer import Requirement, Formalization
from tests.test_req_simulator import test_counter_trace

'''Warning: these test cases don't actually test accuracy of detected constraints in typical scenarios in the simulator!

For the test cases, (currently) a user input value must be given for each tested time point, so these end up being the 
constraints.

Also, it is (currently) not possible to test requirements which comprise multiple countertraces.

For cases testing functionality of constraint propagation, etc. see project report.
'''

testcases = [
    ([
        ['universality_globally',
         {'R': Implies((Equals(Symbol('var2', REAL), Real(2.0))), LT(Symbol('var3', INT),
                                                                     Plus(Symbol('var1', INT), Int(2))))}],

        ['universality_globally',
         {'R': Implies((Equals(Plus(Symbol('var1', INT), Int(1)), Int(3))),
                       Equals(Symbol('var2', REAL), Real(2.0)))}],

        ['universality_globally',
         {'R': Or(Symbol('constraint1', BOOL), And(Symbol('constraint1', BOOL),
                                                   Symbol('constraint2', BOOL)))}],
     ],
     """{
        "head": {
            "duration": 3,
            "times": [0.0, 1.0, 2.0]
        },
        "data": {
            "constraint1": {
                "type": "Bool",
                "values": [true, true, true]
            },
            "constraint2": {
                "type": "Bool",
                "values": [true, true, true]
            },
            "var1": {
                "type": "Int",
                "values": [6, 3, 3]
            },
            "var2": {
                "type": "Real",
                "values": [3.0, 3.0, 3.0]
            },
            "var3": {
                "type": "Int",
                "values": [8, 5, 5]
            },
            "var4": {
                "type": "Real",
                "values": [0.0, 8.0, 7.0]
            }
        }
     }"""),

    ([
        ['edge_response_bound_u1_globally',
         {'R': Equals(Symbol('var5', REAL), Real(2.0)),
          'T': Real(1.0),
          'S': Equals(Symbol('var6', REAL), Real(4.0))}],
     ],
     """{
        "head": {
            "duration": 3,
            "times": [0.0, 1.0, 2.0]
        },
        "data": {
            "var5": {
                "type": "Real",
                "values": [2.0, 0.0, 0.0]
            },
            "var6": {
                "type": "Real",
                "values": [0.0, 4.0, 4.0]
            }
        }
     }"""),

    ([
        ['duration_bound_u_globally',
         {'R': GT(Symbol('var7', INT), Int(1)),
          'T': Real(2.0)}],
     ],
     """{
        "head": {
            "duration": 2,
            "times": [0.0, 1.0]
        },
        "data": {
            "var7": {
                "type": "Int",
                "values": [0, 0]
            }
        }
     }"""),

    ([
        ['initialization_globally',
         {'R': And(Equals(Symbol('var8', REAL), Real(2.0)), Equals(Symbol('var8', REAL), Real(3.0)))}],
     ],
     """{
        "head": {
            "duration": 0,
            "times": [0.0]
        },
        "data": {
            "var8": {
                "type": "Real",
                "values": [2.0]
            }
        }
     }"""),

    ([
         ['initialization_globally',
          {'R': Equals(Symbol('var9', REAL), Real(2.0))}],

         ['initialization_globally',
          {'R': Equals(Symbol('var9', REAL), Real(3.0))}],
     ],
     """{
        "head": {
            "duration": 0,
            "times": [0.0]
        },
        "data": {
            "var9": {
                "type": "Real",
                "values": [2.0]
            }
        }
     }"""),
]


class TestVariableConstraints(TestCase):

    @parameterized.expand(testcases)
    def test_variable_constraints(self, formalizations: list, yaml_str: str):

        peas = []
        for formalization in formalizations:
            pattern_name, expressions = formalization
            _, ct_str, _  = test_counter_trace.testcases[pattern_name]
            ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
            pea = build_automaton(ct)

            # TODO: Fix this hack.
            pea.requirement = Requirement(id='0', description='', type_in_csv='', csv_row={}, pos_in_csv=0)
            pea.formalization = Formalization(id=0)
            pea.countertrace_id = 0
            peas.append(pea)

        scenario = Scenario.from_json_string(yaml_str)
        simulator = Simulator(peas, scenario, test=True)


        for i in range(len(scenario.times) - 1):
            actual = simulator.variable_constraints()

            simulator.check_sat()

            if len(formalizations) == 3 and float(i) == 0.0:
                print("tested case 1_0")
                self.assertIn("constraint1 must be constraint1 at time 0.0", actual,
                              msg="Constraints weren't detected as expected for constraint1")
                self.assertIn("constraint2 must be constraint2 at time 0.0", actual,
                              msg="Constraints weren't detected as expected for constraint2")
                self.assertIn("var1 must be (var1 = 6) at time 0.0", actual,
                              msg="Constraints weren't detected as expected for var1")
                self.assertIn("var2 must be (var2 = 3.0) at time 0.0", actual,
                              msg="Constraints weren't detected as expected for var2")
                self.assertIn("var3 must be (var3 = 8) at time 0.0", actual,
                              msg="Constraints weren't detected as expected for var3")

            elif len(formalizations) == 3 and float(i) == 1.0:
                print("tested case 1_1")
                self.assertIn("constraint1 must be constraint1 at time 1.0", actual,
                              msg="Constraints weren't detected as expected for constraint1")
                self.assertIn("constraint2 must be constraint2 at time 1.0", actual,
                              msg="Constraints weren't detected as expected for constraint2")
                self.assertIn("var1 must be (var1 = 3) at time 1.0", actual,
                              msg="Constraints weren't detected as expected for var1")
                self.assertIn("var2 must be (var2 = 3.0) at time 1.0", actual,
                              msg="Constraints weren't detected as expected for var2")
                self.assertIn("var3 must be (var3 = 5) at time 1.0", actual,
                              msg="Constraints weren't detected as expected for var3")

            elif len(formalizations) == 3 and float(i) == 2.0:
                print("tested case 1_2")
                self.assertIn("constraint1 must be constraint1 at time 2.0", actual,
                              msg="Constraints weren't detected as expected for constraint1")
                self.assertIn("constraint2 must be constraint2 at time 2.0", actual,
                              msg="Constraints weren't detected as expected for constraint2")
                self.assertIn("var1 must be (var1 = 3) at time 2.0", actual,
                              msg="Constraints weren't detected as expected for var1")
                self.assertIn("var2 must be (var2 = 3.0) at time 2.0", actual,
                              msg="Constraints weren't detected as expected for var2")
                self.assertIn("var3 must be (var3 = 5) at time 2.0", actual,
                              msg="Constraints weren't detected as expected for var3")

            elif 'edge_response_bound_u1_globally' in formalizations[-1] and float(i) == 0.0:
                print("tested case 2_0")
                self.assertIn("var5 must be (var5 = 2.0) at time 0.0", actual,
                              msg="Constraints weren't detected as expected for var5")
                self.assertIn("var6 must be (var6 = 0.0) at time 0.0", actual,
                              msg="Constraints weren't detected as expected for var6")

            elif 'edge_response_bound_u1_globally' in formalizations[-1] and float(i) == 1.0:
                print("tested case 2_1")
                self.assertIn("var5 must be (var5 = 0.0) at time 1.0", actual,
                              msg="Constraints weren't detected as expected for var5")
                self.assertIn("var6 must be (var6 = 4.0) at time 1.0", actual,
                              msg="Constraints weren't detected as expected for var6")

            elif 'edge_response_bound_u1_globally' in formalizations[-1] and float(i) == 2.0:
                print("tested case 2_2")
                self.assertIn("var5 must be (var5 = 0.0) at time 2.0", actual,
                              msg="Constraints weren't detected as expected for var5")
                self.assertIn("var6 must be (var6 = 4.0) at time 2.0", actual,
                              msg="Constraints weren't detected as expected for var6")

            elif 'duration_bound_u_globally' in formalizations[-1] and float(i) == 0.0:
                print("tested case 3")
                # TODO: here, actual is empty. Why?
                self.assertIn("var7 must be (var7 = 0) at time 0.0", actual,
                              msg="Constraints weren't detected as expected for var7")

            elif 'duration_bound_u_globally' in formalizations[-1] and float(i) == 1.0:
                print("tested case 3")
                # TODO: here, actual is empty. Why?
                self.assertIn("var7 must be (var7 = 0) at time 1.0", actual,
                              msg="Constraints weren't detected as expected for var7")

            elif len(formalizations) == 2 and float(i) == 0.0:
                print("tested case 5")
                self.assertIn("var9 has contradicting constraints", actual,
                              msg="Constraints weren't detected as expected for var9")
                return None

            elif not simulator.check_sat():
                print("tested case 4")
                self.assertIn("There is inconsistency in some requirement(s).", actual,
                              msg="The inconsistent requirement wasn't detected.")
                return None

            if float(i) == len(scenario.times) - 1:
                break

            simulator.step_next(0)
