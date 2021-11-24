from unittest import TestCase

from parameterized import parameterized
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol
from pysmt.typing import INT

from simulator.counter_trace import create_counter_trace


class TestCounterTrace(TestCase):

    @parameterized.expand([
        ('BndResponsePatternUT', 'GLOBALLY',
         {'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True ; ⌈(R & (! S))⌉ ; ⌈(! S)⌉ ∧ ℓ > T ; True'),

        ('BndResponsePatternUT', 'BEFORE',
         {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         '⌈(! P)⌉ ; ⌈(((! P) & R) & (! S))⌉ ; ⌈((! P) & (! S))⌉ ∧ ℓ > T ; True'),

        ('BndResponsePatternUT', 'AFTER',
         {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True ; ⌈P⌉ ; True ; ⌈(R & (! S))⌉ ; ⌈(! S)⌉ ∧ ℓ > T ; True'),

        ('BndResponsePatternUT', 'AFTER_UNTIL',
         {'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True ; ⌈P⌉ ; ⌈(! Q)⌉ ; ⌈(((! Q) & R) & (! S))⌉ ; ⌈((! Q) & (! S))⌉ ∧ ℓ > T ; True'),

        ('BndResponsePatternUT', 'BETWEEN',
         {'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)},
         'True ; ⌈(P & (! Q))⌉ ; ⌈(! Q)⌉ ; ⌈(((! Q) & R) & (! S))⌉ ; ⌈((! Q) & (! S))⌉ ∧ ℓ > T ; ⌈(! Q)⌉ ; ⌈Q⌉ ; True'),
    ])
    def test_bnd_response_pattern_ut(self, pattern: str, scope: str, expressions: dict[str, FNode], expected: str):
        actual = create_counter_trace(scope, pattern, expressions)
        self.assertEqual(expected, str(actual), msg="Error while creating counter trace.")
