from typing import Iterable, TYPE_CHECKING

from pysmt.environment import Environment
from pysmt.fnode import FNode
from typing_extensions import override

from lib_core.pattern.patterns_basic import APattern
from lib_core.scopes import Scope
from lib_pea.countertrace import Countertrace, phaseT, phase, BoundTypes
from lib_pea.formal_utils import get_smt_expression

if TYPE_CHECKING:
    from lib_core.data import Formalization, Expression
    from lib_core.data import VariableCollection


class AAutomatonPattern(APattern):
    def __init__(self):
        super().__init__()
        self.group = "Abstract"

    def get_target_location(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> "FNode":
        """Return the expression identifying the successor.
        Patterns might have a different placeholder assigned for the successor, so allow resolution here"""
        return get_smt_expression(smt_env, f, vc, "S")

    def get_source_location(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> "FNode":
        return get_smt_expression(smt_env, f, vc, "R")

    def get_locations(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> set["FNode"]:
        return {self.get_source_location(smt_env, f, vc), self.get_target_location(smt_env, f, vc)}

    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        fmgr = smt_env.formula_manager
        return fmgr.TRUE()

    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        # there is no diffecrence between an event always being true versus no event being there
        fmgr = smt_env.formula_manager
        return fmgr.TRUE()

    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.NONE

    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        fmgr = smt_env.formula_manager
        return fmgr.TRUE()

    @staticmethod
    def __find_successors(
        smt_env: Environment, location: "Expression", transitions_by_source: list[tuple["Expression", "Formalization"]]
    ) -> list["Formalization"]:
        transitions = []
        fmgr = smt_env.formula_manager
        with smt_env.factory.get_solver(name="z3") as solver:
            for source, formalization in transitions_by_source:
                # Semantic check as location may be syntactically different in any reference (as it is written by hand).
                if solver.is_valid(fmgr.Iff(location, source)):
                    transitions.append(formalization)
        return transitions

    @staticmethod
    def get_hull(
        smt_env: Environment,
        formalization: "Formalization",
        other_f: Iterable["Formalization"],
        vc: "VariableCollection",
    ) -> set["Formalization"]:
        """Figure out what patterns belong to the automaton of `req`.
        This is done by building the hull of all edges.
        Locations of automata are equivalent iff they are logically equivalent expressions,
        i.e. l1 --> l2 , l3 --> l4 is part of the same automaton if  l2 <==> l3 is valid.
        """
        transitions_by_source: list[tuple["FNode", "Formalization"]] = []
        for f in other_f:
            pattern = f.scoped_pattern.get_patternish()
            if not isinstance(pattern, AAutomatonPattern):
                continue
            transitions_by_source.append((pattern.get_source_location(smt_env, f, vc), f))
        initials_by_target: list[tuple["FNode", "Formalization"]] = []
        for f in other_f:
            pattern = f.scoped_pattern.get_patternish()
            if isinstance(pattern, InitialLoc):
                initials_by_target.append((pattern.get_target_location(smt_env, f, vc), f))

        automaton = {formalization}
        queue = [formalization]
        while queue:
            pivot = queue.pop()
            pattern = pivot.scoped_pattern.get_patternish()
            successors = pattern.__find_successors(
                smt_env, pattern.get_target_location(smt_env, pivot, vc), transitions_by_source
            )
            for f in [f for f in successors if f not in automaton]:
                automaton.add(f)
                queue.append(f)
            successors.clear()

        initials = set()
        for f in automaton:
            pattern = f.scoped_pattern.get_patternish()
            initials.update(
                pattern.__find_successors(smt_env, pattern.get_source_location(smt_env, f, vc), initials_by_target)
            )
            initials.update(
                pattern.__find_successors(smt_env, pattern.get_target_location(smt_env, f, vc), initials_by_target)
            )
        automaton.update(initials)
        return automaton

    def _get_instanciated_coutertrace(
        self,
        smt_env: Environment,
        scope: str,
        this_f: "Formalization",
        other_f: list["Formalization"],
        vc: "VariableCollection",
    ) -> list[Countertrace]:
        self._fail_wrong_scope(scope)
        aut = self.get_hull(smt_env, this_f, other_f, vc)

        source_loc = self.get_source_location(smt_env, this_f, vc)
        target_loc = self.get_target_location(smt_env, this_f, vc)
        other_edges = []
        for of in aut:
            f_pat = of.scoped_pattern.get_patternish()
            if isinstance(f_pat, InitialLoc):
                continue
            if f_pat.get_source_location(smt_env, of, vc) != source_loc:
                continue
            # this will also include this transition so no special case is required
            other_edges.append(
                (
                    f_pat.get_guard(smt_env, of, vc),
                    f_pat.get_event(smt_env, of, vc),
                    f_pat.get_target_location(smt_env, of, vc),
                )
            )

        this_pat = this_f.scoped_pattern.get_patternish()
        return self._generic_transition_builder(
            smt_env,
            source_loc,
            target_loc,
            this_pat.get_event(smt_env, this_f, vc),
            this_pat.get_guard(smt_env, this_f, vc),
            other_edges,
            this_pat.get_bound_type(),
            this_pat.get_bound(smt_env, this_f, vc),
        )

    def _generic_transition_builder(
        self,
        smt_env: Environment,
        source_loc: FNode,
        target_loc: FNode,
        source_event: FNode | None = None,  # the event of the transition we want to encode here
        guard: FNode | None = None,
        outgoing_edges: list[tuple[FNode, FNode, FNode]] | None = None,  #  location, guard, event i.e. (g_j, e_j, l_)
        bound_type: BoundTypes = BoundTypes.NONE,
        time_bound: float = 0.0,
    ) -> list["Countertrace"]:
        """
        Generate different formulas to get CTs equivalent to the automaton, see (TODO: doi for the old paper)
        """
        result = []
        fmgr = smt_env.formula_manager
        tmgr = smt_env.type_manager
        outgoing_edges = [] if outgoing_edges is None else outgoing_edges
        # build formula for event is set from entry (event is true and stays true)                     (see Formula 17)
        result.append(self.__build_edge_event_locked(smt_env, source_loc, source_event, outgoing_edges))
        # build formula for event is not set (and may trigger a trainsition)                           (see Formula 18)
        if source_event != fmgr.TRUE():
            result.append(self.__build_edge_event_armed(smt_env, source_loc, source_event, outgoing_edges))
        # build formulas for time bounds in locations                                                  (see Formula 20)
        if bound_type is not BoundTypes.NONE:
            result.append(
                self._build_edge_time_bound(
                    smt_env, source_loc, target_loc, guard, bound_type, time_bound, source_event, outgoing_edges
                )
            )
        return result

    def __build_edge_event_locked(
        self,
        smt_env: Environment,
        source_loc: FNode,
        source_event: FNode | None = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] | None = None,  #  location, guard, event i.e. (g_j, e_j, l_)
    ) -> Countertrace:
        if outgoing_edges is None:
            outgoing_edges = []
        fmgr = smt_env.formula_manager
        ct_eset = Countertrace(smt_env)
        ct_eset.dc_phases.append(phaseT(smt_env))
        if not source_event:
            ct_eset.dc_phases.append(phase(smt_env, source_loc))
        else:
            ct_eset.dc_phases.append(phase(smt_env, fmgr.And(source_loc, source_event)))
        all_target_expr = []
        for g, e, l in outgoing_edges:
            if e is not fmgr.TRUE() and e == source_event:
                continue
            e_expr = e if e else fmgr.TRUE()
            all_target_expr.append(fmgr.And(l, g, e_expr))
        expr = fmgr.Not(fmgr.Or(source_loc, *all_target_expr))
        ct_eset.dc_phases.append(phase(smt_env, smt_env.simplifier.simplify(expr)))
        ct_eset.dc_phases.append(phaseT(smt_env))
        return ct_eset

    def __build_edge_event_armed(
        self,
        smt_env: Environment,
        source_loc: FNode,
        source_event: FNode | None = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] | None = None,  #  location, guard, event i.e. (g_j, e_j, l_j)
    ) -> Countertrace:
        if outgoing_edges is None:
            outgoing_edges = []
        fmgr = smt_env.formula_manager
        ct_enot = Countertrace(smt_env)
        ct_enot.dc_phases.append(phaseT(smt_env))
        ct_enot.dc_phases.append(phase(smt_env, fmgr.And(source_loc, fmgr.Not(source_event))))
        all_target_expr = []
        for g, e, l in outgoing_edges:
            all_target_expr.append(fmgr.And(l, g, e))
        expr = fmgr.Not(fmgr.Or(fmgr.And(source_loc, fmgr.Not(source_event)), *all_target_expr))
        ct_enot.dc_phases.append(phase(smt_env, smt_env.simplifier.simplify(expr)))
        ct_enot.dc_phases.append(phaseT(smt_env))
        return ct_enot

    def _build_edge_time_bound(
        self,
        smt_env: Environment,
        source_loc: FNode,
        target_loc: FNode,
        guard: FNode | None,
        bound_type: BoundTypes,
        time_bound: float,
        source_event: FNode | None = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] | None = None,  #  location, guard, event i.e. (g_j, e_j, l_j)
    ) -> Countertrace:
        if outgoing_edges is None:
            outgoing_edges = []
        # build formulas for time bounds in locations                                                  (see Formula 20)
        ct = Countertrace(smt_env)
        ct.dc_phases.append(phaseT(smt_env))
        ct.dc_phases.append(phase(smt_env, source_loc, bound_type.invert(), time_bound))
        ct.dc_phases.append(
            phase(
                smt_env,
                self._build_timed_third_phase(smt_env, source_loc, target_loc, guard, source_event, outgoing_edges),
            )
        )
        ct.dc_phases.append(phaseT(smt_env))
        return ct

    def _build_timed_third_phase(
        self,
        smt_env: Environment,
        source_loc: FNode,
        target_loc: FNode,
        guard: FNode | None,
        source_event: FNode | None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]],  #  location, guard, event i.e. (g_j, e_j, l_j)
    ) -> FNode:
        fmgr = smt_env.formula_manager
        # Violation if: the timed edge is taken and ...
        pos_f = fmgr.And(target_loc, guard, source_event)
        # ... none of the other edges could also be taken

        neg_f = fmgr.FALSE()
        for g, e, l in outgoing_edges:
            if e == source_event and g == guard and source_loc == source_loc:
                continue
            neg_f = fmgr.Or(neg_f, fmgr.And(g, e, l))
        return fmgr.And(pos_f, fmgr.Not(neg_f))

    def _fail_wrong_scope(self, scope: str):
        if scope not in [Scope.GLOBALLY.get_slug(), "Globally", Scope.GLOBALLY]:
            # TODO integrate with tag-error reporting
            raise NotImplementedError("Pattern does only exist in GLOBALLY scope")


