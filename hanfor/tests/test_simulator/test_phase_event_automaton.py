from unittest import TestCase

from lark.lark import Lark
from pysmt.shortcuts import Symbol, And, LT, GE, Or, LE, TRUE, Not, FALSE
from pysmt.typing import INT

from simulator.counter_trace import CounterTraceTransformer
from simulator.phase_event_automaton import build_automaton, PhaseEventAutomaton, Transition, Phase, Sets

parser = Lark.open('../../simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace', parser='lalr')


class TestPhaseEventAutomaton(TestCase):
    def test_true(self):
        expected = PhaseEventAutomaton()

        ct_str = 'true;true'
        expressions = {'P': Symbol('P'), 'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        actual = build_automaton(ct)

        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_false(self):
        expected = PhaseEventAutomaton()

        # ct0_st
        p1_invariant = TRUE()
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({})))
        expected.init_phases.append(p1)

        expected.init_transitions.append(Transition(None, p1, p1_invariant))
        expected.transitions.append(Transition(p1, p1, p1_invariant))

        ct_str = '⌈P⌉;true'
        expressions = {'P': FALSE()}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        actual = build_automaton(ct)

        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_bnd_response_pattern_ut_globally(self):
        expected = PhaseEventAutomaton()
        S, R, T, c2 = Symbol('S'), Symbol('R'), Symbol('T', INT), Symbol('c2', INT)

        # ct0_st0
        p1_invariant = Or(S, Not(R))
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        expected.init_phases.append(p1)
        # ct0_st012W
        p2_invariant = And(Not(S), R)
        p2 = Phase(p2_invariant, LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 1, 2})))
        expected.init_phases.append(p2)
        # ct0_st02W
        p3_invariant = And(Not(S), Not(R))
        p3 = Phase(p3_invariant, LE(c2, T), Sets(wait=frozenset({2}), active=frozenset({0, 2})))
        expected.phases.append(p3)

        # ct0_st0
        expected.init_transitions.append(Transition(None, p1, p1_invariant))
        expected.transitions.append(Transition(p1, p1, p1_invariant))
        expected.transitions.append(Transition(p1, p2, p2_invariant, frozenset({'c2'})))
        # ct0_st012W
        expected.init_transitions.append(Transition(None, p2, p2_invariant, frozenset({'c2'})))
        expected.transitions.append(Transition(p2, p2, And(p2_invariant, LT(c2, T))))
        expected.transitions.append(Transition(p2, p1, And(p1_invariant, S)))
        expected.transitions.append(Transition(p2, p3, And(p3_invariant, LT(c2, T))))
        # ct0_st02W
        expected.transitions.append(Transition(p3, p3, And(p3_invariant, LT(c2, T))))
        expected.transitions.append(Transition(p3, p1, And(p1_invariant, S)))
        expected.transitions.append(Transition(p3, p2, And(p2_invariant, LT(c2, T))))

        ct_str = 'true;⌈(!S && R)⌉;⌈!S⌉ ∧ ℓ > T;true'
        expressions = {'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', INT)}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        actual = build_automaton(ct)

        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")

    def test_duration_bound_l_pattern_globally(self):
        expected = PhaseEventAutomaton()
        R, T, c2 = Symbol('R'), Symbol('T', INT), Symbol('c2', INT)

        # ct0_st0
        p1_invariant = R
        p1 = Phase(p1_invariant, TRUE(), Sets(active=frozenset({0})))
        expected.init_phases.append(p1)
        # ct0_st01
        p2_invariant = Not(R)
        p2 = Phase(p2_invariant, TRUE(), Sets(active=frozenset({0, 1})))
        expected.init_phases.append(p2)
        # ct0_st02
        p3_invariant = R
        p3 = Phase(p3_invariant, LE(c2, T), Sets(less=frozenset({2}), active=frozenset({0, 2})))
        expected.phases.append(p3)

        # ct0_st0
        expected.init_transitions.append(Transition(None, p1, p1_invariant))
        expected.transitions.append(Transition(p1, p1, p1_invariant))
        expected.transitions.append(Transition(p1, p2, p2_invariant))
        # ct0_st01
        expected.init_transitions.append(Transition(None, p2, p2_invariant))
        expected.transitions.append(Transition(p2, p2, p2_invariant))
        expected.transitions.append(Transition(p2, p3, p3_invariant, frozenset({'c2'})))
        # ct0_st02
        expected.transitions.append(Transition(p3, p3, And(p3_invariant, LT(c2, T))))
        expected.transitions.append(Transition(p3, p1, And(p1_invariant, GE(c2, T))))
        expected.transitions.append(Transition(p3, p2, And(p2_invariant, Or(R, GE(c2, T)))))

        ct_str = 'true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true'
        expressions = {'R': Symbol('R'), 'T': Symbol('T', INT)}
        ct = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
        actual = build_automaton(ct)

        self.assertEqual(expected, actual, msg="Error while building phase event automaton.")