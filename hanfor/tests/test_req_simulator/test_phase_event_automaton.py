from unittest import TestCase

from lark.lark import Lark
from pysmt.shortcuts import Symbol, And, LT, GE, Or, LE, TRUE, Not
from pysmt.typing import REAL

from req_simulator.counter_trace import CounterTraceTransformer
from req_simulator.phase_event_automaton import build_automaton, PhaseEventAutomaton, Transition, Phase, Sets
from tests.test_req_simulator.test_counter_trace import testcases

parser = Lark.open('../../req_simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace',
                   parser='lalr')


class TestPhaseEventAutomaton(TestCase):

    def test_false(self):
        expressions, ct_str, _ = testcases['false']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()

        # ct0_st
        p1_invariant = TRUE()
        p1 = Phase(p1_invariant, TRUE(), Sets())
        # ct0_st
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true(self):
        expressions, ct_str, _ = testcases['true']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true_lower_bound_empty(self):
        expressions, ct_str, _ = testcases['true_lower_bound_empty']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_true_lower_bound(self):
        expressions, ct_str, _ = testcases['true_lower_bound']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        T, c0 = expressions['T'], Symbol('c0', REAL)

        # ct0_st0W
        p1_invariant = TRUE()
        p1 = Phase(p1_invariant, LE(c0, T), Sets(wait=frozenset({0}), active=frozenset({0})))
        # ct0_st0W
        expected.phases[None].add(Transition(None, p1, p1_invariant, frozenset({'c0'})))
        expected.phases[p1].add(Transition(p1, p1, And(p1_invariant, LT(c0, T))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_globally(self):
        expressions, ct_str, _ = testcases['absence_globally']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R = expressions['R']
        R_ = expressions_['R_']

        # ct0_st0
        p1 = Phase(Not(R), TRUE(), Sets(active=frozenset({0})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, Not(R_)))
        expected.phases[p1].add(Transition(p1, p1, Not(R_)))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_before(self):
        expressions, ct_str, _ = testcases['absence_before']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        P, R = expressions['P'], expressions['R']
        P_, R_ = expressions_['P_'], expressions_['R_']

        # ct0_st0
        p1 = Phase(And(Not(P), Not(R)), TRUE(), Sets(active=frozenset({0})))
        # ct0_st
        p2 = Phase(TRUE(), TRUE(), Sets())

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, And(Not(P_), Not(R_))))
        expected.phases[p1].add(Transition(p1, p1, And(Not(P_), Not(R_))))
        expected.phases[p1].add(Transition(p1, p2, P_))
        # ct0_st
        expected.phases[None].add(Transition(None, p2, P_))
        expected.phases[p2].add(Transition(p2, p2, TRUE()))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_after(self):
        expressions, ct_str, _ = testcases['absence_after']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        P, R = expressions['P'], expressions['R']
        P_, R_ = expressions_['P_'], expressions_['R_']

        # ct0_st0
        p1 = Phase(Not(P), TRUE(), Sets(active=frozenset({0})))
        # ct0_st012
        p2 = Phase(And(P, Not(R)), TRUE(), Sets(active=frozenset({0, 1, 2})))
        # ct0_st02
        p3 = Phase(And(Not(P), Not(R)), TRUE(), Sets(active=frozenset({0, 2})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, Not(P_)))
        expected.phases[p1].add(Transition(p1, p1, Not(P_)))
        expected.phases[p1].add(Transition(p1, p2, And(P_, Not(R_))))
        # ct0_st012
        expected.phases[None].add(Transition(None, p2, And(P_, Not(R_))))
        expected.phases[p2].add(Transition(p2, p2, And(P_, Not(R_))))
        expected.phases[p2].add(Transition(p2, p3, And(Not(P_), Not(R_))))
        # ct0_st02
        expected.phases[p3].add(Transition(p3, p3, And(Not(P_), Not(R_))))
        expected.phases[p3].add(Transition(p3, p2, And(P_, Not(R_))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_l_pattern_globally(self):
        expressions, ct_str, _ = testcases['duration_bound_l_globally']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R, T, c2 = expressions['R'], expressions['T'], Symbol('c2', REAL)
        R_ = expressions_['R_']

        # ct0_st0
        p1 = Phase(R, TRUE(), Sets(active=frozenset({0})))
        # ct0_st01
        p2 = Phase(Not(R), TRUE(), Sets(active=frozenset({0, 1})))
        # ct0_st02
        p3 = Phase(R, LE(c2, T), Sets(less=frozenset({2}), active=frozenset({0, 2})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, R_))
        expected.phases[p1].add(Transition(p1, p1, R_))
        expected.phases[p1].add(Transition(p1, p2, Not(R_)))
        # ct0_st01
        expected.phases[None].add(Transition(None, p2, Not(R_)))
        expected.phases[p2].add(Transition(p2, p2, Not(R_)))
        expected.phases[p2].add(Transition(p2, p3, R_, frozenset({'c2'})))
        # ct0_st02
        expected.phases[p3].add(Transition(p3, p3, And(LT(c2, T), R_)))
        expected.phases[p3].add(Transition(p3, p1, And(GE(c2, T), R_)))
        expected.phases[p3].add(Transition(p3, p2, And(Or(R_, GE(c2, T)), Not(R_))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_u_globally(self):
        expressions, ct_str, _ = testcases['duration_bound_u_globally']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R, T, c1 = expressions['R'], expressions['T'], Symbol('c1', REAL)
        R_ = expressions_['R_']

        # ct0_st0
        p1 = Phase(Not(R), TRUE(), Sets(active=frozenset({0})))
        # ct0_st01X
        p2 = Phase(R, LE(c1, T), Sets(gteq=frozenset({1}), wait=frozenset({1}), active=frozenset({0, 1})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, Not(R_)))
        expected.phases[p1].add(Transition(p1, p1, Not(R_)))
        expected.phases[p1].add(Transition(p1, p2, R_, frozenset({'c1'})))
        # ct0_st01X
        expected.phases[None].add(Transition(None, p2, R_, frozenset({'c1'})))
        expected.phases[p2].add(Transition(p2, p2, And(LT(c1, T), R_)))
        expected.phases[p2].add(Transition(p2, p1, And(LT(c1, T), Not(R_))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_globally(self):
        expressions, ct_str, _ = testcases['response_delay_globally']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R, S, T, c2 = expressions['R'], expressions['S'], expressions['T'], Symbol('c2', REAL)
        R_, S_ = expressions_['R_'], expressions_['S_']

        # ct0_st0
        p1 = Phase(Or(S, Not(R)), TRUE(), Sets(active=frozenset({0})))
        # ct0_st012W
        p2 = Phase(And(R, Not(S)), LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 1, 2})))
        # ct0_st02W
        p3 = Phase(And(Not(R), Not(S)), LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 2})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, Or(S_, Not(R_))))
        expected.phases[p1].add(Transition(p1, p1, Or(S_, Not(R_))))
        expected.phases[p1].add(Transition(p1, p2, And(R_, Not(S_)), frozenset({'c2'})))
        # ct0_st012W
        expected.phases[None].add(Transition(None, p2, And(R_, Not(S_)), frozenset({'c2'})))
        expected.phases[p2].add(Transition(p2, p2, And(LT(c2, T), And(R_, Not(S_)))))
        expected.phases[p2].add(Transition(p2, p1, And(S_, Or(S_, Not(R_)))))
        expected.phases[p2].add(Transition(p2, p3, And(LT(c2, T), And(Not(R_), Not(S_)))))
        # ct0_st02W
        expected.phases[p3].add(Transition(p3, p3, And(LT(c2, T), And(Not(R_), Not(S_)))))
        expected.phases[p3].add(Transition(p3, p1, And(S_, Or(S_, Not(R_)))))
        expected.phases[p3].add(Transition(p3, p2, And(LT(c2, T), And(R_, Not(S_)))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_before(self):
        expressions, ct_str, _ = testcases['response_delay_before']
        expressions_ = {k + '_': Symbol(v.symbol_name() + '_', v.symbol_type()) for k, v in expressions.items()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        P, R, S, T, c2 = expressions['P'], expressions['R'], expressions['S'], expressions['T'], Symbol('c2', REAL)
        P_, R_, S_ = expressions_['P_'], expressions_['R_'], expressions_['S_']

        # ct0_st0
        p1 = Phase(And(Not(P), Or(S, Not(R))), TRUE(), Sets(active=frozenset({0})))
        # ct0_st012W
        p2 = Phase(And(Not(P), And(R, Not(S))), LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 1, 2})))
        # ct0_st02W
        p3 = Phase(And(Not(P), And(Not(R), Not(S))), LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 2})))
        # ct0_st
        p4 = Phase(TRUE(), TRUE(), Sets())

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, And(Not(P_), Or(S_, Not(R_)))))
        expected.phases[p1].add(Transition(p1, p1, And(Not(P_), Or(S_, Not(R_)))))
        expected.phases[p1].add(Transition(p1, p2, And(Not(P_), And(R_, Not(S_))), frozenset({'c2'})))
        expected.phases[p1].add(Transition(p1, p4, P_))
        # ct0_st012W
        expected.phases[None].add(Transition(None, p2, And(Not(P_), And(R_, Not(S_))), frozenset({'c2'})))
        expected.phases[p2].add(Transition(p2, p2, And(LT(c2, T), And(Not(P_), And(R_, Not(S_))))))
        expected.phases[p2].add(Transition(p2, p1, And(Or(P_, S_), And(Not(P_), Or(S_, Not(R_))))))
        expected.phases[p2].add(Transition(p2, p3, And(LT(c2, T), And(Not(P_), And(Not(R_), Not(S_))))))
        expected.phases[p2].add(Transition(p2, p4, P_))
        # ct0_st02W
        expected.phases[p3].add(Transition(p3, p3, And(LT(c2, T), And(Not(P_), And(Not(R_), Not(S_))))))
        expected.phases[p3].add(Transition(p3, p1, And(Or(P_, S_), And(Not(P_), Or(S_, Not(R_))))))
        expected.phases[p3].add(Transition(p3, p2, And(LT(c2, T), And(Not(P_), And(R_, Not(S_))))))
        expected.phases[p3].add(Transition(p3, p4, P_))
        # ct0_st
        expected.phases[None].add(Transition(None, p4, P_))
        expected.phases[p4].add(Transition(p4, p4, TRUE()))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")
