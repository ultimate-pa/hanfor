from dataclasses import dataclass
from typing import Union

from pysmt.environment import Environment
from pysmt.fnode import FNode

from lib_pea.location import PhaseSetsLocation, Location


@dataclass(unsafe_hash=True)
class Transition:
    smt_env: Environment
    src: Union[None, Location] = None
    dst: Location = None
    guard: FNode = None
    resets: frozenset[str] = frozenset()

    def __post_init__(self):
        if not self.guard:
            self.guard = self.smt_env.formula_manager.TRUE()

    def __str__(self):
        return (
            f"{self.src.label if self.src else 'init':>15} --- {str(self.guard):<30} ({str(self.resets):>5})"
            f" ---> {self.dst.label:<15}"
        )

    def pretty_str(self):
        return (
            f"Transition: {self.src.label if self.src else 'init'}  ---> {self.dst.label}\n"
            f"\t guard: {str(self.guard)}\n\tresets: {str(self.resets)}"
        )


@dataclass
class PhaseSetsTransition(Transition):
    src: PhaseSetsLocation | None = None
    dst: PhaseSetsLocation = None

    def __eq__(self, o: "PhaseSetsTransition") -> bool:
        if not isinstance(o, PhaseSetsTransition):
            return False
        if not (o.src == self.src and o.dst == self.dst and o.resets == self.resets):
            return False
        with self.smt_env.factory.get_solver(name="z3") as solver:
            return solver.is_valid(self.smt_env.formula_manager.Iff(o.guard, self.guard))

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

    def normalize(self) -> None:
        fmgr = self.smt_env.formula_manager
        if self.src is not None:
            self.src.normalize()

        if self.dst is not None:
            self.dst.normalize()

        if self.guard not in fmgr:
            self.guard = fmgr.normalize(self.guard)
