from typing import Iterable, TYPE_CHECKING

from pysmt.fnode import FNode
from pysmt.shortcuts import Iff, Not, is_valid, FALSE, Or, And, simplify, TRUE
from typing_extensions import override

from lib_core.pattern.patterns_basic import APattern
from lib_core.scopes import Scope
from lib_pea.countertrace import Countertrace, phaseT, phase
from lib_pea.formal_utils import get_smt_expression

if TYPE_CHECKING:
    from lib_core.data import Formalization, Expression
    from lib_core.data import VariableCollection


SOLVER_NAME = "z3"
LOGIC = "UFLIRA"


class AAutomatonPattern(APattern):
    def __init__(self):
        super().__init__()
        self.group = "Abstract"

    def get_target_location(self, f: "Formalization", vc: "VariableCollection") -> "FNode":
        """Return the expression identifying the successor.
        Patterns might have a different placeholder assigned for the successor, so allow resolution here"""
        return get_smt_expression(f, vc, "S")

    def get_source_location(self, f: "Formalization", vc: "VariableCollection") -> "FNode":
        return get_smt_expression(f, vc, "R")

    def get_locations(self, f: "Formalization", vc: "VariableCollection") -> set["FNode"]:
        return {self.get_source_location(f, vc), self.get_target_location(f, vc)}

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return TRUE()

    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # there is no diffecrence between an event always being true versus no event being there
        return TRUE()

    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.NONE

    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return TRUE()

    @staticmethod
    def __find_successors(
        location: "Expression", transitions_by_source: list[tuple["Expression", "Formalization"]]
    ) -> list["Formalization"]:
        transitions = []
        for source, formalization in transitions_by_source:
            # Semantic check as location may be syntactically different in any reference (as it is written by hand).
            if is_valid(Iff(location, source)):
                transitions.append(formalization)
        return transitions

    @staticmethod
    def get_hull(
        formalization: "Formalization", other_f: Iterable["Formalization"], vc: "VariableCollection"
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
            transitions_by_source.append((pattern.get_source_location(f, vc), f))
        initials_by_target: list[tuple["FNode", "Formalization"]] = []
        for f in other_f:
            pattern = f.scoped_pattern.get_patternish()
            if isinstance(pattern, InitialLoc):
                initials_by_target.append((pattern.get_target_location(f, vc), f))

        automaton = {formalization}
        queue = [formalization]
        while queue:
            pivot = queue.pop()
            pattern = pivot.scoped_pattern.get_patternish()  # noqa
            successors = pattern.__find_successors(pattern.get_target_location(pivot, vc), transitions_by_source)
            for f in [f for f in successors if f not in automaton]:
                automaton.add(f)
                queue.append(f)
            successors.clear()

        initials = set()
        for f in automaton:
            pattern = f.scoped_pattern.get_patternish()
            initials.update(pattern.__find_successors(pattern.get_source_location(f, vc), initials_by_target))
            initials.update(pattern.__find_successors(pattern.get_target_location(f, vc), initials_by_target))
        automaton.update(initials)
        return automaton

    def _get_instanciated_coutertrace(
        self,
        scope: str,
        this_f: "Formalization",
        other_f: list["Formalization"],
        vc: "VariableCollection",
    ) -> list[Countertrace]:
        self._fail_wrong_scope(scope)
        aut = self.get_hull(this_f, other_f, vc)

        source_loc = self.get_source_location(this_f, vc)
        target_loc = self.get_target_location(this_f, vc)
        other_edges = []
        for of in aut:
            f_pat = of.scoped_pattern.get_patternish()
            if isinstance(f_pat, InitialLoc):
                continue
            if f_pat.get_source_location(of, vc) != source_loc:
                continue
            # this will also include this transition so no special case is required
            other_edges.append((f_pat.get_guard(of, vc), f_pat.get_event(of, vc), f_pat.get_target_location(of, vc)))

        this_pat = this_f.scoped_pattern.get_patternish()
        return self._generic_transition_builder(
            source_loc,
            target_loc,
            this_pat.get_event(this_f, vc),
            this_pat.get_guard(this_f, vc),
            other_edges,
            this_pat.get_bound_type(),
            this_pat.get_bound(this_f, vc),
        )

    def _generic_transition_builder(
        self,
        source_loc: FNode,
        target_loc: FNode,
        source_event: FNode = None,  # the event of the transition we want to encode here
        guard: FNode = None,
        outgoing_edges: list[tuple[FNode, FNode, FNode]] = None,  #  location, guard, event i.e. (g_j, e_j, l_)
        bound_type: Countertrace.BoundTypes = Countertrace.BoundTypes.NONE,
        time_bound: float = 0.0,
    ) -> list["Countertrace"]:
        """
        Generate different formulas to get CTs equivalent to the automaton, see (TODO: doi for the old paper)
        """
        result = []
        outgoing_edges = [] if outgoing_edges is None else outgoing_edges
        # build formula for event is set from entry (event is true and stays true)                     (see Formula 17)
        result.append(self.__build_edge_event_locked(source_loc, source_event, outgoing_edges))
        # build formula for event is not set (and may trigger a trainsition)                           (see Formula 18)
        if source_event != TRUE():
            result.append(self.__build_edge_event_armed(source_loc, source_event, outgoing_edges))
        # build formulas for time bounds in locations                                                  (see Formula 20)
        if bound_type is not Countertrace.BoundTypes.NONE:
            result.append(
                self._build_edge_time_bound(
                    source_loc, target_loc, guard, bound_type, time_bound, source_event, outgoing_edges
                )
            )
        return result

    def __build_edge_event_locked(
        self,
        source_loc: FNode,
        source_event: FNode = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] = None,  #  location, guard, event i.e. (g_j, e_j, l_)
    ) -> Countertrace:
        ct_eset = Countertrace()
        ct_eset.dc_phases.append(phaseT())
        if not source_event:
            ct_eset.dc_phases.append(phase(source_loc))
        else:
            ct_eset.dc_phases.append(phase(And(source_loc, source_event)))
        all_target_expr = []
        for g, e, l in outgoing_edges:
            if e is not TRUE() and e == source_event:
                continue
            e_expr = e if e else TRUE()
            all_target_expr.append(And(l, g, e_expr))
        expr = Not(Or(source_loc, *all_target_expr))
        ct_eset.dc_phases.append(phase(simplify(expr)))
        ct_eset.dc_phases.append(phaseT())
        return ct_eset

    def __build_edge_event_armed(
        self,
        source_loc: FNode,
        source_event: FNode = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] = None,  #  location, guard, event i.e. (g_j, e_j, l_j)
    ) -> Countertrace:
        ct_enot = Countertrace()
        ct_enot.dc_phases.append(phaseT())
        ct_enot.dc_phases.append(phase(And(source_loc, Not(source_event))))
        all_target_expr = []
        for g, e, l in outgoing_edges:
            all_target_expr.append(And(l, g, e))
        expr = Not(Or(And(source_loc, Not(source_event)), *all_target_expr))
        ct_enot.dc_phases.append(phase(simplify(expr)))
        ct_enot.dc_phases.append(phaseT())
        return ct_enot

    def _build_edge_time_bound(
        self,
        source_loc: FNode,
        target_loc: FNode,
        guard: FNode,
        bound_type: Countertrace.BoundTypes,
        time_bound: float,
        source_event: FNode = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] = None,  #  location, guard, event i.e. (g_j, e_j, l_j)
    ) -> Countertrace:
        # build formulas for time bounds in locations                                                  (see Formula 20)
        ct = Countertrace()
        ct.dc_phases.append(phaseT())
        ct.dc_phases.append(phase(source_loc, bound_type.invert(), time_bound))
        ct.dc_phases.append(
            phase(self._build_timed_third_phase(source_loc, target_loc, guard, source_event, outgoing_edges))
        )
        ct.dc_phases.append(phaseT())
        return ct

    def _build_timed_third_phase(
        self,
        source_loc: FNode,
        target_loc: FNode,
        guard: FNode,
        source_event: FNode,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]],  #  location, guard, event i.e. (g_j, e_j, l_j)
    ) -> FNode:
        # Violation if: the timed edge is taken and ...
        pos_f = And(target_loc, guard, source_event)
        # ... none of the other edges could also be taken
        neg_f = FALSE()
        for g, e, l in outgoing_edges:
            if e == source_event and g == guard and source_loc == source_loc:
                continue
            neg_f = Or(neg_f, And(g, e, l))
        return And(pos_f, Not(neg_f))

    def _fail_wrong_scope(self, scope: str):
        if scope not in [Scope.GLOBALLY.get_slug(), "Globally", Scope.GLOBALLY]:
            # TODO integrate with tag-error reporting
            raise NotImplementedError("Pattern does only exist in GLOBALLY scope")


