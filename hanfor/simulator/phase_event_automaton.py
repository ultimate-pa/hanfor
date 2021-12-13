from __future__ import annotations

import time
from dataclasses import dataclass

from pysmt.fnode import FNode
from pysmt.shortcuts import TRUE, And, FALSE, Or, Not, Symbol, LT, GE, LE, is_valid, Iff, Solver, is_sat
from pysmt.typing import INT

from simulator.counter_trace import CounterTrace

SOLVER_NAME = 'cvc4'
SOLVER = Solver(name=SOLVER_NAME)


@dataclass(frozen=True)
class Sets:
    gteq: frozenset[int] = frozenset()
    wait: frozenset[int] = frozenset()
    less: frozenset[int] = frozenset()
    active: frozenset[int] = frozenset()

    def __str__(self) -> str:
        return "gteq = %s, wait = %s, less = %s, active = %s" % (
            {*self.gteq} if self.gteq else {}, {*self.wait} if self.wait else {}, {*self.less} if self.less else {},
            {*self.active} if self.active else {})

    def is_empty(self) -> bool:
        return len(self.gteq) == 0 and len(self.wait) == 0 and len(self.less) == 0 and len(self.active) == 0

    def add_gteq(self, i: int) -> Sets:
        return Sets(self.gteq.union({i}), self.wait.union({i}), self.less.copy(), self.active.union({i}))

    def add_wait(self, i: int) -> Sets:
        return Sets(self.gteq.copy(), self.wait.union({i}), self.less.copy(), self.active.union({i}))

    def add_less(self, i: int) -> Sets:
        return Sets(self.gteq.copy(), self.wait.copy(), self.less.union({i}), self.active.union({i}))

    def add_active(self, i: int) -> Sets:
        return Sets(self.gteq.copy(), self.wait.copy(), self.less.copy(), self.active.union({i}))


@dataclass(eq=False, frozen=True)
class Phase:
    state_invariant: FNode = TRUE()
    clock_invariant: FNode = TRUE()
    sets: Sets() = Sets()

    def __eq__(self, o: Phase) -> bool:
        return isinstance(o, Phase) and o.sets == self.sets and \
               is_valid(Iff(o.state_invariant, self.state_invariant), solver_name=SOLVER_NAME) and \
               is_valid(Iff(o.clock_invariant, self.clock_invariant), solver_name=SOLVER_NAME)

    def __str__(self) -> str:
        return 'state_invariant: "%s" | clock_invariant: "%s" | sets: "%s"' % (
            self.state_invariant, self.clock_invariant, self.sets)

    @staticmethod
    def compute_state_invariant(ct: CounterTrace, p: Sets) -> FNode:
        inactive = {*range(len(ct.dc_phases))} - p.active

        result = And(*[ct.dc_phases[i].invariant for i in p.active],
                     *[Not(ct.dc_phases[i].invariant) for i in inactive if can_seep(p, i) == TRUE()])

        return result.simplify()

    @staticmethod
    def compute_clock_invariant(ct: CounterTrace, p: Sets) -> FNode:
        result = And(LE(Symbol('c' + str(i), INT), ct.dc_phases[i].bound) for i in p.active if
                     i in p.wait or ct.dc_phases[i].is_upper_bound() and can_seep(p, i) == FALSE())

        return result.simplify()


@dataclass(eq=False, frozen=True)
class Transition:
    src: Phase = None
    dst: Phase = None
    guard: FNode = TRUE()
    resets: frozenset[str] = frozenset()

    def __eq__(self, o: Transition) -> bool:
        return isinstance(o, Transition) and o.src == self.src and o.dst == self.dst and o.resets == self.resets and \
               is_valid(Iff(o.guard, self.guard), solver_name=SOLVER_NAME)

    def __str__(self) -> str:
        return 'src: "%s" | dst: "%s" | guard: "%s" | resets: "%s"' % (self.src, self.dst, self.guard, self.resets)


