from unittest import TestCase

from lark import Lark
from pysmt.shortcuts import Int

from simulator.counter_trace import CounterTraceTransformer
from simulator.phase_event_automaton import build_automaton
from tests.test_simulator.test_counter_trace import testcases

parser = Lark.open('../../simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace', parser='lalr')


class TestPhaseEventAutomaton(TestCase):
    def test_simulate(self):
        expressions, ct_str, _ = testcases['response_delay_globally']
        expressions['T'] = Int(5)
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        pea = build_automaton(ct)
        #simulator = Simulator(ct, pea)
        #simulator.simulate()