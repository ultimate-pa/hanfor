from collections import defaultdict
from functools import cache
from typing import Iterable, TYPE_CHECKING

from lark import Tree
from pysmt.fnode import FNode
from pysmt.shortcuts import Iff, Not, is_sat

from lib_core import boogie_parsing
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import CountertraceTransformer
from lib_pea.utils import get_countertrace_parser

if TYPE_CHECKING:
    from lib_core.data import Formalization, Expression
    from lib_core.data import VariableCollection


SOLVER_NAME = "z3"
LOGIC = "UFLIRA"

################################################################################
#                               Miscellaneous                                  #
################################################################################
# Additional static terms to be included into the autocomplete field.

VARIABLE_AUTOCOMPLETE_EXTENSION = ["abs()"]


class APattern:

    def __init__(self):
        self._pattern_text: str = "is an empty Pattern"
        self.old_names: list[str] = []
        self._env: dict[str, list[str]] = {}
        self.group: str = "Empty"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = defaultdict(list)

    def get_text(self):
        pass

    def get_instanciation(self, expressions):
        """inserts expressions into the pattern text and returns the fully assembled pattern instanciation"""
        pass

    def get_countertraces(self, scope: str):
        return self._countertraces[scope]

    def has_countertraces(self, scope: str):
        return scope in self._countertraces and self._countertraces[scope]

    def get_instanciated_countertraces(
        self, scope: str, expressions: dict[str, FNode], others: list["APattern"]
    ) -> list[Tree]:
        cts: list[Tree] = []
        for ct_str in self.get_countertraces(scope):
            ct_ast = get_countertrace_parser().parse(ct_str)
            cts.append(CountertraceTransformer(expressions).transform(ct_ast))
        return cts  # TODO: check that this is really a tree

    @classmethod
    @cache
    def get_patterns(cls) -> dict[str, "APattern"]:
        return {t.__name__: t() for t in APattern.__subclasses__()}

    @classmethod
    def get_pattern(cls, name: str) -> "APattern":
        # TODO: search in old names for compatibility reasons
        if name in APattern.get_patterns():
            return cls.get_patterns()[name]
        by_old_name: dict[str, APattern] = dict()
        for pattern in cls.get_patterns().values():
            by_old_name.update({old_name: pattern for old_name in pattern.old_names})
        if name in by_old_name:
            return by_old_name[name]
        raise KeyError(name)

    @classmethod
    def to_frontent_dict(cls) -> dict:
        result = dict()
        for name, pattern in APattern.get_patterns().items():
            result[name] = {
                "env": pattern._env,
                "countertraces": pattern._countertraces,
            }
        return result


class AAutomatonPattern:

    def __init__(self):
        pass

    @classmethod
    def get_target_location(cls, f: "Formalization", var_collection: "VariableCollection") -> "Expression":
        """Return the expression identifying the successor.
        Patterns might have a different placeholder assigned for the successor, so allow resolution here"""
        return cls._get_letter(f, var_collection, "S")

    @classmethod
    def get_source_location(cls, f: "Formalization", var_collection: "VariableCollection") -> "Expression":
        return cls._get_letter(f, var_collection, "R")

    @classmethod
    def _get_letter(cls, f: "Formalization", var_collection: "VariableCollection", letter: str) -> "Expression":
        # TODO: importing boogie parsing here is not nice, get this stuff into the expressions or so
        boogie_parser = boogie_parsing.get_parser_instance()
        ast = boogie_parser.parse(f.expressions_mapping[letter].raw_expression)
        return BoogiePysmtTransformer(set(var_collection.collection.values())).transform(ast)

    @classmethod
    def get_hull(
        cls, formalization: "Formalization", other_f: Iterable["Formalization"], var_collection: "VariableCollection"
    ) -> set["Formalization"]:
        """Figure out what patterns belong to the automaton of `req`.
        This is done by building the hull of all edges found until fixpoint.
        Note: a location is part of an automaton iff there is another location exactly referencing that location as successor.
        Successors where the location is a subset of another location are not regarded as this might be another automaton.
        e.g.   x > 5 ---> x <= 5  and x > 5 && turbo ----> x <= 5 && turbo are not of the same automaton.
        """
        transitions_by_source = []
        for f in other_f:
            p_class = APattern.get_pattern(f.scoped_pattern.pattern.name)
            if not isinstance(p_class, AAutomatonPattern):
                continue
            if isinstance(p_class, InitialLoc):
                # add all transtions in the right direction
                transitions_by_source.append((p_class.get_target_location(f, var_collection), f))
            else:
                # add all initial transitions in the opposite direction (as if they were sinks)
                transitions_by_source.append((p_class.get_source_location(f, var_collection), f))

        automaton = {formalization}
        queue = [formalization]
        while queue:
            pivot = queue.pop()
            pattern: AAutomatonPattern = APattern.get_pattern(pivot.scoped_pattern.pattern.name)  # noqa
            successors = cls.__find_successors(
                pattern.get_target_location(pivot, var_collection), transitions_by_source
            )
            for f in [f for f in successors if f not in automaton]:
                automaton.add(f)
                queue.append(f)
            successors.clear()
        return automaton

    @classmethod
    def __find_successors(
        cls, location: "Expression", transitions_by_source: list[tuple["Expression", "Formalization"]]
    ) -> list["Formalization"]:
        successors = []
        for source, formalization in transitions_by_source:
            # Semantic check as location may be syntactically different in any reference (as it is written by hand).
            if not is_sat(Not(Iff(location, source))):
                successors.append(formalization)
        # assert len(successors) <= 1
        return successors

    def get_formulas(self):
        # TODO use formulas from paper to build formulas for any automaton pattern
        pass


