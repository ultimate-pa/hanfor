from pysmt.fnode import FNode
from pysmt.shortcuts import TRUE, And, FALSE, Or, Not, Symbol, LT, GE, LE, is_sat
from pysmt.typing import REAL

from lib_pea.countertrace import Countertrace
from lib_pea.phase_event_automaton import PhaseEventAutomaton, Sets, Phase, Transition
from lib_pea.utils import substitute_free_variables, SOLVER_NAME, LOGIC


def build_automaton(ct: Countertrace, cp: str = "c") -> PhaseEventAutomaton:
    pea = PhaseEventAutomaton(ct)
    visited, pending = set(), set()
    init = True

    while pending or init:
        if init:
            p = Sets()
            src = None
        else:
            p = pending.pop()
            visited.add(p)
            src = Phase(compute_state_invariant(ct, p), compute_clock_invariant(ct, p, cp), p)

        enter, keep = compute_enter_keep(ct, p, init, cp)
        successors = build_successors(0, p, Sets(), set(), TRUE(), ct, enter, keep, cp)

        for s in successors:
            dst = Phase(compute_state_invariant(ct, s[0]), compute_clock_invariant(ct, s[0], cp), s[0])

            if s[0] not in visited.union(pending):
                pending.add(s[0])

            pea.add_transition(Transition(src, dst, s[1], frozenset(s[2])))

        init = False

    return pea


def compute_state_invariant(ct: Countertrace, p: Sets) -> FNode:
    inactive = {*range(len(ct.dc_phases))} - p.active

    result = And(*[ct.dc_phases[i].invariant for i in p.active],
                 *[Not(ct.dc_phases[i].invariant) for i in inactive if can_seep(p, i) == TRUE()])
    return result


def compute_clock_invariant(ct: Countertrace, p: Sets, cp: str) -> FNode:
    result = []

    # TODO: check this
    for i in p.active:
        lt_args = [Symbol(cp + str(i), REAL), ct.dc_phases[i].bound]

        if (i in p.wait) and (i in p.gteq and i == len(ct.dc_phases) - 2):
            result.append(LT(*lt_args))

        if (i in p.wait) and not (i in p.gteq and i == len(ct.dc_phases) - 2):
            result.append(LE(*lt_args))

        if not (i in p.wait) and (ct.dc_phases[i].is_upper_bound() and can_seep(p, i) == FALSE()):
            result.append(LE(*lt_args))

    # result = And(LE(Symbol(cp + str(i), REAL), ct.dc_phases[i].bound) for i in p.active if
    #             i in p.wait or ct.dc_phases[i].is_upper_bound() and can_seep(p, i) == FALSE())

    return And(result)


def build_successors(i: int, p: Sets, p_: Sets, resets: set[str], guard: FNode, ct: Countertrace,
                     enter: dict[int, FNode], keep: dict[int, FNode], cp: str) -> list[tuple[Sets, FNode, set[str]]]:
    result = []
    guard = guard.simplify()

    # Terminate if guard is unsatisfiable.
    if guard != TRUE() and (guard == FALSE() or not is_sat(guard, solver_name=SOLVER_NAME, logic=LOGIC)):
        return []

    # Check if successor and guard are complete.
    if i >= len(ct.dc_phases):
        # Add successor if last phase is not included.
        if i - 1 not in p_.active:
            return [(p_, guard, resets)]

        return []

    # TODO: Primed vars are not needed.
    # inv = substitute_free_variables(ct.dc_phases[i].invariant)
    seep = And(can_seep(p_, i), ct.dc_phases[i].invariant)

    # Case 1: i not in p_.active
    result.extend(build_successors(i + 1, p, p_, resets,
                                   And(guard, Not(Or(enter[i], keep[i], seep))),
                                   ct, enter, keep, cp))

    # Case 2: i in p_.active
    guard = And(guard, Or(enter[i], keep[i], seep))

    if ct.dc_phases[i].is_lower_bound():
        # Case 2a: clock i in resets
        if ct.dc_phases[i].bound_type == Countertrace.BoundTypes.GREATEREQUAL:
            result.extend(build_successors(i + 1, p, p_.add_gteq(i), resets.union({cp + str(i)}),
                                           And(guard, Not(keep[i]), enter[i]),
                                           ct, enter, keep, cp))

            result.extend(build_successors(i + 1, p, p_.add_wait(i), resets.union({cp + str(i)}),
                                           And(guard, Not(keep[i]), Not(enter[i])),
                                           ct, enter, keep, cp))
        else:
            result.extend(build_successors(i + 1, p, p_.add_wait(i), resets.union({cp + str(i)}),
                                           And(guard, Not(keep[i])),
                                           ct, enter, keep, cp))

            # result.extend(build_successors(i + 1, p, p_.add_wait(i), resets.union({cp + str(i)}),
            #                                And(guard, Not(keep[i])), ct, enter, keep))

        # Case 2b: clock i not in resets
        if i in p.wait:
            result.extend(build_successors(i + 1, p, p_.add_gteq(i) if i in p.gteq else p_.add_wait(i), resets,
                                           And(guard, keep[i], LT(Symbol(cp + str(i), REAL), ct.dc_phases[i].bound)),
                                           ct, enter, keep, cp))

            result.extend(build_successors(i + 1, p, p_.add_active(i), resets,
                                           And(guard, keep[i], GE(Symbol(cp + str(i), REAL), ct.dc_phases[i].bound)),
                                           ct, enter, keep, cp))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), resets,
                                           And(guard, keep[i]),
                                           ct, enter, keep, cp))

    elif ct.dc_phases[i].is_upper_bound() and can_seep(p_, i) == FALSE():
        # Case 2c: clock i in resets
        if ct.dc_phases[i].bound_type == Countertrace.BoundTypes.LESS:
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({cp + str(i)}),
                                           And(guard, enter[i] or can_seep(p, i)),
                                           ct, enter, keep, cp))
            """
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({cp + str(i)}),
                                           And(guard, enter[i]),
                                           ct, enter, keep, cp))

            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({cp + str(i)}),
                                           And(guard, can_seep(p, i)),
                                           ct, enter, keep, cp))
            """
        else:
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({cp + str(i)}),
                                           And(guard, Not(enter[i]), can_seep(p, i)),
                                           ct, enter, keep, cp))

            result.extend(build_successors(i + 1, p, p_.add_active(i), resets.union({cp + str(i)}),
                                           And(guard, enter[i]),
                                           ct, enter, keep, cp))

            # result.extend(build_successors(i + 1, p, p_.add_less(i), resets.union({cp + str(i)}), # wrong
            #                               And(guard, enter[i], can_seep(p, i)),
            #                               ct, enter, keep, cp))

        # Case 2e: clock i not in resets
        if i in p.less:
            result.extend(build_successors(i + 1, p, p_.add_less(i), resets,
                                           And(guard, Not(enter[i]), Not(can_seep(p, i))),
                                           ct, enter, keep, cp))
        else:
            result.extend(build_successors(i + 1, p, p_.add_active(i), resets,
                                           And(guard, Not(enter[i]), Not(can_seep(p, i))),
                                           ct, enter, keep, cp))

    else:
        # i in p_.active
        result.extend(build_successors(i + 1, p, p_.add_active(i), resets, guard, ct, enter, keep, cp))

    return result


