from collections import defaultdict
from typing import Union

from pysmt.fnode import FNode
from pysmt.formula import FormulaManager
from pysmt.shortcuts import FALSE, TRUE, And, Symbol, Solver, simplify
from pysmt.solvers.z3 import Z3Solver
from pysmt.walkers import IdentityDagWalker

from lib_pea.location import Location
from lib_pea.transition import Transition

SOLVER_NAME = "z3"
LOGIC = "UFLIRA"


class PeaOperationsMixin:

    OP_TOKEN = 1

    def intersect(self: Union["Pea", "PeaOperationsMixin"], other: "Pea", simplify: bool = True) -> "Pea":
        """Naiive implementation of PEA intersection for building small examples"""
        from lib_pea.pea import Pea

        PeaOperationsMixin.OP_TOKEN += 2  # Some way to add unuiqe stuff to each pea
        # TODO Clock substitutions
        self_clocks = {c: f"{c}.{PeaOperationsMixin.OP_TOKEN-1}" for c in self.clocks}
        other_clocks = {c: f"{c}.{PeaOperationsMixin.OP_TOKEN}" for c in other.clocks}
        result = Pea()
        locations = PeaOperationsMixin.__union_locations(
            self.locations(), other.locations(), self_clocks, other_clocks, simplify
        )
        result.transitions = PeaOperationsMixin.__union_transitions(
            self.transitions, other.transitions, locations, self_clocks, other_clocks, simplify
        )
        result.clocks = set(self_clocks.values()) | set(other_clocks.values())
        # TODO: Minimize away all false edges and locations
        return result

    @staticmethod
    def __union_locations(
        self_locs: set[Location],
        other_locs: set[Location],
        self_clocks: dict[str, str],
        other_clocks: dict[str, str],
        simplify: bool,
    ) -> dict[(Location, Location), Location]:
        result = dict()
        for sl in self_locs:
            for ol in other_locs:
                if not sl or not ol:
                    continue  # Cant combine an initial edge with a non-initnial edge
                ul = Location(
                    state_invariant=PeaOperationsMixin.__conjunct_builder(
                        sl.state_invariant, ol.state_invariant, self_clocks, other_clocks
                    ),
                    clock_invariant=PeaOperationsMixin.__conjunct_builder(
                        sl.clock_invariant, ol.clock_invariant, self_clocks, other_clocks
                    ),
                    label=f"{sl.label}+{ol.label}",  # TODO this is not distributive... worgs
                )
                if not simplify or ul.state_invariant is FALSE() or ul.clock_invariant is FALSE():
                    continue
                result[(sl, ol)] = ul
        return result

    @staticmethod
    def __union_transitions(
        self_transitions: defaultdict[Location, set[Transition]],
        other_transitions: defaultdict[Location, set[Transition]],
        locations: dict[(Location, Location), Location],
        self_clocks: dict[str, str],
        other_clocks: dict[str, str],
        simplify: bool,
    ) -> defaultdict[Location, set[Transition]]:
        result = defaultdict(set)
        for (self_loc, other_loc), union_loc in locations.items():
            for st in self_transitions[self_loc]:
                for ot in other_transitions[other_loc]:
                    ut = Transition(
                        src=union_loc,
                        dst=locations[(st.dst, ot.dst)],
                        guard=PeaOperationsMixin.__conjunct_builder(st.guard, ot.guard, self_clocks, other_clocks),
                        resets=frozenset({self_clocks[c] for c in st.resets} | {other_clocks[c] for c in ot.resets}),
                    )
                    if not simplify or ut.guard is FALSE():
                        continue
                    result[union_loc].add(ut)
        # Build initial trainsitions
        for si in self_transitions[None]:
            for oi in self_transitions[None]:
                ut = Transition(
                    src=None,
                    dst=locations[(si.dst, oi.dst)],
                    guard=PeaOperationsMixin.__conjunct_builder(si.guard, oi.guard, self_clocks, other_clocks),
                    resets=frozenset(),
                )
                if not simplify or ut.guard is FALSE():
                    continue
                result[None].add(ut)
        return result

    @staticmethod
    def __conjunct_builder(
        self_junct: FNode, other_junct: FNode, self_clocks: dict[str, str], other_clocks: dict[str, str]
    ):
        """Just conjuct the two Fnodes, but make clocks unique before"""
        self_junct = Renamer(self_clocks).walk(self_junct)
        other_junct = Renamer(other_clocks).walk(other_junct)
        g = And(self_junct, other_junct)
        g = simplify(g)
        return g


class Renamer(IdentityDagWalker):
    def __init__(self, renaming_dict: dict):
        IdentityDagWalker.__init__(self)
        self.renaming_dict = renaming_dict

    def walk_symbol(self, formula, args, **kwargs):
        # lambda s: Symbol("renamed_" + s.symbol_name(), s.symbol_type())
        if name := formula.symbol_name in self.renaming_dict:
            return Symbol(self.renaming_dict[name], formula.symbol_type())
        return formula
