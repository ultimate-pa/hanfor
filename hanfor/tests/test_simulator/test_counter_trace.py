from unittest import TestCase

from lark.lark import Lark
from parameterized import parameterized
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol
from pysmt.typing import INT

from simulator.counter_trace import create_counter_trace, CounterTraceTransformer


class TestCounterTrace(TestCase):
    @parameterized.expand([
        ('BndResponsePatternUT', 'GLOBALLY',
         {'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True'),

        ('BndResponsePatternUT', 'BEFORE',
         {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         '⌈(! P)⌉;⌈(((! P) & R) & (! S))⌉;⌈((! P) & (! S))⌉ ∧ ℓ > T;True'),

        ('BndResponsePatternUT', 'AFTER',
         {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True;⌈P⌉;True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True'),

        ('BndResponsePatternUT', 'BETWEEN',
         {'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈(((! Q) & R) & (! S))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;⌈(! Q)⌉;⌈Q⌉;True'),

        ('BndResponsePatternUT', 'AFTER_UNTIL',
         {'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True;⌈P⌉;⌈(! Q)⌉;⌈(((! Q) & R) & (! S))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;True'),
    ])
    def test_bnd_response_pattern_ut(self, pattern: str, scope: str, expressions: dict[str, FNode], expected: str):
        actual = create_counter_trace(scope, pattern, expressions)
        self.assertEqual(expected, str(actual), msg="Error while creating counter trace.")

    @parameterized.expand([
        # BndResponsePatternUT Globally
        ({'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'true;⌈(!S && R)⌉;⌈!S⌉ ∧ ℓ > T;true',
         'True;⌈((! S) & R)⌉;⌈(! S)⌉ ∧ ℓ > T;True'),

        # BndResponsePatternUT BEFORE
        ({'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         '⌈!P⌉;⌈(!P && (!S && R))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true',
         '⌈(! P)⌉;⌈((! P) & ((! S) & R))⌉;⌈((! P) & (! S))⌉ ∧ ℓ > T;True'),

        # BndResponsePatternUT AFTER
        ({'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'true;⌈P⌉;true;⌈(!S && R)⌉;⌈!S⌉ ∧ ℓ > T;true',
         'True;⌈P⌉;True;⌈((! S) & R)⌉;⌈(! S)⌉ ∧ ℓ > T;True'),

        # BndResponsePatternUT BETWEEN
        ({'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (!S && R))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true',
         'True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & ((! S) & R))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;⌈(! Q)⌉;⌈Q⌉;True'),

        # BndResponsePatternUT AFTER_UNTIL
        ({'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'true;⌈P⌉;⌈!Q⌉;⌈(!Q && (!S && R))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true',
         'True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & ((! S) & R))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;True'),
    ])
    def test_counter_trace_transformer(self, expressions: dict[str, FNode], counter_trace: str, expected: str):
        parser = Lark.open("../../simulator/counter_trace_grammar.lark", rel_to=__file__, start='counter_trace', parser='lalr')
        lark_tree = parser.parse(counter_trace)
        actual = CounterTraceTransformer(expressions).transform(lark_tree)
        self.assertEqual(expected, str(actual), msg="Error while parsing counter trace.")
        # Image.open(BytesIO(pydot__tree_to_graph(lark_tree).create_png())).show()