from unittest import TestCase

from pysmt.shortcuts import Symbol, And, LT, GE, Or, LE, TRUE, Not
from pysmt.typing import REAL

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.pea import PhaseSetsPea
from lib_pea.transition import PhaseSetsTransition
from lib_pea.location import PhaseSetsLocation
from lib_pea.phase_sets import PhaseSets
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.utils import get_countertrace_parser
from tests.test_req_simulator.test_counter_trace import testcases


class TestPhaseEventAutomaton(TestCase):
    def test_false(self):
        expressions, ct_str, _ = testcases["false"]
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()

        # ct0_st
        p1_invariant = TRUE()
        p1 = PhaseSetsLocation(p1_invariant, TRUE(), PhaseSets())
        # ct0_st
        expected.transitions[None].add(PhaseSetsTransition(None, p1, p1_invariant))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, p1_invariant))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true(self):
        expressions, ct_str, _ = testcases["true"]
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true_lower_bound_empty(self):
        expressions, ct_str, _ = testcases["true_lower_bound_empty"]
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true_lower_bound(self):
        expressions, ct_str, _ = testcases["true_lower_bound"]
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        T, c0 = expressions["T"], Symbol("c0", REAL)

        # ct0_st0W
        p1_invariant = TRUE()
        p1 = PhaseSetsLocation(p1_invariant, LE(c0, T), PhaseSets(wait=frozenset({0}), active=frozenset({0})))
        # ct0_st0W
        expected.transitions[None].add(PhaseSetsTransition(None, p1, p1_invariant, frozenset({"c0"})))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, And(p1_invariant, LT(c0, T))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_globally(self):
        expressions, ct_str, _ = testcases["absence_globally"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        R = expressions["R"]
        R_ = expressions_["R_"]
        R_ = R

        # ct0_st0
        p1 = PhaseSetsLocation(Not(R), TRUE(), PhaseSets(active=frozenset({0})))

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, Not(R_)))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, Not(R_)))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_before(self):
        expressions, ct_str, _ = testcases["absence_before"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        P, R = expressions["P"], expressions["R"]
        P_, R_ = expressions_["P_"], expressions_["R_"]
        P_, R_ = P, R

        # ct0_st0
        p1 = PhaseSetsLocation(And(Not(P), Not(R)), TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st
        p2 = PhaseSetsLocation(TRUE(), TRUE(), PhaseSets())

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, And(Not(P_), Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, And(Not(P_), Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p2, P_))
        # ct0_st
        expected.transitions[None].add(PhaseSetsTransition(None, p2, P_))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p2, TRUE()))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_after(self):
        expressions, ct_str, _ = testcases["absence_after"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        P, R = expressions["P"], expressions["R"]
        P_, R_ = expressions_["P_"], expressions_["R_"]
        P_, R_ = P, R

        # ct0_st0
        p1 = PhaseSetsLocation(Not(P), TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st012
        p2 = PhaseSetsLocation(And(P, Not(R)), TRUE(), PhaseSets(active=frozenset({0, 1, 2})))
        # ct0_st02
        p3 = PhaseSetsLocation(And(Not(P), Not(R)), TRUE(), PhaseSets(active=frozenset({0, 2})))

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, Not(P_)))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, Not(P_)))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p2, And(P_, Not(R_))))
        # ct0_st012
        expected.transitions[None].add(PhaseSetsTransition(None, p2, And(P_, Not(R_))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p2, And(P_, Not(R_))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p3, And(Not(P_), Not(R_))))
        # ct0_st02
        expected.transitions[p3].add(PhaseSetsTransition(p3, p3, And(Not(P_), Not(R_))))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p2, And(P_, Not(R_))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_l_pattern_globally(self):
        expressions, ct_str, _ = testcases["duration_bound_l_globally"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        R, T, c2 = expressions["R"], expressions["T"], Symbol("c2", REAL)
        R_ = expressions_["R_"]
        R_ = R

        # ct0_st0
        p1 = PhaseSetsLocation(R, TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st01
        p2 = PhaseSetsLocation(Not(R), TRUE(), PhaseSets(active=frozenset({0, 1})))
        # ct0_st02
        p3 = PhaseSetsLocation(R, LE(c2, T), PhaseSets(less=frozenset({2}), active=frozenset({0, 2})))

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, R_))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, R_))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p2, Not(R_)))
        # ct0_st01
        expected.transitions[None].add(PhaseSetsTransition(None, p2, Not(R_)))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p2, Not(R_)))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p3, R_, frozenset({"c2"})))
        # ct0_st02
        expected.transitions[p3].add(PhaseSetsTransition(p3, p3, And(LT(c2, T), R_)))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p1, And(GE(c2, T), R_)))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p2, And(Or(R_, GE(c2, T)), Not(R_))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_u_globally(self):
        expressions, ct_str, _ = testcases["duration_bound_u_globally"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        R, T, c1 = expressions["R"], expressions["T"], Symbol("c1", REAL)
        R_ = expressions_["R_"]
        R_ = R

        # ct0_st0
        p1 = PhaseSetsLocation(Not(R), TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st01X
        p2 = PhaseSetsLocation(
            R,
            LT(c1, T),
            PhaseSets(gteq=frozenset({1}), wait=frozenset({1}), active=frozenset({0, 1})),
        )

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, Not(R_)))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, Not(R_)))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p2, R_, frozenset({"c1"})))
        # ct0_st01X
        expected.transitions[None].add(PhaseSetsTransition(None, p2, R_, frozenset({"c1"})))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p2, And(LT(c1, T), R_)))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p1, And(LT(c1, T), Not(R_))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_globally(self):
        expressions, ct_str, _ = testcases["response_delay_globally"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        R, S, T, c2 = (
            expressions["R"],
            expressions["S"],
            expressions["T"],
            Symbol("c2", REAL),
        )
        R_, S_ = expressions_["R_"], expressions_["S_"]
        S_, R_ = S, R

        # ct0_st0
        p1 = PhaseSetsLocation(Or(S, Not(R)), TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st012W
        p2 = PhaseSetsLocation(
            And(R, Not(S)),
            LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 1, 2})),
        )
        # ct0_st02W
        p3 = PhaseSetsLocation(
            And(Not(R), Not(S)),
            LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 2})),
        )

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, Or(S_, Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, Or(S_, Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p2, And(R_, Not(S_)), frozenset({"c2"})))
        # ct0_st012W
        expected.transitions[None].add(PhaseSetsTransition(None, p2, And(R_, Not(S_)), frozenset({"c2"})))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p2, And(LT(c2, T), And(R_, Not(S_)))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p1, And(S_, Or(S_, Not(R_)))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p3, And(LT(c2, T), And(Not(R_), Not(S_)))))
        # ct0_st02W
        expected.transitions[p3].add(PhaseSetsTransition(p3, p3, And(LT(c2, T), And(Not(R_), Not(S_)))))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p1, And(S_, Or(S_, Not(R_)))))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p2, And(LT(c2, T), And(R_, Not(S_)))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_before(self):
        expressions, ct_str, _ = testcases["response_delay_before"]
        expressions_ = {k + "_": Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea()
        P, R, S, T, c2 = (
            expressions["P"],
            expressions["R"],
            expressions["S"],
            expressions["T"],
            Symbol("c2", REAL),
        )
        P_, R_, S_ = expressions_["P_"], expressions_["R_"], expressions_["S_"]
        P_, R_, S_ = P, R, S

        # ct0_st0
        p1 = PhaseSetsLocation(And(Not(P), Or(S, Not(R))), TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st012W
        p2 = PhaseSetsLocation(
            And(Not(P), And(R, Not(S))),
            LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 1, 2})),
        )
        # ct0_st02W
        p3 = PhaseSetsLocation(
            And(Not(P), And(Not(R), Not(S))),
            LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 2})),
        )
        # ct0_st
        p4 = PhaseSetsLocation(TRUE(), TRUE(), PhaseSets())

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(None, p1, And(Not(P_), Or(S_, Not(R_)))))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p1, And(Not(P_), Or(S_, Not(R_)))))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p2, And(Not(P_), And(R_, Not(S_))), frozenset({"c2"})))
        expected.transitions[p1].add(PhaseSetsTransition(p1, p4, P_))
        # ct0_st012W
        expected.transitions[None].add(PhaseSetsTransition(None, p2, And(Not(P_), And(R_, Not(S_))), frozenset({"c2"})))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p2, And(LT(c2, T), And(Not(P_), And(R_, Not(S_))))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p1, And(Or(P_, S_), And(Not(P_), Or(S_, Not(R_))))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p3, And(LT(c2, T), And(Not(P_), And(Not(R_), Not(S_))))))
        expected.transitions[p2].add(PhaseSetsTransition(p2, p4, P_))
        # ct0_st02W
        expected.transitions[p3].add(PhaseSetsTransition(p3, p3, And(LT(c2, T), And(Not(P_), And(Not(R_), Not(S_))))))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p1, And(Or(P_, S_), And(Not(P_), Or(S_, Not(R_))))))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p2, And(LT(c2, T), And(Not(P_), And(R_, Not(S_))))))
        expected.transitions[p3].add(PhaseSetsTransition(p3, p4, P_))
        # ct0_st
        expected.transitions[None].add(PhaseSetsTransition(None, p4, P_))
        expected.transitions[p4].add(PhaseSetsTransition(p4, p4, TRUE()))

        actual: PhaseSetsPea = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")
