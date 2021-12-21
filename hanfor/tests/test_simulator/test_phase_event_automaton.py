from unittest import TestCase

from lark.lark import Lark
from pysmt.shortcuts import Symbol, And, LT, GE, Or, LE, TRUE, Not
from pysmt.typing import INT

from simulator.counter_trace import CounterTraceTransformer
from simulator.phase_event_automaton import build_automaton, PhaseEventAutomaton, Transition, Phase, Sets
from tests.test_simulator.test_counter_trace import testcases

parser = Lark.open('../../simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace', parser='lalr')


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
        T, c0 = expressions['T'], Symbol('c0', INT)

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
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R = expressions['R']

        # ct0_st0
        p1_invariant = Not(R)
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_before(self):
        expressions, ct_str, _ = testcases['absence_before']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        P, R = expressions['P'], expressions['R']

        # ct0_st0
        p1_invariant = And(Not(P), Not(R))
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        # ct0_st
        p2_invariant = TRUE()
        p2 = Phase(p2_invariant, TRUE(), Sets())

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p2, And(p2_invariant, P)))
        # ct0_st
        expected.phases[None].add(Transition(None, p2, And(p2_invariant, P)))
        expected.phases[p2].add(Transition(p2, p2, p2_invariant))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_absence_after(self):
        expressions, ct_str, _ = testcases['absence_after']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        P, R = expressions['P'], expressions['R']

        # ct0_st0
        p1_invariant = Not(P)
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        # ct0_st012
        p2_invariant = And(P, Not(R))
        p2 = Phase(p2_invariant, TRUE(), Sets(active=frozenset({0, 1, 2})))
        # ct0_st02
        p3_invariant = And(Not(P), Not(R))
        p3 = Phase(p3_invariant, TRUE(), Sets(active=frozenset({0, 2})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p2, p2_invariant))
        # ct0_st012
        expected.phases[None].add(Transition(None, p2, p2_invariant))
        expected.phases[p2].add(Transition(p2, p2, p2_invariant))
        expected.phases[p2].add(Transition(p2, p3, p3_invariant))
        # ct0_st02
        expected.phases[p3].add(Transition(p3, p3, p3_invariant))
        expected.phases[p3].add(Transition(p3, p2, p2_invariant))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_l_pattern_globally(self):
        expressions, ct_str, _ = testcases['duration_bound_l_globally']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R, T, c2 = expressions['R'], expressions['T'], Symbol('c2', INT)

        # ct0_st0
        p1_invariant = R
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        # ct0_st01
        p2_invariant = Not(R)
        p2 = Phase(p2_invariant, TRUE(), Sets(active=frozenset({0, 1})))
        # ct0_st02
        p3_invariant = R
        p3 = Phase(p3_invariant, LE(c2, T), Sets(less=frozenset({2}), active=frozenset({0, 2})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p2, p2_invariant))
        # ct0_st01
        expected.phases[None].add(Transition(None, p2, p2_invariant))
        expected.phases[p2].add(Transition(p2, p2, p2_invariant))
        expected.phases[p2].add(Transition(p2, p3, p3_invariant, frozenset({'c2'})))
        # ct0_st02
        expected.phases[p3].add(Transition(p3, p3, And(p3_invariant, LT(c2, T))))
        expected.phases[p3].add(Transition(p3, p1, And(p1_invariant, GE(c2, T))))
        expected.phases[p3].add(Transition(p3, p2, And(p2_invariant, Or(R, GE(c2, T)))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_globally(self):
        expressions, ct_str, _ = testcases['response_delay_globally']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        R, S, T, c2 = expressions['R'], expressions['S'], expressions['T'], Symbol('c2', INT)

        # ct0_st0
        p1_invariant = Or(S, Not(R))
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        # ct0_st012W
        p2_invariant = And(Not(S), R)
        p2 = Phase(p2_invariant, LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 1, 2})))
        # ct0_st02W
        p3_invariant = And(Not(S), Not(R))
        p3 = Phase(p3_invariant, LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 2})))

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p2, p2_invariant, frozenset({'c2'})))
        # ct0_st012W
        expected.phases[None].add(Transition(None, p2, p2_invariant, frozenset({'c2'})))
        expected.phases[p2].add(Transition(p2, p2, And(p2_invariant, LT(c2, T))))
        expected.phases[p2].add(Transition(p2, p1, And(p1_invariant, S)))
        expected.phases[p2].add(Transition(p2, p3, And(p3_invariant, LT(c2, T))))
        # ct0_st02W
        expected.phases[p3].add(Transition(p3, p3, And(p3_invariant, LT(c2, T))))
        expected.phases[p3].add(Transition(p3, p1, And(p1_invariant, S)))
        expected.phases[p3].add(Transition(p3, p2, And(p2_invariant, LT(c2, T))))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_response_delay_before(self):
        expressions, ct_str, _ = testcases['response_delay_before']
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))

        expected = PhaseEventAutomaton()
        P, R, S, T, c2 = expressions['P'], expressions['R'], expressions['S'], expressions['T'], Symbol('c2', INT)

        # ct0_st0
        p1_invariant = And(Not(P), Or(S, Not(R)))
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        # ct0_st012W
        p2_invariant = And(Not(P), And(R, Not(S)))
        p2 = Phase(p2_invariant, LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 1, 2})))
        # ct0_st02W
        p3_invariant = And(Not(P), And(Not(R), Not(S)))
        p3 = Phase(p3_invariant, LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 2})))
        # ct0_st
        p4_invariant = TRUE()
        p4 = Phase(p4_invariant, TRUE(), Sets())

        # ct0_st0
        expected.phases[None].add(Transition(None, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p1, p1_invariant))
        expected.phases[p1].add(Transition(p1, p2, p2_invariant, frozenset({'c2'})))
        expected.phases[p1].add(Transition(p1, p4, And(p4_invariant, P)))
        # ct0_st012W
        expected.phases[None].add(Transition(None, p2, p2_invariant, frozenset({'c2'})))
        expected.phases[p2].add(Transition(p2, p2, And(p2_invariant, LT(c2, T))))
        expected.phases[p2].add(Transition(p2, p1, And(p1_invariant, Or(P, S))))
        expected.phases[p2].add(Transition(p2, p3, And(p3_invariant, LT(c2, T))))
        expected.phases[p2].add(Transition(p2, p4, And(p4_invariant, P)))
        # ct0_st02W
        expected.phases[p3].add(Transition(p3, p3, And(p3_invariant, LT(c2, T))))
        expected.phases[p3].add(Transition(p3, p1, And(p1_invariant, Or(P, S))))
        expected.phases[p3].add(Transition(p3, p2, And(p2_invariant, LT(c2, T))))
        expected.phases[p3].add(Transition(p3, p4, And(p4_invariant, P)))
        # ct0_st
        expected.phases[None].add(Transition(None, p4, And(p4_invariant, P)))
        expected.phases[p4].add(Transition(p4, p4, p4_invariant))

        actual = build_automaton(ct)
        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")