################################################################################
#                             Available patterns                               #
################################################################################


class InitialLoc(AAutomatonPattern):
    group: str = "Automaton"
    order: int = -1
    old_names = ["InitialLoc "]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "location {R} is an initial location"
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_source_location(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> "FNode":
        # This way we can handle the edge without an exception case
        return get_smt_expression(smt_env, f, vc, "R")

    @override
    def get_target_location(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> "FNode":
        return get_smt_expression(smt_env, f, vc, "R")

    @override
    def _get_instanciated_coutertrace(
        self,
        smt_env: Environment,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        vc: "VariableCollection",
    ) -> list[Countertrace]:
        """Generate the counter-trace of the initial edges of the automaton                       (formula 16 in paper)
        e.g. [A || B]; true
        """
        self._fail_wrong_scope(scope)
        fmgr = smt_env.formula_manager
        expr = fmgr.FALSE()
        aut = self.get_hull(smt_env, f, other_f, vc)
        for t in aut:
            if not isinstance(t.scoped_pattern.get_patternish(), InitialLoc):
                continue
            expr = fmgr.Or(expr, get_smt_expression(smt_env, t, vc, "R"))
        expr = smt_env.simplifier.simplify(expr)
        ct = Countertrace(smt_env)
        ct.dc_phases.append(phase(smt_env, fmgr.Not(expr)))
        ct.dc_phases.append(phaseT(smt_env))
        return [ct]


class Transition(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 0
    old_names = ["Transition"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled ."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionG(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 1
    old_names = ["TransitionG"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled if guard {V} holds."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "V")


class TransitionLG(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 2
    old_names = ["TransitionLG"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled if guard {V} holds."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "V")

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")


class TransitionUG(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 3
    old_names = ["TransitionUG"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled if guard {V} holds."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.LESSEQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")

    @override
    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "V")


class TransitionL(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 4
    old_names = ["TransitionL"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled ."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")


class TransitionU(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 5
    old_names = ["TransitionU"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled ."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.LESSEQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")


class TransitionE(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 6
    old_names = ["TransitionE"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} if event {U} fires ."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "U")


class TransitionGE(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 7
    old_names = ["TransitionGE"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} if event {U} fires and guard {V} holds."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "V")

    @override
    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "U")


class TransitionLE(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 10
    old_names = ["TransitionLE"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} if event {U} fires ."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "U")

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")


class TransitionUE(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 11
    old_names = ["TransitionUE"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} if event {U} fires ."
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "U")

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.LESSEQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")


class TransitionLGE(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 8
    old_names = ["TransitionLGE"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "if in location {R} for at least {T} transition to {S} if event {U} fires and guard {V} holds."
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "V")

    @override
    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "U")

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")


class TransitionUGE(AAutomatonPattern):
    group: str = "Automaton"
    order: int = 9
    old_names = ["TransitionUGE"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "if in location {R} for at most {T} transition to {S} if event {U} fires and guard {V} holds."
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(smt_env, f, vc, "V")

    @override
    def get_event(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "U")

    @override
    def get_bound_type(self) -> BoundTypes:
        return BoundTypes.LESSEQUAL

    @override
    def get_bound(self, smt_env: Environment, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(smt_env, f, vc, "T")
