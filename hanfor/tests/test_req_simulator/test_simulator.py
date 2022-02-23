from unittest import TestCase

from lark import Lark
from parameterized import parameterized
from pysmt.shortcuts import Real

from req_simulator.Scenario import Scenario
from req_simulator.counter_trace import CounterTraceTransformer
from req_simulator.phase_event_automaton import build_automaton
from req_simulator.simulator import Simulator
from tests.test_req_simulator import test_counter_trace

parser = Lark.open('../../req_simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace',
                   parser='lalr')

testcases = {
    'false_true':
        ('false',
         """
         head:
             duration: 6
             types:
                 R: bool
         data:
             0:
                 R: false
             5:
                 R: true
         """,
         True),

    'true_false':
        ('true',
         """
         head:
             duration: 5
             types:
                 nonsense_bool: bool
                 nonsense_int: int
         data:
             0:
                 nonsense_bool: false
                 nonsense_int: 5
             2:
                 nonsense_int: 3
         """,
         False),

    'true_lower_bound_empty_false':
        ('true_lower_bound_empty',
         """
         head:
             duration: 6
             types:
                 nonsense_bool: bool
                 nonsense_real: real
         data:
             0:
                 nonsense_bool: true
                 nonsense_real: -1.1
             5:
                 nonsense_real: 3.2
         """,
         False),

    'absence_globally_true':
        ('absence_globally',
         """
         head:
             duration: 6
             types:
                 R: bool
         data:
             0:
                 R: false
             5:
                 R: false
         """,
         True),

    'absence_globally_false':
        ('absence_globally',
         """
         head:
             duration: 6
             types:
                 R: bool
         data:
             0:
                 R: false
             5:
                 R: true
         """,
         False),

    'absence_before_true':
        ('absence_before',
         """
         head:
             duration: 8
             types:
                 P: bool
                 R: bool
         data:
             0:
                 P: false
                 R: false
             3:
                 P: true
             7:  
                 R: true
         """,
         True),

    'absence_before_false':
        ('absence_before',
         """
         head:
             duration: 7
             types:
                 P: bool
                 R: bool
         data:
             0:
                 P: false
                 R: true
             6:
                 R: false
         """,
         False),
}


class TestSimulator(TestCase):

    @parameterized.expand(testcases.values())
    def test_simulator(self, pattern_name: str, yaml_str: str, expected: bool):
        expressions, ct_str, _ = test_counter_trace.testcases[pattern_name]
        expressions['T'] = Real(5)

        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        pea = build_automaton(ct)
        scenario = Scenario.parse_from_yaml_string(yaml_str)

        simulator = Simulator([ct], [pea])
        simulator.set_scenario(scenario)

        actual = False
        for i in range(len(scenario.values)):
            transitions = simulator.check_sat()
            assert (len(transitions) <= 1)

            if len(transitions) == 0:
                break

            if len(transitions) == 1:
                simulator.walk_transitions(transitions[0])
                actual = True if i == len(scenario.values) - 1 else False

        self.assertEqual(expected, actual, msg="Error while simulating scenario.")