class PhaseEventAutomaton:
    def __init__(self):
        self.init_phases: list[Phase] = []
        self.phases: list[Phase] = []
        self.init_transitions: list[Transition] = []
        self.transitions: list[Transition] = []

    def __eq__(self, o: PhaseEventAutomaton) -> bool:
        return isinstance(o, PhaseEventAutomaton) and self.compare(o.phases, self.phases) and \
               self.compare(o.transitions, self.transitions)

    @staticmethod
    def compare(l1, l2):
        l1 = list(l1)
        try:
            for i in l2:
                l1.remove(i)
        except ValueError:
            return False
        return not l1

    def add_phase(self, phase: Phase, init: bool = False):
        self.init_phases.append(phase) if init else self.phases.append(phase)
        #self.phases.append(phase)
        #return len(self.phases) - 1

    def add_transition(self, transition: Transition, init: bool) -> None:
        self.init_transitions.append(transition) if init else self.transitions.append(transition)
        #self.transitions.append(transition)


def build_automaton(ct: CounterTrace) -> PhaseEventAutomaton:
    t = time.perf_counter()

    pea = PhaseEventAutomaton()
    #indices = {}
    visited, pending = set(), set()
    init = True

    while pending or init:
        if init:
            p = Sets()
            #indices[p] = -1
        else:
            p = pending.pop()
            visited.add(p)

        enter, keep = compute_enter_keep(ct, p, init)
        successors = build_successors(0, p, Sets(), set(), TRUE(), ct, enter, keep)

        for s in successors:
            src = None if init else Phase(Phase.compute_state_invariant(ct, p), Phase.compute_clock_invariant(ct, p), p)
            dst = Phase(Phase.compute_state_invariant(ct, s[0]), Phase.compute_clock_invariant(ct, s[0]), s[0])

            if s[0] not in visited.union(pending):
                pea.add_phase(dst, init)
                pending.add(s[0])

            pea.add_transition(Transition(src, dst, s[1], frozenset(s[2])), init)

        init = False

    print('TIME: %0.4f ms' % ((time.perf_counter() - t) * 1000))
    return pea


cache = {}


def build_successors(i: int, p: Sets, p_: Sets, resets: set[str], guard: FNode, ct: CounterTrace,
                     enter: dict[int, FNode], keep: dict[int, FNode]) -> list[tuple[Sets, FNode, set[str]]]:
    result = []
    guard = guard.simplify()

    # Abort if guard is not satisfiable.
    if guard != TRUE() and (guard == FALSE() or not is_sat(guard, solver_name=SOLVER_NAME)):
        return []

    # Check if successor and guard are complete.
    if i >= len(ct.dc_phases):
        # Add successor if last phase not included.
        if i - 1 not in p_.active:
            return [(p_, guard, resets)]

        return []

    # Seep depends on partial successor location.
    seep = And(can_seep(p_, i), ct.dc_phases[i].invariant).simplify()
    # Case 1: i not in successor.active.
    result.extend(build_successors(i + 1, p, p_, resets,
                                   And(guard, Not(enter[i]), Not(keep[i]), Not(seep)),
                                   ct, enter, keep))

    # Case 2: i in p_.active.
    guard = And(guard, Or(enter[i], keep[i], seep)).simplify()

    if ct.dc_phases[i].is_lower_bound():
        # Case 2a: clocks[i] in reset_clocks.
        if ct.dc_phases[i].bound_type == CounterTrace.BoundTypes.GREATEREQUAL:
            result.extend(build_successors(i + 1, p, p_.add_gteq(i), resets.union({'c' + str(i)}),
                                           And(guard, Not(keep[i]), enter[i]),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_wait(i), resets.union({'c' + str(i)}),
                                           And(guard, Not(keep[i]), Not(enter[i])),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_wait(i), resets.union({'c' + str(i)}),
                                           And(guard, Not(keep[i]), ct.dc_phases[i].invariant),
                                           ct, enter, keep))

        # Case 2b: clocks[i] not in reset_clocks.
        if i in p.wait:
            result.extend(build_successors(i + 1, p, p_.add_gteq(i) if i in p.gteq else p_.add_wait(i), resets,
                                           And(guard, keep[i], LT(Symbol('c' + str(i), INT), ct.dc_phases[i].bound)),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_active(i), resets,
                                           And(guard, keep[i], GE(Symbol('c' + str(i), INT), ct.dc_phases[i].bound)),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), resets,
                                           And(guard, keep[i]),
                                           ct, enter, keep))

    elif ct.dc_phases[i].is_upper_bound() and can_seep(p_, i) == FALSE():
        # Case 2c: clocks[i] in reset_clocks.
        if ct.dc_phases[i].bound_type == CounterTrace.BoundTypes.LESS:
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({'c' + str(i)}),
                                           And(guard, enter[i] or can_seep(p, i)),
                                           ct, enter, keep))
            '''
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({'c' + str(i)}),
                                           And(guard, enter[i]),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({'c' + str(i)}),
                                           And(guard, can_seep(p, i)),
                                           ct, enter, keep))
            '''
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), resets.union({'c' + str(i)}),
                                           And(guard, enter[i]),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({'c' + str(i)}),
                                           And(guard, enter[i], can_seep(p, i)),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({'c' + str(i)}),
                                           And(guard, Not(enter[i]), can_seep(p, i)),
                                           ct, enter, keep))

        # Case 2e: clocks[i] not in reset_clocks.
        if i in p.less:
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets,
                                           And(guard, Not(enter[i]), Not(can_seep(p, i))),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), resets,
                                           And(guard, Not(enter[i]), Not(can_seep(p, i))),
                                           ct, enter, keep))
    else:
        # i in p_.active.
        result.extend(build_successors(i + 1, p, p_.add_active(i), resets, guard, ct, enter, keep))

    return result