################################################################################
#                             Available patterns                               #
################################################################################


class NotFormalizable(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "no pattern set"
        self.old_names = ["Plumbing"]
        self._env: dict[str, list[str]] = {}
        self.group: str = "not_formalizable"
        self.order: int = 0


class Response(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds then {S} eventually holds"
        self.old_names = ["Response"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Order"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true"],
            "AFTER": [],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": [],
        }


class ResponseChain12(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}"
        )
        self.old_names = ["ResponseChain1-2"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 2
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true",
            ],
            "AFTER": [],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [],
        }


class ConstrainedChain(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, where {U} does not hold between {S} and {T}"
        )
        self.old_names = ["ConstrainedChain"]
        self._env: dict[str, list[str]] = {"U": ["bool"], "R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 4
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈(!P && (!T && U))⌉;⌈!P⌉;⌈(!P && T)⌉;⌈!P⌉;⌈P⌉;true",
            ],
            "AFTER": [],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈(!Q && (!T && U))⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [],
        }


class Precedence(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds then {S} previously held"
        self.old_names = ["Precedence"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Order"
        self.order: int = 4
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!S⌉;⌈R⌉;true"],
            "BEFORE": ["⌈(!P && !S)⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!S⌉;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true"],
        }


class PrecedenceChain21(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} previously held and was preceded by {T}"
        )
        self.old_names = ["PrecedenceChain2-1"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 5
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!T⌉;⌈R⌉;true", "⌈!S⌉;⌈R⌉;true", "⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true"],
            "BEFORE": [
                "⌈(!P && !T)⌉;⌈(!P && R)⌉;true",
                "⌈(!P && !S)⌉;⌈(!P && R)⌉;true",
                "⌈(!P && !T)⌉;⌈(!P && (S && !T))⌉;⌈(!P && !T)⌉;⌈(!P && (!S && T))⌉;⌈(!P && !S)⌉;⌈(!P && R)⌉;true",
            ],
            "AFTER": [
                "true;⌈P⌉;⌈!T⌉;⌈R⌉;true",
                "true;⌈P⌉;⌈!S⌉;⌈R⌉;true",
                "true;⌈P⌉;⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true",
            ],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;true",
                "true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true",
                "true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true",
            ],
        }


class PrecedenceChain12(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held"
        )
        self.old_names = ["PrecedenceChain1-2"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 6
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BEFORE": ["⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true"],
        }


class Universality(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that {R} holds"
        self.old_names = ["Universality"]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true"],
        }


class UniversalityDelay(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that {R} holds after at most {S} time units"
        self.old_names = ["UniversalityDelay"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 5
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉ ∧ ℓ ≥ S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true"],
        }


class ExistenceBoundU(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "transitions to states in which {R} holds occur at most twice"
        self.old_names = ["BoundedExistence"]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 3
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"
            ],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;true"],
        }


class Invariance(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then {S} holds as well"
        self.old_names = ["Invariant"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 2
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈(R && !S)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true"],
        }


class Absence(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is never the case that {R} holds"
        self.old_names = ["Absence"]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 4
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true"],
        }


class ResponseDelay(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then {S} holds after at most {T} time units"
        self.old_names = ["BoundedResponse"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        }


class ReccurrenceBound(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that {R} holds at least every {S} time units"
        self.old_names = ["BoundedRecurrence"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉ ∧ ℓ > S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;true"],
        }


class DurationBoundU(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, it holds for less than {S} time units"
        )
        self.old_names = ["MaxDuration"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;true"],
        }


class ResponseBoundL12(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units"
        )
        self.old_names = ["TimeConstrainedMinDuration"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && T)⌉ ∧ ℓ <₀ U;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true"],
        }


class InvarianceBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then {S} holds for at least {T} time units"
        self.old_names = ["BoundedInvariance"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true"],
        }


class ResponseBoundL1(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards"
        )
        self.old_names = ["TimeConstrainedInvariant"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;true"],
        }


class DurationBoundL(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, it holds for at least {S} time units"
        )
        self.old_names = ["MinDuration"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;true"],
        }


class ResponseDelayBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} time units"
        )
        self.old_names = ["ConstrainedTimedExistence"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;⌈!S⌉ ∧ ℓ > T;true", "true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true"],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ <₀ T;⌈(!P && S)⌉ ∧ ℓ < U;⌈(!P && !S)⌉;true",
            ],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ > T;true", "true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true",
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true",
            ],
        }


