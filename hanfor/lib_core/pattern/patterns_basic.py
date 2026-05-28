from collections import defaultdict
from typing import TYPE_CHECKING

from pysmt.environment import Environment

from lib_pea.countertrace import Countertrace, CountertraceTransformer
from lib_pea.formal_utils import get_expression_mapping_smt
from lib_pea.utils import get_countertrace_parser

if TYPE_CHECKING:
    from lib_core.data import Formalization
    from lib_core.data import VariableCollection


class APattern:
    group: str = "Abstract"
    order: int = 0
    old_names: list[str] = []

    def __init__(self):
        self._pattern_text: str = "is an empty Pattern"
        self._env: dict[str, list[str]] = {}
        self._countertraces: dict[str, list[str]] = defaultdict(list)

    def get_text(self):
        return self._pattern_text

    def get_instanciation(self, expressions):
        """inserts expressions into the pattern text and returns the fully assembled pattern instanciation"""
        pass

    def get_countertraces(self, scope: str):
        return self._countertraces[scope]

    def has_countertraces(self, scope: str):
        return scope in self._countertraces and self._countertraces[scope]

    @property
    def env(self):
        return self._env

    def get_instanciated_countertraces(
        self,
        smt_env: Environment,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        variable_collection: "VariableCollection",
    ) -> list[Countertrace]:
        return self._get_instanciated_coutertrace(smt_env, scope, f, other_f, variable_collection)

    def _get_instanciated_coutertrace(
        self,
        smt_env: Environment,
        scope: str,
        f: "Formalization",
        other_f: list["Formalization"],
        variable_collection: "VariableCollection",
    ) -> list[Countertrace]:
        cts = []
        expr = get_expression_mapping_smt(smt_env, f, variable_collection)
        for ct_str in self.get_countertraces(scope):
            ct_ast = get_countertrace_parser().parse(ct_str)
            cts.append(CountertraceTransformer(smt_env, expr).transform(ct_ast))
        return cts

    @classmethod
    def get_patterns(cls) -> dict[str, type["APattern"]]:
        return {t.__name__: t for t in cls.__get_inheriting_pattern(cls) if t.group != "Abstract"}

    @classmethod
    def __get_inheriting_pattern(cls, t: type["APattern"]) -> set[type["APattern"]]:
        # noinspection PyTypeChecker
        result: set[type["APattern"]] = set(t.__subclasses__())
        for sub in t.__subclasses__():
            # noinspection PyTypeChecker
            result |= cls.__get_inheriting_pattern(sub)
        return result

    @classmethod
    def get_pattern(cls, name: str) -> type["APattern"]:
        # TODO: search in old names for compatibility reasons
        patterns = cls.get_patterns()
        if name in patterns:
            return patterns[name]
        by_old_name: dict[str, type["APattern"]] = dict()
        for pattern in cls.get_patterns().values():
            by_old_name.update({old_name: pattern for old_name in pattern.old_names})
        if name in by_old_name:
            return by_old_name[name]
        raise KeyError(name)

    @classmethod
    def to_frontent_dict(cls) -> dict:
        result = dict()
        for name, pattern in APattern.get_patterns().items():
            pattern_inst = pattern()
            result[name] = {
                "env": pattern_inst._env,
                "countertraces": pattern_inst._countertraces,
            }
        return result


class NotFormalizable(APattern):
    group: str = "not_formalizable"
    order: int = 0
    old_names = ["Plumbing"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "no pattern set"
        self._env: dict[str, list[str]] = {}


class Response(APattern):
    group: str = "Order"
    order: int = 0
    old_names = ["Response"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds then {S} eventually holds"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true"],
            "AFTER": [],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": [],
        }


class ResponseChain12(APattern):
    group: str = "Order"
    order: int = 2
    old_names = ["ResponseChain1-2"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
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
    group: str = "Order"
    order: int = 4
    old_names = ["ConstrainedChain"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, where {U} does not hold between {S} and {T}"
        )
        self._env: dict[str, list[str]] = {"U": ["bool"], "R": ["bool"], "S": ["bool"], "T": ["bool"]}
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
    group: str = "Order"
    order: int = 4
    old_names = ["Precedence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds then {S} previously held"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!S⌉;⌈R⌉;true"],
            "BEFORE": ["⌈(!P && !S)⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!S⌉;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true"],
        }


class PrecedenceChain21(APattern):
    group: str = "Order"
    order: int = 5
    old_names = ["PrecedenceChain2-1"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} previously held and was preceded by {T}"
        )

        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
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
    group: str = "Order"
    order: int = 6
    old_names = ["PrecedenceChain1-2"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held"
        )

        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}

        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BEFORE": ["⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true"],
        }


