from collections import namedtuple
from unittest import TestCase

from parameterized import parameterized
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, FALSE, And, Equals, Int, Real
from pysmt.typing import REAL, INT

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.utils import get_countertrace_parser

Test = namedtuple("Test", "expressions ct_str expected")

testcases = {
    "false": Test({"P": FALSE()}, "⌈P⌉;true", "⌈False⌉;True"),
    "true": Test({}, "true;true", "True;True"),
    "true_lower_bound_empty": Test({"T": Symbol("T", REAL)}, "true ∧ ℓ >₀ T;true", "True ∧ ℓ >₀ T;True"),
    "true_lower_bound": Test({"T": Symbol("T", REAL)}, "true ∧ ℓ > T;true", "True ∧ ℓ > T;True"),
    "absence_globally": Test({"R": Symbol("R")}, "true;⌈R⌉;true", "True;⌈R⌉;True"),
    "absence_before": Test({"P": Symbol("P"), "R": Symbol("R")}, "⌈!P⌉;⌈(!P && R)⌉;true", "⌈(! P)⌉;⌈((! P) & R)⌉;True"),
    "absence_after": Test({"P": Symbol("P"), "R": Symbol("R")}, "true;⌈P⌉;true;⌈R⌉;true", "True;⌈P⌉;True;⌈R⌉;True"),
    "absence_between": Test(
        {"P": Symbol("P"), "Q": Symbol("Q"), "R": Symbol("R")},
        "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
        "True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & R)⌉;⌈(! Q)⌉;⌈Q⌉;True",
    ),
    "absence_after_until": Test(
        {"P": Symbol("P"), "Q": Symbol("Q"), "R": Symbol("R")},
        "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true",
        "True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & R)⌉;True",
    ),
    "duration_bound_l_globally": Test(
        {"R": Symbol("R"), "T": Symbol("T", REAL)},
        "true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true",
        "True;⌈(! R)⌉;⌈R⌉ ∧ ℓ < T;⌈(! R)⌉;True",
    ),
    "duration_bound_l_before": Test(
        {"P": Symbol("P"), "R": Symbol("R"), "T": Symbol("T", REAL)},
        "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < T;⌈(!P && !R)⌉;true",
        "⌈(! P)⌉;⌈((! P) & (! R))⌉;⌈((! P) & R)⌉ ∧ ℓ < T;⌈((! P) & (! R))⌉;True",
    ),
    "duration_bound_l_after": Test(
        {"P": Symbol("P"), "R": Symbol("R"), "T": Symbol("T", REAL)},
        "true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true",
        "True;⌈P⌉;True;⌈(! R)⌉;⌈R⌉ ∧ ℓ < T;⌈(! R)⌉;True",
    ),
    "duration_bound_l_between": Test(
        {"P": Symbol("P"), "Q": Symbol("Q"), "R": Symbol("R"), "T": Symbol("T", REAL)},
        "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < T;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true",
        "True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & (! R))⌉;⌈((! Q) & R)⌉ ∧ ℓ < T;⌈((! Q) & (! R))⌉;⌈(! Q)⌉;⌈Q⌉;True",
    ),
    "duration_bound_l_after_until": Test(
        {"P": Symbol("P"), "Q": Symbol("Q"), "R": Symbol("R"), "T": Symbol("T", REAL)},
        "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < T;⌈(!Q && !R)⌉;true",
        "True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & (! R))⌉;⌈((! Q) & R)⌉ ∧ ℓ < T;⌈((! Q) & (! R))⌉;True",
    ),
    "duration_bound_u_globally": Test(
        {"R": Symbol("R"), "T": Symbol("T", REAL)}, "true;⌈R⌉ ∧ ℓ ≥ T;true", "True;⌈R⌉ ∧ ℓ ≥ T;True"
    ),
    "response_delay_globally": Test(
        {"R": Symbol("R"), "S": Symbol("S"), "T": Symbol("T", REAL)},
        "true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true",
        "True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True",
    ),
    "response_delay_before": Test(
        {"P": Symbol("P"), "R": Symbol("R"), "S": Symbol("S"), "T": Symbol("T", REAL)},
        "⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true",
        "⌈(! P)⌉;⌈((! P) & (R & (! S)))⌉;⌈((! P) & (! S))⌉ ∧ ℓ > T;True",
    ),
    "response_delay_after": Test(
        {"P": Symbol("P"), "R": Symbol("R"), "S": Symbol("S"), "T": Symbol("T", REAL)},
        "true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true",
        "True;⌈P⌉;True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True",
    ),
    "response_delay_between": Test(
        {"P": Symbol("P"), "Q": Symbol("Q"), "R": Symbol("R"), "S": Symbol("S"), "T": Symbol("T", REAL)},
        "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true",
        "True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & (R & (! S)))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;⌈(! Q)⌉;⌈Q⌉;True",
    ),
    "response_delay_after_until": Test(
        {"P": Symbol("P"), "Q": Symbol("Q"), "R": Symbol("R"), "S": Symbol("S"), "T": Symbol("T", REAL)},
        "true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true",
        "True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & (R & (! S)))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;True",
    ),
    "universality_globally": Test(
        {"P": And(Equals(Symbol("int", INT), Int(1)), Equals(Symbol("real", REAL), Real(1.0)))},
        "true;⌈P⌉;true",
        "True;⌈((int = 1) & (real = 1.0))⌉;True",
    ),
}


class TestCounterTrace(TestCase):
    # TODO: Obsolete.
    """
    @parameterized.expand([
        ('BndResponsePatternUT', 'GLOBALLY',
         {'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', REAL)},
         'True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True'),

        ('BndResponsePatternUT', 'BEFORE',
         {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', REAL)},
         '⌈(! P)⌉;⌈(((! P) & R) & (! S))⌉;⌈((! P) & (! S))⌉ ∧ ℓ > T;True'),

        ('BndResponsePatternUT', 'AFTER',
         {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', REAL)},
         'True;⌈P⌉;True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True'),

        ('BndResponsePatternUT', 'BETWEEN',
         {'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', REAL)},
         'True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈(((! Q) & R) & (! S))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;⌈(! Q)⌉;⌈Q⌉;True'),

        ('BndResponsePatternUT', 'AFTER_UNTIL',
         {'P': Symbol('P'), 'Q': Symbol('Q'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', REAL)},
         'True;⌈P⌉;⌈(! Q)⌉;⌈(((! Q) & R) & (! S))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;True'),
    ])
    def test_bnd_response_pattern_ut(self, pattern: str, scope: str, expressions: dict[str, FNode], expected: str):
        actual = create_counter_trace(scope, pattern, expressions)
        self.assertEqual(expected, str(actual), msg="Error while creating counter trace.")
    """

    @parameterized.expand([(k, *v) for k, v in testcases.items()])
    def test_counter_trace(self, name, expressions: dict[str, FNode], counter_trace: str, expected: str):
        lark_tree = get_countertrace_parser().parse(counter_trace)
        actual = CountertraceTransformer(expressions).transform(lark_tree)
        self.assertEqual(expected, str(actual), msg="Error while parsing counter trace.")
        # Image.open(BytesIO(pydot__tree_to_graph(lark_tree).create_png())).show()
