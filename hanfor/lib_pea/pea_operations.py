from collections import defaultdict
from typing import Union, TYPE_CHECKING

from pysmt.environment import Environment
from pysmt.fnode import FNode
from pysmt.formula import FormulaManager
from pysmt.solvers.z3 import Z3Solver
from pysmt.walkers import IdentityDagWalker

from lib_pea.location import Location
from lib_pea.transition import Transition

if TYPE_CHECKING:
    from lib_pea.pea import Pea


class PeaOperationsMixin:

    OP_TOKEN = 1

    def intersect(self: Union["Pea", "PeaOperationsMixin"], other: "Pea", smt_env: Environment, solver) -> "Pea":
        """Naiive implementation of PEA intersection for building small examples"""
        from lib_pea.pea import Pea

        PeaOperationsMixin.OP_TOKEN += 2  # Some way to add unuiqe stuff to each pea
        # TODO Clock substitutions
        self_clocks = {c: f"{c}.{PeaOperationsMixin.OP_TOKEN-1}" for c in self.clocks}
        other_clocks = {c: f"{c}.{PeaOperationsMixin.OP_TOKEN}" for c in other.clocks}
        result = Pea(smt_env)
        locations = PeaOperationsMixin.__union_locations(
            smt_env, self.locations(), other.locations(), self_clocks, other_clocks, smt_env.formula_manager, solver
        )
        result.transitions = PeaOperationsMixin.__union_transitions(
            smt_env,
            self.transitions,
            other.transitions,
            locations,
            self_clocks,
            other_clocks,
            smt_env.formula_manager,
            solver,
        )
        result.clocks = set(self_clocks.values()) | set(other_clocks.values())
        # TODO: Minimize away all false edges and locations
        return result

    @staticmethod
    def __union_locations(
        smt_env: Environment,
        self_locs: set[Location],
        other_locs: set[Location],
        self_clocks: dict[str, str],
        other_clocks: dict[str, str],
        fm: FormulaManager,
        solver: Z3Solver,
    ) -> dict[tuple[Location, Location], Location]:
        result = dict()
        for sl in self_locs:
            for ol in other_locs:
                if not sl or not ol:
                    continue  # Cant combine an initial edge with a non-initnial edge
                ul = Location(smt_env,
                    state_invariant=PeaOperationsMixin.__conjunct_builder(
                        smt_env, sl.state_invariant, ol.state_invariant, self_clocks, other_clocks, fm, solver
                    ),
                    clock_invariant=PeaOperationsMixin.__conjunct_builder(
                        smt_env, sl.clock_invariant, ol.clock_invariant, self_clocks, other_clocks, fm, solver
                    ),
                    label=f"{sl.label}+{ol.label}",
                )
                if ul.state_invariant is fm.FALSE() or ul.clock_invariant is fm.FALSE():
                    continue
                result[(sl, ol)] = ul
        return result

    @staticmethod
    def __union_transitions(
        smt_env: Environment,
        self_transitions: defaultdict[Location, set[Transition]],
        other_transitions: defaultdict[Location, set[Transition]],
        locations: dict[tuple[Location, Location], Location],
        self_clocks: dict[str, str],
        other_clocks: dict[str, str],
        fm: FormulaManager,
        solver: Z3Solver,
    ) -> defaultdict[Location, set[Transition]]:
        result = defaultdict(set)
        for (self_loc, other_loc), union_loc in locations.items():
            for st in self_transitions[self_loc]:
                for ot in other_transitions[other_loc]:
                    if (st.dst, ot.dst) not in locations:
                        continue
                    ut = Transition(
                        smt_env,
                        src=union_loc,
                        dst=locations[(st.dst, ot.dst)],
                        guard=PeaOperationsMixin.__conjunct_builder(
                            smt_env, st.guard, ot.guard, self_clocks, other_clocks, fm, solver
                        ),
                        resets=frozenset({self_clocks[c] for c in st.resets} | {other_clocks[c] for c in ot.resets}),
                    )
                    if ut.guard is fm.FALSE():
                        continue
                    result[union_loc].add(ut)
        # Build initial trainsitions
        for si in self_transitions[None]:
            for oi in self_transitions[None]:
                if (si.dst, oi.dst) not in locations:
                    continue
                ut = Transition(
                    smt_env,
                    src=None,
                    dst=locations[(si.dst, oi.dst)],
                    guard=PeaOperationsMixin.__conjunct_builder(
                        smt_env, si.guard, oi.guard, self_clocks, other_clocks, fm, solver
                    ),
                    resets=frozenset(),
                )
                if ut.guard is fm.FALSE():
                    continue
                result[None].add(ut)
        return result

    @staticmethod
    def __conjunct_builder(
        smt_env: Environment,
        self_junct: FNode,
        other_junct: FNode,
        self_clocks: dict[str, str],
        other_clocks: dict[str, str],
        fm: FormulaManager,
        solver: Z3Solver,
    ):
        """Just conjuct the two Fnodes, but make clocks unique before"""
        self_junct = Renamer(self_clocks, fm).walk(self_junct)
        other_junct = Renamer(other_clocks, fm).walk(other_junct)
        g = fm.And(self_junct, other_junct)
        if solver.is_unsat(g):
            return fm.FALSE()
        g = smt_env.simplifier.simplify(g)
        return g


class Renamer(IdentityDagWalker):
    def __init__(
        self,
        renaming_dict: dict,
        fm: FormulaManager,
    ):
        IdentityDagWalker.__init__(self)
        self.renaming_dict = renaming_dict
        self.fm = fm

    def walk_symbol(self, formula, args, **kwargs):
        # lambda s: Symbol("renamed_" + s.symbol_name(), s.symbol_type())
        if name := formula.symbol_name in self.renaming_dict:
            return self.fm.Symbol(self.renaming_dict[name], formula.symbol_type())
        return formula