################################################################################
#                             Available patterns                               #
################################################################################


class InitialLoc(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "location {R} is an initial location"
        self.old_names = ["InitialLoc "]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = -1
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_source_location(self, f: "Formalization", vc: "VariableCollection") -> "FNode":
        # This way we can handle the edge without an exception case
        return get_smt_expression(f, vc, "R")

    @override
    def get_target_location(self, f: "Formalization", vc: "VariableCollection") -> "FNode":
        return get_smt_expression(f, vc, "R")

    @override
    def _get_instanciated_coutertrace(
        self,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        vc: "VariableCollection",
    ) -> list[Countertrace]:
        """Generate the counter-trace of the initial edges of the automaton                       (formula 16 in paper)
        e.g. [A || B]; true
        """
        self._fail_wrong_scope(scope)
        expr = FALSE()
        aut = self.get_hull(f, other_f, vc)
        for t in aut:
            if not isinstance(t.scoped_pattern.get_patternish(), InitialLoc):
                continue
            expr = Or(expr, get_smt_expression(t, vc, "R"))
        expr = simplify(expr)
        ct = Countertrace()
        ct.dc_phases.append(phase(Not(expr)))
        ct.dc_phases.append(phaseT())
        return [ct]


class Transition(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled ."
        self.old_names = ["Transition"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionG(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 1
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "V")


class TransitionLG(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionLG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 2
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "V")

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")


class TransitionUG(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionUG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 3
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.LESSEQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")

    @override
    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "V")


class TransitionL(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled ."
        self.old_names = ["TransitionL"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Automaton"
        self.order: int = 4
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")


class TransitionU(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled ."
        self.old_names = ["TransitionU"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Automaton"
        self.order: int = 5
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.LESSEQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")


class TransitionE(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} if event {U} fires ."
        self.old_names = ["TransitionE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 6
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "U")


class TransitionGE(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} if event {U} fires and guard {V} holds."
        self.old_names = ["TransitionGE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 7
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "V")

    @override
    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "U")


class TransitionLE(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} if event {U} fires ."
        self.old_names = ["TransitionLE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 10
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "U")

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")


class TransitionUE(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} if event {U} fires ."
        self.old_names = ["TransitionUE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 11
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "U")

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.LESSEQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")


class TransitionLGE(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "if in location {R} for at least {T} transition to {S} if event {U} fires and guard {V} holds."
        )
        self.old_names = ["TransitionLGE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 8
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "V")

    @override
    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "U")

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.GREATEREQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")


class TransitionUGE(AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "if in location {R} for at most {T} transition to {S} if event {U} fires and guard {V} holds."
        )
        self.old_names = ["TransitionUGE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 9
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @override
    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")

    @override
    def get_event(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "U")

    @override
    def get_bound_type(self) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.LESSEQUAL

    @override
    def get_bound(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        return get_smt_expression(f, vc, "T")