class Universality(APattern):
    group: str = "Occurence"
    order: int = 0
    old_names = ["Universality"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that {R} holds"

        self._env: dict[str, list[str]] = {"R": ["bool"]}

        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true"],
        }


class UniversalityDelay(APattern):
    group: str = "Real-time"
    order: int = 5
    old_names = ["UniversalityDelay"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that {R} holds after at most {S} time units"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉ ∧ ℓ ≥ S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true"],
        }


class ExistenceBoundU(APattern):
    group: str = "Occurence"
    order: int = 3
    old_names = ["BoundedExistence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "transitions to states in which {R} holds occur at most twice"
        self._env: dict[str, list[str]] = {"R": ["bool"]}
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
    group: str = "Occurence"
    order: int = 2
    old_names = ["Invariant"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then {S} holds as well"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈(R && !S)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true"],
        }


class Absence(APattern):
    group: str = "Occurence"
    order: int = 4
    old_names = ["Absence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is never the case that {R} holds"
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true"],
        }


class ResponseDelay(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["BoundedResponse"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then {S} holds after at most {T} time units"

        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}

        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        }


class ReccurrenceBound(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["BoundedRecurrence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that {R} holds at least every {S} time units"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉ ∧ ℓ > S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;true"],
        }


class DurationBoundU(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["MaxDuration"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, it holds for less than {S} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;true"],
        }


class ResponseBoundL12(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["TimeConstrainedMinDuration"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && T)⌉ ∧ ℓ <₀ U;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true"],
        }


class InvarianceBoundL2(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["BoundedInvariance"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then {S} holds for at least {T} time units"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true"],
        }


class ResponseBoundL1(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["TimeConstrainedInvariant"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;true"],
        }


class DurationBoundL(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["MinDuration"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, it holds for at least {S} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;true"],
        }


class ResponseDelayBoundL2(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["ConstrainedTimedExistence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]}
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
    group: str = "Real-time"
    order: int = 0
    old_names = ["BndTriggeredEntryConditionPattern"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that after {R} holds for at least {S} time units and {T} holds, then {U} holds"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (R && (T && !U)))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true"],
        }


class TriggerResponseDelayBoundL1(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["BndTriggeredEntryConditionPatternDelayed"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that after {R} holds for at least {S}  time units and {T} holds, then {U} holds after at most {V}  time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"], "V": ["real"]}
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
    group: str = "Real-time"
    order: int = 0
    old_names = ["EdgeResponsePatternDelayed"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        }


class EdgeResponseBoundL2(APattern):
    group: str = "Real-time"
    order: int = 0
    old_names = ["BndEdgeResponsePattern"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds for at least {T} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
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
    group: str = "Real-time"
    order: int = 0
    old_names = ["BndEdgeResponsePatternDelayed"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units for at least {U} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]}
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
    group: str = "Real-time"
    order: int = 0
    old_names = ["BndEdgeResponsePatternTU "]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that once {R} becomes satisfied and holds for at most {S} time units, then {T} holds  afterwards"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (!R && !T))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;true"],
        }


class Initialization(APattern):
    group: str = "Order"
    order: int = 6
    old_names = ["Initialization "]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that initially {R} holds"
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!R⌉;true"],
            "BEFORE": ["⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !R)⌉;true"],
        }


class Persistence(APattern):
    group: str = "Order"
    order: int = 7
    old_names = ["Persistence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds, then it holds persistently"
        self._env: dict[str, list[str]] = {"R": ["bool"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;true"],
        }


class ConditionalResponseBoundL1(APattern):
    group: str = "Real-time"
    order: int = 10
    old_names = ["InvarianceDelay"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds, then {S} holds as well after at most {T} time units"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self._countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R && S⌉;⌈R && !S⌉;true", "true;⌈R && !S⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class Toggle1(APattern):
    group: str = "Legacy"
    order: int = 0
    old_names = ["Toggle1"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "it is always the case that if {R} holds then {S} toggles {T}"
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}


class Toggle2(APattern):
    group: str = "Legacy"
    order: int = 0
    old_names = ["Toggle2"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"], "U": ["real"]}


class BndEntryConditionPattern(APattern):
    group: str = "Legacy"
    order: int = 0
    old_names = ["BndEntryConditionPattern"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that after {R} holds for at least {S}  time units, then {T} holds"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}


class ResponseChain21(APattern):
    group: str = "Legacy"
    order: int = 1
    old_names = ["ResponseChain2-1"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = (
            "it is always the case that if {R} holds and is succeeded by {S}, then {T} eventually holds after {S}"
        )
        self._env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}


class Existence(APattern):
    group: str = "Legacy"
    order: int = 1
    old_names = ["Existence"]

    def __init__(self):
        super().__init__()
        self._pattern_text: str = "{R} eventually holds"
        self._env: dict[str, list[str]] = {"R": ["bool"]}