def compute_enter_keep(ct: Countertrace, p: Sets, init: bool, cp: str) -> tuple[dict[int, FNode], dict[int, FNode]]:
    enter_, keep_ = {}, {}

    if init:
        for i in range(-1, len(ct.dc_phases)):
            inv = substitute_free_variables(ct.dc_phases[i].invariant)
            enter_[i] = (TRUE() if i < 0 else And(enter_[i - 1],
                         TRUE() if ct.dc_phases[i - 1].allow_empty else FALSE(), inv))
            # enter_[i] = TRUE() if i < 0 else And(
            #   enter_[i - 1],
            #   TRUE() if ct.dc_phases[i - 1].allow_empty else FALSE(),
            #   ct.dc_phases[i].invariant)
            keep_[i] = FALSE()
    else:
        for i in range(len(ct.dc_phases)):
            enter_[i] = enter(ct, p, i, cp)
            keep_[i] = keep(ct, p, i, cp)

    return enter_, keep_


def enter(ct: Countertrace, p: Sets, i: int, cp: str) -> FNode:
    inv = substitute_free_variables(ct.dc_phases[i].invariant)
    return And(complete(ct, p, i - 1, cp), inv)  # return And(complete(ct, p, i - 1), ct.dc_phases[i].invariant)


def seep(ct: Countertrace, p: Sets, i: int) -> FNode:
    inv = substitute_free_variables(ct.dc_phases[i].invariant)
    return And(can_seep(p, i), inv)  # return And(can_seep(p, i), ct.dc_phases[i].invariant)


def keep(ct: Countertrace, p: Sets, i: int, cp: str) -> FNode:
    inv = substitute_free_variables(ct.dc_phases[i].invariant)
    return And(TRUE() if i in p.active else FALSE(), inv,
               LT(Symbol(cp + str(i), REAL), ct.dc_phases[i].bound)
               if ct.dc_phases[i].is_upper_bound() and can_seep(p, i) == FALSE() else TRUE())

    # return And(TRUE() if i in p.active else FALSE(), ct.dc_phases[i].invariant,
    #           LT(Symbol(cp + str(i), INT), ct.dc_phases[i].bound)
    #           if ct.dc_phases[i].is_upper_bound() and can_seep(p, i) == FALSE() else TRUE())


def complete(ct: Countertrace, p: Sets, i: int, cp: str) -> FNode:
    result = TRUE() if i in p.active else FALSE()

    if i in p.wait:
        result = And(result, GE(Symbol(cp + str(i), REAL), ct.dc_phases[i].bound) if i in p.gteq else FALSE())
    else:
        result = And(result, LT(Symbol(cp + str(i), REAL), ct.dc_phases[i].bound) if i in p.less else TRUE())

    if i > 0 and ct.dc_phases[i].allow_empty:
        result = Or(result, complete(ct, p, i - 1, cp))

    return result


def can_seep(p: Sets, i: int) -> FNode:
    return TRUE() if i - 1 in p.active.difference(p.wait) else FALSE()