class TriggerResponseBoundL1(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that after {R} holds for at least {S} time units and {T} holds, then {U} holds"
        )
        self.old_names = ["BndTriggeredEntryConditionPattern"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (R && (T && !U)))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true"],
        }


class TriggerResponseDelayBoundL1(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that after {R} holds for at least {S}  time units and {T} holds, then {U} holds after at most {V}  time units"
        )
        self.old_names = ["BndTriggeredEntryConditionPatternDelayed"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"], "V": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;⌈!U⌉ ∧ ℓ > V;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (R && (T && !U)))⌉;⌈(!P && !U)⌉ ∧ ℓ > V;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;⌈!U⌉ ∧ ℓ > V;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;⌈(!Q && !U)⌉ ∧ ℓ > V;true;⌈Q⌉;true"
            ],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;⌈(!Q && !U)⌉ ∧ ℓ > V;true"],
        }


class EdgeResponseDelay(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units"
        )
        self.old_names = ["EdgeResponsePatternDelayed"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        }


class EdgeResponseBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds for at least {T} time units"
        )
        self.old_names = ["BndEdgeResponsePattern"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < T;⌈!S⌉;true", "true;⌈!R⌉;⌈(R && !S)⌉;true"],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && S)⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true;⌈(!P && !S)⌉;true",
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;true",
            ],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < T;⌈!S⌉;true", "true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true",
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;true",
            ],
        }


class EdgeResponseDelayBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units for at least {U} time units"
        )
        self.old_names = ["BndEdgeResponsePatternDelayed"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true", "true;⌈!R⌉;⌈R⌉;true ∧ ℓ < T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true"],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true",
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && S)⌉ ∧ ℓ < U;⌈(!P && !S)⌉;true",
            ],
            "AFTER": [
                "true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true",
                "true;⌈P⌉;true;⌈!R⌉;⌈R⌉;true ∧ ℓ < T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true",
            ],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true",
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true",
            ],
        }


class EdgeResponseBoundU1(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied and holds for at most {S} time units, then {T} holds  afterwards"
        )
        self.old_names = ["BndEdgeResponsePatternTU "]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (!R && !T))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;true"],
        }


class Initialization(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that initially {R} holds"
        self.old_names = ["Initialization "]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Order"
        self.order: int = 6
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!R⌉;true"],
            "BEFORE": ["⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !R)⌉;true"],
        }


class Persistence(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then it holds persistently"
        self.old_names = ["Persistence"]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Order"
        self.order: int = 7
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;true"],
        }


class InvarianceDelay(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds, then {S} holds as well after at most {T} time units"
        )
        self.old_names = ["InvarianceDelay"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 10
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R && S⌉;⌈R && !S⌉;true", "true;⌈R && !S⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class InitialLoc(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "location {R} is an initial location"
        self.old_names = ["InitialLoc "]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = -1
        self._countertraces: dict[str, list[str]] = {"GLOBALLY": []}

    @classmethod
    def get_source_location(cls, f: "Formalization", var_collection: "VariableCollection"):
        raise Exception("There is no source location in an initial transition. Do not access this field here.")

    @classmethod
    def get_target_location(cls, f: "Formalization", var_collection: "VariableCollection") -> "Expression":
        return cls._get_letter(f, var_collection, "R")


class Toggle1(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds then {S} toggles {T}"
        self.old_names = ["Toggle1"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 0


class Toggle2(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later"
        )
        self.old_names = ["Toggle2"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"], "U": ["real"]}
        self.group: str = "Legacy"
        self.order: int = 0


class BndEntryConditionPattern(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that after {R} holds for at least {S}  time units, then {T} holds"
        )
        self.old_names = ["BndEntryConditionPattern"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 0


class ResponseChain21(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds and is succeeded by {S}, then {T} eventually holds after {S}"
        )
        self.old_names = ["ResponseChain2-1"]
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 1


class Existence(APattern):

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "{R} eventually holds"
        self.old_names = ["Existence"]
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 1


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
