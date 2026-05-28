from typing import Tuple
from unittest import TestCase

from pysmt.environment import Environment

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import PeaBuilder
from lib_pea.pea import Pea
from lib_pea.utils import get_countertrace_parser


class TestPhaseAutomatonOperations(TestCase):

    def setUp(self):
        self.env = Environment()
        self.mgr = self.env.formula_manager
        self.tm = self.env.type_manager

        self.INITIAL_P = ({"P": self.mgr.Symbol("P")}, "⌈!P⌉;true")
        self.ALWAYS_NOT_P = ({"P": self.mgr.Symbol("P")}, "true;⌈P⌉;true")

        self.DBLB_1 = (
            {"P": self.mgr.Symbol("P"), "R": self.mgr.Symbol("R"), "T": self.mgr.Symbol("T", self.tm.REAL())},
            "true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true",
        )
        self.DBLB_2 = (
            {"P": self.mgr.Symbol("P"), "R": self.mgr.Symbol("R"), "T": self.mgr.Symbol("T", self.tm.REAL())},
            "true;⌈P⌉;true;⌈(! R)⌉;⌈R⌉ ∧ ℓ < T;⌈(! R)⌉;true",
        )

        self.solver = self.env.factory.Solver()

    def test_identity(self):
        a1 = self.__get_automaton(self.ALWAYS_NOT_P)
        a2 = self.__get_automaton(self.ALWAYS_NOT_P)
        r = a1.intersect(a2, self.env, self.solver)
        print(r)
        # TODO check

    def test_empty(self):
        a1 = self.__get_automaton(self.INITIAL_P)
        a2 = self.__get_automaton(self.ALWAYS_NOT_P)
        r = a1.intersect(a2, self.env, self.solver)
        print(r)
        # TODO check

    def test_large(self):
        a1 = self.__get_automaton(self.DBLB_1)
        a2 = self.__get_automaton(self.DBLB_2)
        r = a1.intersect(a2, self.env, self.solver)
        print(r)
        pass

    def __get_automaton(self, test: Tuple[dict, str]) -> Pea:
        expressions, ct_str = test
        ct = CountertraceTransformer(self.env, expressions).transform(get_countertrace_parser().parse(ct_str))
        return PeaBuilder(self.env).build_automaton(ct)
