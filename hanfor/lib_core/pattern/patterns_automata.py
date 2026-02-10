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

    def get_target_location(self, f: "Formalization", var_collection: "VariableCollection") -> "FNode":
        """Return the expression identifying the successor.
        Patterns might have a different placeholder assigned for the successor, so allow resolution here"""
        return get_smt_expression(f, var_collection, "S")

    def get_source_location(self, f: "Formalization", var_collection: "VariableCollection") -> "FNode":
        return get_smt_expression(f, var_collection, "R")

    def get_locations(self, f: "Formalization", var_collection: "VariableCollection"):
        return {self.get_source_location(f, var_collection), self.get_target_location(f, var_collection)}

    def get_guard(self) -> FNode:
        # Just see non-guarded edges as true
        return TRUE()

    def get_event(self) -> FNode:
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
        formalization: "Formalization", other_f: Iterable["Formalization"], var_collection: "VariableCollection"
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
            transitions_by_source.append((pattern.get_source_location(f, var_collection), f))
        initials_by_target: list[tuple["FNode", "Formalization"]] = []
        for f in other_f:
            pattern = f.scoped_pattern.pattern.get_patternish()
            if isinstance(pattern, InitialLoc):
                initials_by_target.append((pattern.get_target_location(f, var_collection), f))

        automaton = {formalization}
        queue = [formalization]
        while queue:
            pivot = queue.pop()
            pattern = pivot.scoped_pattern.pattern.get_patternish()  # noqa
            successors = pattern.__find_successors(
                pattern.get_target_location(pivot, var_collection), transitions_by_source
            )
            for f in [f for f in successors if f not in automaton]:
                automaton.add(f)
                queue.append(f)
            successors.clear()

        initials = set()
        for f in automaton:
            pattern = f.scoped_pattern.pattern.get_patternish()
            initials.update(
                pattern.__find_successors(pattern.get_source_location(f, var_collection), initials_by_target)
            )
            initials.update(
                pattern.__find_successors(pattern.get_target_location(f, var_collection), initials_by_target)
            )
        automaton.update(initials)
        return automaton

    def _generic_transition_builder(
        self,
        source_loc: FNode,
        all_target_loc: list[tuple[FNode, FNode, FNode]] = [],  #  location, guard, event i.e. (l_j, g_j, e_j)
        # TODO: fix to immutable something
        event: FNode = None,
    ) -> list["Countertrace"]:
        # TODO: rewrite this as "per locaiton":
        ## sig: transition_builder(loc, transition_patterns) -> CT
        ### get location
        ### collect all edges of the locations over their rejspective "gimme ... s"
        ### assemble the formula
        # Now only for the simplest of transitiosn :)
        ct = Countertrace()
        ct.dc_phases.append(phaseT())
        if not event:
            ct.dc_phases.append(phase(source_loc))
            all_target_expr = []
            for l, g, e in all_target_loc:
                g_exp = g if g else TRUE()
                e_expr = e if e else TRUE()
                all_target_expr.append(And(l, g_exp, e_expr))
            expr = Not(Or(source_loc, *all_target_expr))
        else:
            pass  # built with event?
        ct.dc_phases.append(phase(simplify(expr)))
        ct.dc_phases.append(phaseT())
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
    def get_source_location(self, f: "Formalization", var_collection: "VariableCollection") -> "FNode":
        # This way we can handle the edge without an exception case
        return get_smt_expression(f, var_collection, "R")

    @override
    def get_target_location(self, f: "Formalization", var_collection: "VariableCollection") -> "FNode":
        return get_smt_expression(f, var_collection, "R")

    @override
    def _get_instanciated_coutertrace(
        self,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        variable_collection: "VariableCollection",
    ) -> list[Countertrace]:
        self._fail_wrong_scope(scope)
        expr = FALSE()
        aut = self.get_hull(f, other_f, variable_collection)
        for t in aut:
            if not isinstance(t.scoped_pattern.pattern.get_patternish(), InitialLoc):
                continue
            expr = Or(expr, get_smt_expression(t, variable_collection, "R"))
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

    @override
    def _get_instanciated_coutertrace(
        self,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        variable_collection: "VariableCollection",
    ) -> list[Countertrace]:
        self._fail_wrong_scope(scope)
        aut = self.get_hull(f, other_f, variable_collection)

        source_loc = self.get_source_location(f, variable_collection)
        other_target = []
        for f in aut:
            f_pat = f.scoped_pattern.pattern.get_patternish()
            if isinstance(f, InitialLoc):
                continue
            if f_pat.get_source_location(f, variable_collection) != source_loc:
                continue
            # this will also include this transition so no special case is required
            other_target.append((f_pat.get_target_location(f, variable_collection), None, None))
        return self._generic_transition_builder(source_loc, other_target)


class TransitionG(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} then transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 1
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionLG(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionLG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 2
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionUG(AAutomatonPattern, APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled if guard {V} holds."
        self.old_names = ["TransitionUG"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "V": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 3
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}


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
