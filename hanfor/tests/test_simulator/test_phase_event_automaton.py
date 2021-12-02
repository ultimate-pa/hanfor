from unittest import TestCase

from lark.lark import Lark
from pysmt.shortcuts import Symbol
from pysmt.typing import INT

from simulator.counter_trace import CounterTraceTransformer
from simulator.phase_event_automaton import build_automaton


class TestCounterTrace(TestCase):
    def test_bnd_response_pattern_ut(self):
        ct_str = 'true;⌈(!S && R)⌉;⌈!S⌉ ∧ ℓ > T;true'
        expressions = {'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)}

        parser = Lark.open("../../simulator/counter_trace_grammar.lark", rel_to=__file__, start='counter_trace',
                           parser='lalr')
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        init_locations, locations = build_automaton(ct)
        print("there we go")
