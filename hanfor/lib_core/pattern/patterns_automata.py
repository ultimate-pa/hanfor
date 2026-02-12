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


class AAutomatonPattern:

    def __init__(self):
        pass

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
            pattern = f.scoped_pattern.pattern.get_patternish()
            if not isinstance(pattern, AAutomatonPattern):
                continue
            transitions_by_source.append((pattern.get_source_location(f, vc), f))
        initials_by_target: list[tuple["FNode", "Formalization"]] = []
        for f in other_f:
            pattern = f.scoped_pattern.pattern.get_patternish()
            if isinstance(pattern, InitialLoc):
                initials_by_target.append((pattern.get_target_location(f, vc), f))

        automaton = {formalization}
        queue = [formalization]
        while queue:
            pivot = queue.pop()
            pattern = pivot.scoped_pattern.pattern.get_patternish()  # noqa
            successors = pattern.__find_successors(pattern.get_target_location(pivot, vc), transitions_by_source)
            for f in [f for f in successors if f not in automaton]:
                automaton.add(f)
                queue.append(f)
            successors.clear()

        initials = set()
        for f in automaton:
            pattern = f.scoped_pattern.pattern.get_patternish()
            initials.update(pattern.__find_successors(pattern.get_source_location(f, vc), initials_by_target))
            initials.update(pattern.__find_successors(pattern.get_target_location(f, vc), initials_by_target))
        automaton.update(initials)
        return automaton

    def _get_instanciated_coutertrace(
        self,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        vc: "VariableCollection",
    ) -> list[Countertrace]:
        self._fail_wrong_scope(scope)
        aut = self.get_hull(f, other_f, vc)

        source_loc = self.get_source_location(f, vc)
        other_target = []
        for f in aut:
            f_pat = f.scoped_pattern.pattern.get_patternish()
            if isinstance(f, InitialLoc):
                continue
            if f_pat.get_source_location(f, vc) != source_loc:
                continue
            # this will also include this transition so no special case is required
            other_target.append((f_pat.get_guard(f, vc), None, f_pat.get_target_location(f, vc)))
        return self._generic_transition_builder(source_loc, self.get_event(f, vc), other_target)

    def _generic_transition_builder(
        self,
        source_loc: FNode,
        source_event: FNode = None,  # the event of the transition we want to encode here
        outgoing_edges: list[tuple[FNode, FNode, FNode]] = None,  #  location, guard, event i.e. (g_j, e_j, l_)
    ) -> list["Countertrace"]:
        """Generate formulas of transitions, encoding successor, gurads and events              (see Formula 17 and 18)
        e.g. TODO
        """
        outgoing_edges = [] if outgoing_edges is None else outgoing_edges
        # build formula for event is set from entry (event is true and stays true)                     (see Formula 17)
        ct = Countertrace()
        ct.dc_phases.append(phaseT())
        if not source_event:
            ct.dc_phases.append(phase(source_loc))
        else:
            ct.dc_phases.append(phase(And(source_loc, source_event)))
        all_target_expr = []
        for g, e, l in outgoing_edges:
            if e is not TRUE() and e == source_event:
                continue
            e_expr = e if e else TRUE()
            all_target_expr.append(And(l, g, e_expr))
        expr = Not(Or(source_loc, *all_target_expr))

        ct.dc_phases.append(phase(simplify(expr)))
        ct.dc_phases.append(phaseT())
        # build formula for event is not set (and may trigger a trainsition)                           (see Formula 18)
        if source_event:
            pass  # built with event?
        return [ct]

    def _fail_wrong_scope(self, scope: str):
        if scope not in [Scope.GLOBALLY.get_slug(), "Globally", Scope.GLOBALLY]:
            # TODO integrate with tag-error reporting
            raise NotImplementedError("Pattern does only exist in GLOBALLY scope")


################################################################################
#                             Available patterns                               #
################################################################################


class InitialLoc(AAutomatonPattern, APattern):

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
            if not isinstance(t.scoped_pattern.pattern.get_patternish(), InitialLoc):
                continue
            expr = Or(expr, get_smt_expression(t, vc, "R"))
        expr = simplify(expr)
        ct = Countertrace()
        ct.dc_phases.append(phase(Not(expr)))
        ct.dc_phases.append(phaseT())
        return [ct]


class Transition(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled ."
        self.old_names = ["Transition"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionG(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 1
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")


class TransitionLG(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionLG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 2
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")


class TransitionUG(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionUG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 3
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")


class TransitionL(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled ."
        self.old_names = ["TransitionL"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Automaton"
        self.order: int = 4
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionU(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled ."
        self.old_names = ["TransitionU"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Automaton"
        self.order: int = 5
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionE(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} if event {U} fires ."
        self.old_names = ["TransitionE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 6
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionGE(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} if event {U} fires and guard {V} holds."
        self.old_names = ["TransitionGE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 7
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")


class TransitionLE(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} if event {U} fires ."
        self.old_names = ["TransitionLE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 10
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionUE(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} if event {U} fires ."
        self.old_names = ["TransitionUE"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 11
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionLGE(AAutomatonPattern, APattern):

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

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")


class TransitionUGE(AAutomatonPattern, APattern):

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

    def get_guard(self, f: "Formalization", vc: "VariableCollection") -> FNode:
        # Just see non-guarded edges as true
        return get_smt_expression(f, vc, "V")
