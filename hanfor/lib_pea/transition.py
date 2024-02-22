from dataclasses import dataclass

from pysmt.fnode import FNode
from pysmt.formula import FormulaManager
from pysmt.shortcuts import TRUE, is_valid, Iff

from lib_pea.location import PhaseSetsLocation, Location
from lib_pea.config import SOLVER_NAME, LOGIC


@dataclass
class Transition:
    src: Location = None
    dst: Location = None
    guard: FNode = TRUE()
    resets: frozenset[str] = frozenset()


@dataclass
class PhaseSetsTransition(Transition):
    src: PhaseSetsLocation = None
    dst: PhaseSetsLocation = None

    def __eq__(self, o: "PhaseSetsTransition") -> bool:
        return (
            isinstance(o, PhaseSetsTransition)
            and o.src == self.src
            and o.dst == self.dst
            and o.resets == self.resets
            and is_valid(Iff(o.guard, self.guard), solver_name=SOLVER_NAME, logic=LOGIC)
        )

    def __hash__(self) -> int:
        return hash((self.src, self.dst, self.resets))

    def __str__(self) -> str:
        return 'src: "%s" | dst: "%s" | guard: "%s" | resets: "%s"' % (
            None if self.src is None else self.src,
            self.dst,
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