def compute_enter_keep(ct: CounterTrace, p: Sets, init: bool) -> tuple[dict[int, FNode], dict[int, FNode]]:
    enter_, keep_ = {}, {}

    if init:
        for i in range(-1, len(ct.dc_phases)):
            enter_[i] = TRUE() if i < 0 else And(enter_[i - 1], TRUE() if ct.dc_phases[i - 1].allow_empty else FALSE(),
                                                 ct.dc_phases[i].invariant).simplify()
            keep_[i] = FALSE()
    else:
        for i in range(len(ct.dc_phases)):
            enter_[i] = enter(ct, p, i)
            keep_[i] = keep(ct, p, i)

    return enter_, keep_


def enter(ct: CounterTrace, p: Sets, i: int) -> FNode:
    return And(complete(ct, p, i - 1), ct.dc_phases[i].invariant).simplify()


def seep(ct: CounterTrace, p: Sets, i: int) -> FNode:
    return And(can_seep(p, i), ct.dc_phases[i].invariant).simplify()


def keep(ct: CounterTrace, p: Sets, i: int) -> FNode:
    return And(TRUE() if i in p.active else FALSE(), ct.dc_phases[i].invariant,
               LT(Symbol('c' + str(i), INT), ct.dc_phases[i].bound)
               if ct.dc_phases[i].is_upper_bound() and can_seep(p, i) == FALSE() else TRUE()).simplify()


def complete(ct: CounterTrace, p: Sets, i: int) -> FNode:
    result = TRUE() if i in p.active else FALSE()

    if i in p.wait:
        result = And(result, GE(Symbol('c' + str(i), INT), ct.dc_phases[i].bound) if i in p.gteq else FALSE())
    else:
        result = And(result, LT(Symbol('c' + str(i), INT), ct.dc_phases[i].bound) if i in p.less else TRUE())

    if i > 0 and ct.dc_phases[i].allow_empty:
        result = Or(result, complete(ct, p, i - 1))

    return result.simplify()


def can_seep(p: Sets, i: int) -> FNode:
    return TRUE() if i - 1 in p.active.difference(p.wait) else FALSE()
