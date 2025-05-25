from dataclasses import dataclass
from fractions import Fraction

from pysmt.fnode import FNode
from pysmt.formula import FormulaManager
from pysmt.shortcuts import TRUE, is_valid, Iff

from lib_pea.phase_sets import PhaseSets
from lib_pea.config import SOLVER_NAME, LOGIC
import numexpr


@dataclass
class Location:
    state_invariant: FNode = TRUE()
    clock_invariant: FNode = TRUE()
    label: str = None


@dataclass
class PhaseSetsLocation(Location):
    label: PhaseSets() = PhaseSets()

    def __eq__(self, o: "PhaseSetsLocation") -> bool:
        return (
            isinstance(o, PhaseSetsLocation)
            and o.label == self.label
            and is_valid(Iff(o.state_invariant, self.state_invariant), solver_name=SOLVER_NAME, logic=LOGIC)
            and is_valid(Iff(o.clock_invariant, self.clock_invariant), solver_name=SOLVER_NAME, logic=LOGIC)
        )

    def __hash__(self) -> int:
        return hash((self.label))

    def __str__(self) -> str:
        return f's_inv: ({self.state_invariant.serialize()}" | c_inv: "{self.clock_invariant.serialize()}" | sets: "{self.label})'

    def __repr__(self):
        return str(self.label)

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
            bound = float(Fraction(numexpr.evaluate(str(atom.args()[1])).item()))
            is_lt_bound = atom.is_lt()

            # if result is None or (result[2] and bound < result[1]) or (not result[2] and bound <= result[1]):
            if result is None or bound < result[1]:
                result = (clock, bound, is_lt_bound)

        return result
