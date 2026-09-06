from unittest import TestCase

from pysmt.environment import Environment

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import PeaBuilder
from lib_pea.location import PhaseSetsLocation
from lib_pea.pea import PhaseSetsPea
from lib_pea.phase_sets import PhaseSets
from lib_pea.transition import PhaseSetsTransition
from lib_pea.utils import get_countertrace_parser
from tests.test_req_simulator.test_counter_trace import pattern_cases


class TestPhaseEventAutomaton(TestCase):
    def test_false(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "false")
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)

        # ct0_st
        p1_invariant = fmgr.TRUE()
        p1 = PhaseSetsLocation(smt_env, p1_invariant, fmgr.TRUE(), PhaseSets())
        # ct0_st
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, p1_invariant))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, p1_invariant))

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "true")
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true_lower_bound_empty(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "true_lower_bound_empty")
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true_lower_bound(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "true_lower_bound")
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        T, c0 = expressions["T"], fmgr.Symbol("c0", tmgr.REAL())

        # ct0_st0W
        p1_invariant = fmgr.TRUE()
        p1 = PhaseSetsLocation(
            smt_env, p1_invariant, fmgr.LE(c0, T), PhaseSets(wait=frozenset({0}), active=frozenset({0}))
        )
        # ct0_st0W
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, p1_invariant, frozenset({"c0"})))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, fmgr.And(p1_invariant, fmgr.LT(c0, T))))

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_globally(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "absence_globally")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        R = expressions["R"]
        R_ = expressions_["R_"]
        R_ = R

        # ct0_st0
        p1 = PhaseSetsLocation(smt_env, fmgr.Not(R), fmgr.TRUE(), PhaseSets(active=frozenset({0})))

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, fmgr.Not(R_)))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, fmgr.Not(R_)))

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_before(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "absence_before")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        P, R = expressions["P"], expressions["R"]
        P_, R_ = expressions_["P_"], expressions_["R_"]
        P_, R_ = P, R

        # ct0_st0
        p1 = PhaseSetsLocation(
            smt_env, fmgr.And(fmgr.Not(P), fmgr.Not(R)), fmgr.TRUE(), PhaseSets(active=frozenset({0}))
        )
        # ct0_st
        p2 = PhaseSetsLocation(smt_env, fmgr.TRUE(), fmgr.TRUE(), PhaseSets())

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, fmgr.And(fmgr.Not(P_), fmgr.Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, fmgr.And(fmgr.Not(P_), fmgr.Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p2, P_))
        # ct0_st
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p2, P_))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p2, fmgr.TRUE()))

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_after(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "absence_after")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        P, R = expressions["P"], expressions["R"]
        P_, R_ = expressions_["P_"], expressions_["R_"]
        P_, R_ = P, R

        # ct0_st0
        p1 = PhaseSetsLocation(smt_env, fmgr.Not(P), fmgr.TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st012
        p2 = PhaseSetsLocation(smt_env, fmgr.And(P, fmgr.Not(R)), fmgr.TRUE(), PhaseSets(active=frozenset({0, 1, 2})))
        # ct0_st02
        p3 = PhaseSetsLocation(
            smt_env, fmgr.And(fmgr.Not(P), fmgr.Not(R)), fmgr.TRUE(), PhaseSets(active=frozenset({0, 2}))
        )

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, fmgr.Not(P_)))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, fmgr.Not(P_)))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p2, fmgr.And(P_, fmgr.Not(R_))))
        # ct0_st012
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p2, fmgr.And(P_, fmgr.Not(R_))))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p2, fmgr.And(P_, fmgr.Not(R_))))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p3, fmgr.And(fmgr.Not(P_), fmgr.Not(R_))))
        # ct0_st02
        expected.transitions[p3].add(PhaseSetsTransition(smt_env, p3, p3, fmgr.And(fmgr.Not(P_), fmgr.Not(R_))))
        expected.transitions[p3].add(PhaseSetsTransition(smt_env, p3, p2, fmgr.And(P_, fmgr.Not(R_))))

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_l_pattern_globally(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "duration_bound_l_globally")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        R, T, c2 = expressions["R"], expressions["T"], fmgr.Symbol("c2", tmgr.REAL())
        R_ = expressions_["R_"]
        R_ = R

        # ct0_st0
        p1 = PhaseSetsLocation(smt_env, R, fmgr.TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st01
        p2 = PhaseSetsLocation(smt_env, fmgr.Not(R), fmgr.TRUE(), PhaseSets(active=frozenset({0, 1})))
        # ct0_st02
        p3 = PhaseSetsLocation(smt_env, R, fmgr.LE(c2, T), PhaseSets(less=frozenset({2}), active=frozenset({0, 2})))

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, R_))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, R_))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p2, fmgr.Not(R_)))
        # ct0_st01
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p2, fmgr.Not(R_)))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p2, fmgr.Not(R_)))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p3, R_, frozenset({"c2"})))
        # ct0_st02
        expected.transitions[p3].add(PhaseSetsTransition(smt_env, p3, p3, fmgr.And(fmgr.LT(c2, T), R_)))
        expected.transitions[p3].add(PhaseSetsTransition(smt_env, p3, p1, fmgr.And(fmgr.GE(c2, T), R_)))
        expected.transitions[p3].add(
            PhaseSetsTransition(smt_env, p3, p2, fmgr.And(fmgr.Or(R_, fmgr.GE(c2, T)), fmgr.Not(R_)))
        )

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_u_globally(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "duration_bound_u_globally")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        R, T, c1 = expressions["R"], expressions["T"], fmgr.Symbol("c1", tmgr.REAL())
        R_ = expressions_["R_"]
        R_ = R

        # ct0_st0
        p1 = PhaseSetsLocation(smt_env, fmgr.Not(R), fmgr.TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st01X
        p2 = PhaseSetsLocation(
            smt_env,
            R,
            fmgr.LT(c1, T),
            PhaseSets(gteq=frozenset({1}), wait=frozenset({1}), active=frozenset({0, 1})),
        )

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, fmgr.Not(R_)))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, fmgr.Not(R_)))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p2, R_, frozenset({"c1"})))
        # ct0_st01X
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p2, R_, frozenset({"c1"})))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p2, fmgr.And(fmgr.LT(c1, T), R_)))
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p1, fmgr.And(fmgr.LT(c1, T), fmgr.Not(R_))))

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_globally(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "response_delay_globally")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        R, S, T, c2 = (
            expressions["R"],
            expressions["S"],
            expressions["T"],
            fmgr.Symbol("c2", tmgr.REAL()),
        )
        R_, S_ = expressions_["R_"], expressions_["S_"]
        S_, R_ = S, R

        # ct0_st0
        p1 = PhaseSetsLocation(smt_env, fmgr.Or(S, fmgr.Not(R)), fmgr.TRUE(), PhaseSets(active=frozenset({0})))
        # ct0_st012W
        p2 = PhaseSetsLocation(
            smt_env,
            fmgr.And(R, fmgr.Not(S)),
            fmgr.LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 1, 2})),
        )
        # ct0_st02W
        p3 = PhaseSetsLocation(
            smt_env,
            fmgr.And(fmgr.Not(R), fmgr.Not(S)),
            fmgr.LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 2})),
        )

        # ct0_st0
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p1, fmgr.Or(S_, fmgr.Not(R_))))
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p1, fmgr.Or(S_, fmgr.Not(R_))))
        expected.transitions[p1].add(
            PhaseSetsTransition(smt_env, p1, p2, fmgr.And(R_, fmgr.Not(S_)), frozenset({"c2"}))
        )
        # ct0_st012W
        expected.transitions[None].add(
            PhaseSetsTransition(smt_env, None, p2, fmgr.And(R_, fmgr.Not(S_)), frozenset({"c2"}))
        )
        expected.transitions[p2].add(
            PhaseSetsTransition(smt_env, p2, p2, fmgr.And(fmgr.LT(c2, T), fmgr.And(R_, fmgr.Not(S_))))
        )
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p1, fmgr.And(S_, fmgr.Or(S_, fmgr.Not(R_)))))
        expected.transitions[p2].add(
            PhaseSetsTransition(smt_env, p2, p3, fmgr.And(fmgr.LT(c2, T), fmgr.And(fmgr.Not(R_), fmgr.Not(S_))))
        )
        # ct0_st02W
        expected.transitions[p3].add(
            PhaseSetsTransition(smt_env, p3, p3, fmgr.And(fmgr.LT(c2, T), fmgr.And(fmgr.Not(R_), fmgr.Not(S_))))
        )
        expected.transitions[p3].add(PhaseSetsTransition(smt_env, p3, p1, fmgr.And(S_, fmgr.Or(S_, fmgr.Not(R_)))))
        expected.transitions[p3].add(
            PhaseSetsTransition(smt_env, p3, p2, fmgr.And(fmgr.LT(c2, T), fmgr.And(R_, fmgr.Not(S_))))
        )

        actual = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_before(self):
        smt_env = Environment()
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        expressions, ct_str, _ = pattern_cases(smt_env, "response_delay_before")
        expressions_ = {k + "_": fmgr.Symbol(v.symbol_name() + "_", v.symbol_type()) for k, v in expressions.items()}
        ct = CountertraceTransformer(smt_env, expressions).transform(get_countertrace_parser().parse(ct_str))

        expected = PhaseSetsPea(smt_env, ct)
        P, R, S, T, c2 = (
            expressions["P"],
            expressions["R"],
            expressions["S"],
            expressions["T"],
            fmgr.Symbol("c2", tmgr.REAL()),
        )
        P_, R_, S_ = expressions_["P_"], expressions_["R_"], expressions_["S_"]
        P_, R_, S_ = P, R, S

        # ct0_st0
        p1 = PhaseSetsLocation(
            smt_env, fmgr.And(fmgr.Not(P), fmgr.Or(S, fmgr.Not(R))), fmgr.TRUE(), PhaseSets(active=frozenset({0}))
        )
        # ct0_st012W
        p2 = PhaseSetsLocation(
            smt_env,
            fmgr.And(fmgr.Not(P), fmgr.And(R, fmgr.Not(S))),
            fmgr.LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 1, 2})),
        )
        # ct0_st02W
        p3 = PhaseSetsLocation(
            smt_env,
            fmgr.And(fmgr.Not(P), fmgr.And(fmgr.Not(R), fmgr.Not(S))),
            fmgr.LE(c2, T),
            PhaseSets(wait=frozenset({2}), active=frozenset({0, 2})),
        )
        # ct0_st
        p4 = PhaseSetsLocation(smt_env, fmgr.TRUE(), fmgr.TRUE(), PhaseSets())

        # ct0_st0
        expected.transitions[None].add(
            PhaseSetsTransition(smt_env, None, p1, fmgr.And(fmgr.Not(P_), fmgr.Or(S_, fmgr.Not(R_))))
        )
        expected.transitions[p1].add(
            PhaseSetsTransition(smt_env, p1, p1, fmgr.And(fmgr.Not(P_), fmgr.Or(S_, fmgr.Not(R_))))
        )
        expected.transitions[p1].add(
            PhaseSetsTransition(smt_env, p1, p2, fmgr.And(fmgr.Not(P_), fmgr.And(R_, fmgr.Not(S_))), frozenset({"c2"}))
        )
        expected.transitions[p1].add(PhaseSetsTransition(smt_env, p1, p4, P_))
        # ct0_st012W
        expected.transitions[None].add(
            PhaseSetsTransition(
                smt_env, None, p2, fmgr.And(fmgr.Not(P_), fmgr.And(R_, fmgr.Not(S_))), frozenset({"c2"})
            )
        )
        expected.transitions[p2].add(
            PhaseSetsTransition(
                smt_env, p2, p2, fmgr.And(fmgr.LT(c2, T), fmgr.And(fmgr.Not(P_), fmgr.And(R_, fmgr.Not(S_))))
            )
        )
        expected.transitions[p2].add(
            PhaseSetsTransition(
                smt_env, p2, p1, fmgr.And(fmgr.Or(P_, S_), fmgr.And(fmgr.Not(P_), fmgr.Or(S_, fmgr.Not(R_))))
            )
        )
        expected.transitions[p2].add(
            PhaseSetsTransition(
                smt_env, p2, p3, fmgr.And(fmgr.LT(c2, T), fmgr.And(fmgr.Not(P_), fmgr.And(fmgr.Not(R_), fmgr.Not(S_))))
            )
        )
        expected.transitions[p2].add(PhaseSetsTransition(smt_env, p2, p4, P_))
        # ct0_st02W
        expected.transitions[p3].add(
            PhaseSetsTransition(
                smt_env, p3, p3, fmgr.And(fmgr.LT(c2, T), fmgr.And(fmgr.Not(P_), fmgr.And(fmgr.Not(R_), fmgr.Not(S_))))
            )
        )
        expected.transitions[p3].add(
            PhaseSetsTransition(
                smt_env, p3, p1, fmgr.And(fmgr.Or(P_, S_), fmgr.And(fmgr.Not(P_), fmgr.Or(S_, fmgr.Not(R_))))
            )
        )
        expected.transitions[p3].add(
            PhaseSetsTransition(
                smt_env, p3, p2, fmgr.And(fmgr.LT(c2, T), fmgr.And(fmgr.Not(P_), fmgr.And(R_, fmgr.Not(S_))))
            )
        )
        expected.transitions[p3].add(PhaseSetsTransition(smt_env, p3, p4, P_))
        # ct0_st
        expected.transitions[None].add(PhaseSetsTransition(smt_env, None, p4, P_))
        expected.transitions[p4].add(PhaseSetsTransition(smt_env, p4, p4, fmgr.TRUE()))

        actual: PhaseSetsPea = PeaBuilder(smt_env).build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")
