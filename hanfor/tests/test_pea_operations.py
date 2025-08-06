from typing import Tuple
from unittest import TestCase

from pysmt.typing import REAL

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.pea import Pea
from lib_pea.utils import get_countertrace_parser
from tests.test_req_simulator.test_counter_trace import testcases

from pysmt.shortcuts import FALSE, And, Symbol, simplify

INITIAL_P = ({"P": Symbol("P")}, "⌈!P⌉;true")
ALWAYS_NOT_P = ({"P": Symbol("P")}, "true;⌈P⌉;true")

DBLB_1 = ({"P": Symbol("P"), "R": Symbol("R"), "T": Symbol("T", REAL)}, "true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true")
DBLB_2 = (
    {"P": Symbol("P"), "R": Symbol("R"), "T": Symbol("T", REAL)},
    "true;⌈P⌉;true;⌈(! R)⌉;⌈R⌉ ∧ ℓ < T;⌈(! R)⌉;true",
)


class TestPhaseAutomatonOperations(TestCase):

    def test_identity(self):
        a1 = self.__get_automaton(ALWAYS_NOT_P)
        a2 = self.__get_automaton(ALWAYS_NOT_P)
        r = a1.intersect(a2)
        print(r)
        # TODO check

    def test_empty(self):
        a1 = self.__get_automaton(INITIAL_P)
        a2 = self.__get_automaton(ALWAYS_NOT_P)
        r = a1.intersect(a2)
        print(r)
        # TODO check

    def test_large(self):
        a1 = self.__get_automaton(DBLB_1)
        a2 = self.__get_automaton(DBLB_2)
        r = a1.intersect(a2)
        print(r)
        pass

    def __get_automaton(self, test: Tuple[dict, str]) -> Pea:
        expressions, ct_str = test
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
        return build_automaton(ct)
