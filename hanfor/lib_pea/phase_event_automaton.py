from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction

from pysmt.fnode import FNode
from pysmt.formula import FormulaManager
from pysmt.shortcuts import (
    TRUE,
    is_valid,
    Iff,
    get_env,
)
from lib_pea.countertrace import Countertrace
from req_simulator.utils import SOLVER_NAME, LOGIC
from reqtransformer import Pickleable, Requirement, Formalization


@dataclass(frozen=True)
class Sets:
    gteq: frozenset[int] = frozenset()
    wait: frozenset[int] = frozenset()
    less: frozenset[int] = frozenset()
    active: frozenset[int] = frozenset()

    def __str__(self) -> str:
        result = ""

        for i in self.active:
            result += str(i)
            result += (
                "ᴳ"
                if i in self.gteq
                else "ᵂ"
                if i in self.wait
                else "ᴸ"
                if i in self.less
                else ""
            )

        return result

    def is_empty(self) -> bool:
        return (
            len(self.gteq) == 0
            and len(self.wait) == 0
            and len(self.less) == 0
            and len(self.active) == 0
        )

    def add_gteq(self, i: int) -> "Sets":
        return Sets(
            self.gteq.union({i}),
            self.wait.union({i}),
            self.less.copy(),
            self.active.union({i}),
        )

    def add_wait(self, i: int) -> "Sets":
        return Sets(
            self.gteq.copy(),
            self.wait.union({i}),
            self.less.copy(),
            self.active.union({i}),
        )

    def add_less(self, i: int) -> "Sets":
        return Sets(
            self.gteq.copy(),
            self.wait.copy(),
            self.less.union({i}),
            self.active.union({i}),
        )

    def add_active(self, i: int) -> "Sets":
        return Sets(
            self.gteq.copy(), self.wait.copy(), self.less.copy(), self.active.union({i})
        )


@dataclass()
class Phase:
    state_invariant: FNode = TRUE()
    clock_invariant: FNode = TRUE()
    sets: Sets() = Sets()

    def __eq__(self, o: "Phase") -> bool:
        return (
            isinstance(o, Phase)
            and o.sets == self.sets
            and is_valid(
                Iff(o.state_invariant, self.state_invariant),
                solver_name=SOLVER_NAME,
                logic=LOGIC,
            )
            and is_valid(
                Iff(o.clock_invariant, self.clock_invariant),
                solver_name=SOLVER_NAME,
                logic=LOGIC,
            )
        )

    def __hash__(self) -> int:
        return hash((self.sets))

    def __str__(self) -> str:
        return f's_inv: "{self.state_invariant.serialize()}" | c_inv: "{self.clock_invariant.serialize()}" | sets: "{self.sets}"'

    def __repr__(self):
        return str(self)

    def normalize(self, formula_manager: FormulaManager) -> None:
        if self.state_invariant not in formula_manager:
            self.state_invariant = formula_manager.normalize(self.state_invariant)

        if self.clock_invariant not in formula_manager:
            self.clock_invariant = formula_manager.normalize(self.clock_invariant)

    def get_min_clock_bound(self) -> tuple[str, float, bool] | None:
        result = None

        atoms = self.clock_invariant.get_atoms()

        if len(atoms) <= 0:
            return result

        # TODO: Distinguish between lt and le? -> Infinite many chops.
        for atom in atoms:
            assert atom.is_lt() or atom.is_le()

            clock = str(atom.args()[0])
            bound = float(Fraction(str(atom.args()[1])))
            is_lt_bound = atom.is_lt()

            # if result is None or (result[2] and bound < result[1]) or (not result[2] and bound <= result[1]):
            if result is None or bound < result[1]:
                result = (clock, bound, is_lt_bound)

        return result


@dataclass()
class Transition:
    src: Phase = None
    dst: Phase = None
    guard: FNode = TRUE()
    resets: frozenset[str] = frozenset()

    def __eq__(self, o: "Transition") -> bool:
        return (
            isinstance(o, Transition)
            and o.src == self.src
            and o.dst == self.dst
            and o.resets == self.resets
            and is_valid(Iff(o.guard, self.guard), solver_name=SOLVER_NAME, logic=LOGIC)
        )

    def __hash__(self) -> int:
        return hash((self.src, self.dst, self.resets))

    def __str__(self) -> str:
        return 'src: "%s" | dst: "%s" | guard: "%s" | resets: "%s"' % (
            None if self.src is None else self.src.sets,
            self.dst.sets,
            self.guard.serialize(),
            {*self.resets} if self.resets else "{}",
        )

    def __repr__(self):
        return str(self)

    def normalize(self, formula_manager: FormulaManager) -> None:
        if self.src is not None:
            self.src.normalize(formula_manager)

        if self.dst is not None:
            self.dst.normalize(formula_manager)

        if self.guard not in formula_manager:
            self.guard = formula_manager.normalize(self.guard)


class PhaseEventAutomaton(Pickleable):
    def __init__(self, countertrace: Countertrace = None, path: str = None):
        # TODO: Rename to transitions
        self.phases: defaultdict[Phase, set[Transition]] = defaultdict(set)
        self.countertrace: Countertrace = countertrace
        self.clocks: set[str] = set()
        self.requirement: Requirement = None
        self.formalization: Formalization = None
        self.countertrace_id: int = None

        super().__init__(path)

    def __eq__(self, o: "PhaseEventAutomaton") -> bool:
        return isinstance(o, PhaseEventAutomaton) and o.phases == self.phases

    @classmethod
    def load(cls, path: str) -> "PhaseEventAutomaton":
        pea = super().load(path)
        pea.normalize(get_env().formula_manager)

        return pea

    def normalize(self, formula_manager: FormulaManager) -> None:
        self.countertrace.normalize(formula_manager)

        for transitions in self.phases.values():
            for transition in transitions:
                transition.normalize(formula_manager)

    def add_transition(self, transition: Transition) -> None:
        if transition in self.phases[transition.src]:
            raise ValueError("Transition already exists in this phase event automaton.")

        self.clocks |= transition.resets
        self.phases[transition.src].add(transition)
