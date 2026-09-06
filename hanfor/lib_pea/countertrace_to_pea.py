from pysmt.environment import Environment
from pysmt.fnode import FNode
from z3 import Then, Tactic, With

from lib_pea.countertrace import Countertrace, BoundTypes
from lib_pea.location import PhaseSetsLocation
from lib_pea.pea import PhaseSetsPea
from lib_pea.phase_sets import PhaseSets
from lib_pea.transition import PhaseSetsTransition
from lib_pea.utils import substitute_free_variables


class PeaBuilder:

    def __init__(self, smt_env: Environment):
        self.__smt_env = smt_env
        self.__fmgr = self.__smt_env.formula_manager
        self.__tmgr = self.__smt_env.type_manager
        self.__solver = self.__smt_env.factory.Solver(name="z3")

    def build_automaton(self, ct: Countertrace, cp: str = "c") -> PhaseSetsPea:
        pea = PhaseSetsPea(self.__smt_env, ct)
        visited, pending = set(), set()
        init = True

        while pending or init:
            if init:
                p = PhaseSets()
                src = None
            else:
                p = pending.pop()
                visited.add(p)
                src = PhaseSetsLocation(
                    self.__smt_env, self.compute_state_invariant(ct, p), self.compute_clock_invariant(ct, p, cp), p
                )

            enter, keep = self.compute_enter_keep(ct, p, init, cp)
            successors = self.build_successors(0, p, PhaseSets(), set(), self.__fmgr.TRUE(), ct, enter, keep, cp)

            for s in successors:
                dst = PhaseSetsLocation(
                    self.__smt_env,
                    self.compute_state_invariant(ct, s[0]),
                    self.compute_clock_invariant(ct, s[0], cp),
                    s[0],
                )

                if s[0] not in visited.union(pending):
                    pending.add(s[0])

                pea.add_transition(PhaseSetsTransition(self.__smt_env, src, dst, s[1], frozenset(s[2])))

            init = False

        return pea

    def compute_state_invariant(self, ct: Countertrace, p: PhaseSets) -> FNode:
        inactive = {*range(len(ct.dc_phases))} - p.active

        result = self.__fmgr.And(
            *[ct.dc_phases[i].invariant for i in p.active],
            *[
                self.__fmgr.Not(ct.dc_phases[i].invariant)
                for i in inactive
                if self.can_seep(p, i) == self.__fmgr.TRUE()
            ],
        )
        return result

    def compute_clock_invariant(self, ct: Countertrace, p: PhaseSets, cp: str) -> FNode:
        result = []

        # TODO: check this
        for i in p.active:
            lt_args = [self.__fmgr.Symbol(cp + str(i), self.__tmgr.REAL()), ct.dc_phases[i].bound]

            if (i in p.wait) and (i in p.gteq and i == len(ct.dc_phases) - 2):
                result.append(self.__fmgr.LT(*lt_args))

            if (i in p.wait) and not (i in p.gteq and i == len(ct.dc_phases) - 2):
                result.append(self.__fmgr.LE(*lt_args))

            if not (i in p.wait) and (ct.dc_phases[i].is_upper_bound() and self.can_seep(p, i) == self.__fmgr.FALSE()):
                result.append(self.__fmgr.LE(*lt_args))

        return self.__fmgr.And(result)

    def build_successors(
        self,
        i: int,
        p: PhaseSets,
        p_: PhaseSets,
        resets: set[str],
        guard: FNode,
        ct: Countertrace,
        enter: dict[int, FNode],
        keep: dict[int, FNode],
        cp: str,
    ) -> list[tuple[PhaseSets, FNode, set[str]]]:
        result = []
        guard = self.simplify_with_z3(guard)

        # Terminate if guard is unsatisfiable.
        if guard != self.__fmgr.TRUE() and (guard == self.__fmgr.FALSE() or not self.__solver.is_sat(guard)):
            return []

        # Check if successor and guard are complete.
        if i >= len(ct.dc_phases):
            # Add successor if last phase is not included.
            if i - 1 not in p_.active:
                return [(p_, guard, resets)]

            return []

        # TODO: Primed vars are not needed.
        # inv = substitute_free_variables(ct.dc_phases[i].invariant)
        seep = self.__fmgr.And(self.can_seep(p_, i), ct.dc_phases[i].invariant)

        # Case 1: i not in p_.active
        result.extend(
            self.build_successors(
                i + 1,
                p,
                p_,
                resets,
                self.__fmgr.And(guard, self.__fmgr.Not(self.__fmgr.Or(enter[i], keep[i], seep))),
                ct,
                enter,
                keep,
                cp,
            )
        )

        # Case 2: i in p_.active
        guard = self.__fmgr.And(guard, self.__fmgr.Or(enter[i], keep[i], seep))

        if ct.dc_phases[i].is_lower_bound():
            # Case 2a: clock i in resets
            if ct.dc_phases[i].bound_type == BoundTypes.GREATEREQUAL:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_gteq(i),
                        resets.union({cp + str(i)}),
                        self.__fmgr.And(guard, self.__fmgr.Not(keep[i]), enter[i]),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )

                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_wait(i),
                        resets.union({cp + str(i)}),
                        self.__fmgr.And(guard, self.__fmgr.Not(keep[i]), self.__fmgr.Not(enter[i])),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )
            else:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_wait(i),
                        resets.union({cp + str(i)}),
                        self.__fmgr.And(guard, self.__fmgr.Not(keep[i])),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )

            # Case 2b: clock i not in resets
            if i in p.wait:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_gteq(i) if i in p.gteq else p_.add_wait(i),
                        resets,
                        self.__fmgr.And(
                            guard,
                            keep[i],
                            self.__fmgr.LT(self.__fmgr.Symbol(cp + str(i), self.__tmgr.REAL()), ct.dc_phases[i].bound),
                        ),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )

                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_active(i),
                        resets,
                        self.__fmgr.And(
                            guard,
                            keep[i],
                            self.__fmgr.GE(self.__fmgr.Symbol(cp + str(i), self.__tmgr.REAL()), ct.dc_phases[i].bound),
                        ),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )
            else:
                result.extend(
                    self.build_successors(
                        i + 1, p, p_.add_active(i), resets, self.__fmgr.And(guard, keep[i]), ct, enter, keep, cp
                    )
                )

        elif ct.dc_phases[i].is_upper_bound() and self.can_seep(p_, i) == self.__fmgr.FALSE():
            # Case 2c: clock i in resets
            if ct.dc_phases[i].bound_type == BoundTypes.LESS:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_less(i),
                        resets.union({cp + str(i)}),
                        self.__fmgr.And(guard, enter[i] or self.can_seep(p, i)),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )
            else:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_less(i),
                        resets.union({cp + str(i)}),
                        self.__fmgr.And(guard, self.__fmgr.Not(enter[i]), self.can_seep(p, i)),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )

                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_active(i),
                        resets.union({cp + str(i)}),
                        self.__fmgr.And(guard, enter[i]),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )

            # Case 2e: clock i not in resets
            if i in p.less:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_less(i),
                        resets,
                        self.__fmgr.And(guard, self.__fmgr.Not(enter[i]), self.__fmgr.Not(self.can_seep(p, i))),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )
            else:
                result.extend(
                    self.build_successors(
                        i + 1,
                        p,
                        p_.add_active(i),
                        resets,
                        self.__fmgr.And(guard, self.__fmgr.Not(enter[i]), self.__fmgr.Not(self.can_seep(p, i))),
                        ct,
                        enter,
                        keep,
                        cp,
                    )
                )

        else:
            # i in p_.active
            result.extend(self.build_successors(i + 1, p, p_.add_active(i), resets, guard, ct, enter, keep, cp))

        return result

    def compute_enter_keep(
        self, ct: Countertrace, p: PhaseSets, init: bool, cp: str
    ) -> tuple[dict[int, FNode], dict[int, FNode]]:
        enter_, keep_ = {}, {}

        if init:
            for i in range(-1, len(ct.dc_phases)):
                inv = substitute_free_variables(self.__smt_env, ct.dc_phases[i].invariant)
                enter_[i] = (
                    self.__fmgr.TRUE()
                    if i < 0
                    else self.__fmgr.And(
                        enter_[i - 1],
                        self.__fmgr.TRUE() if ct.dc_phases[i - 1].allow_empty else self.__fmgr.FALSE(),
                        inv,
                    )
                )
                # enter_[i] = TRUE() if i < 0 else And(
                #   enter_[i - 1],
                #   TRUE() if ct.dc_phases[i - 1].allow_empty else FALSE(),
                #   ct.dc_phases[i].invariant)
                keep_[i] = self.__fmgr.FALSE()
        else:
            for i in range(len(ct.dc_phases)):
                enter_[i] = self.enter(ct, p, i, cp)
                keep_[i] = self.keep(ct, p, i, cp)

        return enter_, keep_

    def enter(self, ct: Countertrace, p: PhaseSets, i: int, cp: str) -> FNode:
        inv = substitute_free_variables(self.__smt_env, ct.dc_phases[i].invariant)
        return self.__fmgr.And(
            self.complete(ct, p, i - 1, cp), inv
        )  # return And(complete(ct, p, i - 1), ct.dc_phases[i].invariant)

    def seep(self, ct: Countertrace, p: PhaseSets, i: int) -> FNode:
        inv = substitute_free_variables(self.__smt_env, ct.dc_phases[i].invariant)
        return self.__fmgr.And(self.can_seep(p, i), inv)  # return And(can_seep(p, i), ct.dc_phases[i].invariant)

    def keep(self, ct: Countertrace, p: PhaseSets, i: int, cp: str) -> FNode:
        inv = substitute_free_variables(self.__smt_env, ct.dc_phases[i].invariant)
        return self.__fmgr.And(
            self.__fmgr.TRUE() if i in p.active else self.__fmgr.FALSE(),
            inv,
            (
                self.__fmgr.LT(self.__fmgr.Symbol(cp + str(i), self.__tmgr.REAL()), ct.dc_phases[i].bound)
                if ct.dc_phases[i].is_upper_bound() and self.can_seep(p, i) == self.__fmgr.FALSE()
                else self.__fmgr.TRUE()
            ),
        )

    def complete(self, ct: Countertrace, p: PhaseSets, i: int, cp: str) -> FNode:
        result = self.__fmgr.TRUE() if i in p.active else self.__fmgr.FALSE()

        if i in p.wait:
            result = self.__fmgr.And(
                result,
                (
                    self.__fmgr.GE(self.__fmgr.Symbol(cp + str(i), self.__tmgr.REAL()), ct.dc_phases[i].bound)
                    if i in p.gteq
                    else self.__fmgr.FALSE()
                ),
            )
        else:
            result = self.__fmgr.And(
                result,
                (
                    self.__fmgr.LT(self.__fmgr.Symbol(cp + str(i), self.__tmgr.REAL()), ct.dc_phases[i].bound)
                    if i in p.less
                    else self.__fmgr.TRUE()
                ),
            )

        if i > 0 and ct.dc_phases[i].allow_empty:
            result = self.__fmgr.Or(result, self.complete(ct, p, i - 1, cp))

        return result

    def can_seep(self, p: PhaseSets, i: int) -> FNode:
        return self.__fmgr.TRUE() if i - 1 in p.active.difference(p.wait) else self.__fmgr.FALSE()

    def simplify_with_z3(self, f: FNode) -> FNode:
        tactic = Then(With(Tactic("simplify"), elim_and=True), Tactic("propagate-values"))
        result = tactic(self.__solver.converter.convert(f)).as_expr()
        result = self.__solver.converter.back(result)

        # TODO: Implement this in a testcase.
        # assert is_valid(Iff(f, result)), f"Failed to simplify: {f} is not equivalent to {result}"

        return result
