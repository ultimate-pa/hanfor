from __future__ import annotations

from pysmt.fnode import FNode
from pysmt.shortcuts import TRUE, And, FALSE, Or, Not, Symbol, LT, GE
from pysmt.typing import INT

from simulator.counter_trace import CounterTrace


class Phase():
    def __init__(self):
        self.phase_sets: Phase.PhaseSets = Phase.PhaseSets(set(), set(), set(), set())

    def add_successor(self, guard: FNode, clocks, phase: Phase):
        raise NotImplementedError()

    class PhaseSets():
        def __init__(self, gteq: set[int] = None, wait: set[int] = None, less: set[int] = None,
                     active: set[int] = None):
            self.gteq: set[int] = set() if gteq is None else gteq
            self.wait: set[int] = set() if wait is None else wait
            self.less: set[int] = set() if less is None else less
            self.active: set[int] = set() if active is None else active

        def __eq__(self, o):
            return isinstance(o, Phase.PhaseSets) and \
                   self.gteq == o.gteq and self.wait == o.wait and self.less == o.less and self.active == o.active

        def add_gteq(self, i: int) -> Phase.PhaseSets:
            return Phase.PhaseSets(self.gteq.union({i}), self.wait.union({i}), self.less.copy(), self.active.union({i}))

        def add_wait(self, i: int) -> Phase.PhaseSets:
            return Phase.PhaseSets(self.gteq.copy(), self.wait.union({i}), self.less.copy(), self.active.union({i}))

        def add_less(self, i: int) -> Phase.PhaseSets:
            return Phase.PhaseSets(self.gteq.copy(), self.wait.copy(), self.less.union({i}), self.active.union({i}))

        def add_active(self, i: int) -> Phase.PhaseSets:
            return Phase.PhaseSets(self.gteq.copy(), self.wait.copy(), self.less.copy(), self.active.union({i}))


def build_automaton(ct: CounterTrace):
    result_init, result, visited, pending = [], [], [], []

    while pending or not result_init:
        if result_init:
            p = pending.pop()
            visited.append(p)
        else:
            p = Phase.PhaseSets()

        enter, keep = compute_enter_keep(ct, p if result_init else None)
        successors = build_successors(0, p, Phase.PhaseSets(), set(), TRUE(), ct, enter, keep)

        pending.extend([s[1] for s in successors if s[1] not in visited and s[1] not in pending])
        result.extend(successors) if result_init else result_init.extend(successors)

    return result_init, result


