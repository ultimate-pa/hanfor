from dataclasses import dataclass
from fractions import Fraction

import numexpr
from pysmt.environment import Environment
from pysmt.fnode import FNode

from lib_pea.phase_sets import PhaseSets


@dataclass(unsafe_hash=True)
class Location:
    smt_env: Environment
    state_invariant: FNode = None
    clock_invariant: FNode = None
    label: str = None

    def __post_init__(self):
        if self.state_invariant is None:
            self.state_invariant = self.smt_env.formula_manager.TRUE()
        if self.clock_invariant is None:
            self.clock_invariant = self.smt_env.formula_manager.TRUE()

    def __str__(self):
        return f"{self.label:<10}: {str(self.state_invariant):<40}, {str(self.clock_invariant):<20}"

    def pretty_str(self):
        return f"Location: {self.label}\n\t  invar: {str(self.state_invariant)}\n\tc invar: {str(self.clock_invariant)}"


@dataclass
class PhaseSetsLocation(Location):
    smt_env: Environment
    label: PhaseSets = PhaseSets()

    def __eq__(self, o: "PhaseSetsLocation") -> bool:
        if not isinstance(o, PhaseSetsLocation):
            return False
        if not o.label == self.label:
            return False
        with self.smt_env.factory.get_solver(name="z3") as solver:
            return solver.is_valid(
                self.smt_env.formula_manager.Iff(o.state_invariant, self.state_invariant)
            ) and solver.is_valid(self.smt_env.formula_manager.Iff(o.clock_invariant, self.clock_invariant))

    def __hash__(self) -> int:
        return hash((self.label))

    def __str__(self) -> str:
        return f's_inv: ({self.state_invariant.serialize()}" | c_inv: "{self.clock_invariant.serialize()}" | sets: "{self.label})'

    def __repr__(self):
        return str(self.label)

    def normalize(self) -> None:
        fmgr = self.smt_env.formula_manager
        if self.state_invariant not in fmgr:
            self.state_invariant = fmgr.normalize(self.state_invariant)

        if self.clock_invariant not in fmgr:
            self.clock_invariant = fmgr.normalize(self.clock_invariant)

    def get_min_clock_bound(self) -> tuple[str, float, bool] | None:
        result = None

        atoms = self.clock_invariant.get_atoms()

        if len(atoms) <= 0:
            return result

        # TODO: Distinguish between lt and le? -> Infinite many chops.
        for atom in atoms:
            assert atom.is_lt() or atom.is_le()

            clock = str(atom.args()[0])
            bound = float(Fraction(numexpr.evaluate(str(atom.args()[1])).item()))
            is_lt_bound = atom.is_lt()

            # if result is None or (result[2] and bound < result[1]) or (not result[2] and bound <= result[1]):
            if result is None or bound < result[1]:
                result = (clock, bound, is_lt_bound)

        return result