def build_successors(i: int, p: Phase.PhaseSets, p_: Phase.PhaseSets, reset_clocks: set[str], guard: FNode,
                     ct: CounterTrace, enter: dict[int, FNode], keep: dict[int, FNode]) \
        -> list[tuple[Phase.PhaseSets, Phase.PhaseSets, FNode, set[str]]]:
    result = []

    # Abort if guard is not satisfiable.
    if guard.simplify() == FALSE():
        return []

    # Check if successor and guard are complete.
    if i >= len(ct.dc_phases):
        # Add successor if last phase not included.
        if i - 1 not in p_.active:
            return [(p, p_, guard.simplify(), reset_clocks)]

        return []

    # Seep depends on partial successor location.
    seep = And(can_seep(p_, i), ct.dc_phases[i].invariant)
    # Case 1: i not in successor.active.
    result.extend(build_successors(i + 1, p, p_, reset_clocks,
                                   And(guard, Not(Or(enter[i], keep[i], seep))),
                                   ct, enter, keep))

    # Case 2: i in p_.active.
    guard = And(guard, Or(enter[i], keep[i], seep))

    if ct.dc_phases[i].is_lower_bound():
        # Case 2a: clocks[i] in reset_clocks.
        if ct.dc_phases[i].bound_type == CounterTrace.BoundTypes.GREATEREQUAL:
            result.extend(build_successors(i + 1, p, p_.add_gteq(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, Not(keep[i]), enter[i]),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_wait(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, Not(keep[i]), Not(enter[i])),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_wait(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, Not(keep[i]), ct.dc_phases[i].invariant),
                                           ct, enter, keep))

        # Case 2b: clocks[i] not in reset_clocks.
        if i in p.wait:
            result.extend(build_successors(i + 1, p, p_.add_gteq(i) if i in p.gteq else p_.add_wait(i), reset_clocks,
                                           And(guard, keep[i], LT(Symbol('c' + str(i), INT), ct.dc_phases[i].bound)),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_active(i), reset_clocks,
                                           And(guard, keep[i], GE(Symbol('c' + str(i), INT), ct.dc_phases[i].bound)),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), reset_clocks,
                                           And(guard, keep[i]),
                                           ct, enter, keep))

    elif ct.dc_phases[i].is_upper_bound() and can_seep(p_, i) == FALSE():
        # Case 2c: clocks[i] in reset_clocks.
        if ct.dc_phases[i].bound_type == CounterTrace.BoundTypes.LESS:
            result.extend(build_successors(i + 1, p, p_.add_less(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, enter[i]),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_less(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, can_seep(p, i)),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, enter[i]),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_less(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, enter[i], can_seep(p, i)),
                                           ct, enter, keep))

            result.extend(build_successors(i + 1, p, p_.add_less(i), reset_clocks.union({'c' + str(i)}),
                                           And(guard, Not(enter[i]), can_seep(p, i)),
                                           ct, enter, keep))

        # Case 2e: clocks[i] not in reset_clocks.
        if i in p.less:
            result.extend(build_successors(i + 1, p, p_.add_less(i), reset_clocks,
                                           And(guard, Not(enter[i]), Not(can_seep(p, i))),
                                           ct, enter, keep))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), reset_clocks,
                                           And(guard, Not(enter[i]), Not(can_seep(p, i))),
                                           ct, enter, keep))
    else:
        # i in p_.active.
        result.extend(build_successors(i + 1, p, p_.add_active(i), reset_clocks, guard, ct, enter, keep))

    return result


def compute_enter_keep(ct: CounterTrace, p: Phase.PhaseSets = None) -> tuple[dict[int, FNode], dict[int, FNode]]:
    enter_, keep_ = {}, {}

    if not p:
        for i in range(-1, len(ct.dc_phases)):
            allow_empty = TRUE() if ct.dc_phases[i - 1].allow_empty else FALSE()
            enter_[i] = TRUE() if i < 0 else And(enter_[i - 1], allow_empty, ct.dc_phases[i].invariant)
            keep_[i] = FALSE()
    else:
        for i in range(len(ct.dc_phases)):
            enter_[i] = enter(ct, p, i)
            keep_[i] = keep(ct, p, i)

    return enter_, keep_


def keep(ct: CounterTrace, p: Phase.PhaseSets, i: int) -> FNode:
    is_upper_bound = ct.dc_phases[i].bound_type == CounterTrace.BoundTypes.LESS or \
                     ct.dc_phases[i].bound_type == CounterTrace.BoundTypes.LESSEQUAL
    is_can_seep = can_seep(p, i) == FALSE()

    return And(TRUE() if i in p.active else FALSE(), ct.dc_phases[i].invariant,
               LT(Symbol('c' + str(i), INT), ct.dc_phases[i].bound) if is_upper_bound and is_can_seep else TRUE())


def enter(ct: CounterTrace, p: Phase.PhaseSets, i: int) -> FNode:
    return And(complete(ct, p, i - 1), ct.dc_phases[i].invariant)


def seep(ct: CounterTrace, p: Phase.PhaseSets, i: int) -> FNode:
    return And(can_seep(p, i), ct.dc_phases[i].invariant)


def complete(ct: CounterTrace, p: Phase.PhaseSets, i: int) -> FNode:
    result = TRUE() if i in p.active else FALSE()

    if i in p.wait:
        result = And(result, GE(Symbol('c' + str(i), INT), ct.dc_phases[i].bound) if i in p.gteq else FALSE())
    else:
        result = And(result, LT(Symbol('c' + str(i), INT), ct.dc_phases[i].bound) if i in p.less else TRUE())

    if i > 0 and ct.dc_phases[i].allow_empty:
        result = Or(result, complete(ct, p, i - 1))

    return result


def can_seep(p: Phase.PhaseSets, i: int) -> FNode:
    return TRUE() if i - 1 in p.active.difference(p.wait) else FALSE()
