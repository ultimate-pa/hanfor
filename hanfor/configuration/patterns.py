from linecache import cache
from typing import Union

################################################################################
#                               Miscellaneous                                  #
################################################################################
# Additional static terms to be included into the autocomplete field.

VARIABLE_AUTOCOMPLETE_EXTENSION = ["abs()"]


class APattern:

    def __init__(self):
        self.pattern_text: str = "is an empty Pattern"
        self.old_name: Union[str, None] = None
        self.env: dict[str, list[str]] = {}
        self.group: str = "Empty"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {}

    def get_text(self):
        pass

    def get_instanciation(self, expressions):
        """inserts expressions into the pattern text and returns the fully assembled pattern instanciation"""
        pass

    def get_countertraces(self, scope):
        return self.countertraces[scope]

    def has_countertraces(self, scope: str):
        return scope in self.countertraces and self.countertraces[scope]

    @classmethod
    def get_patterns(cls) -> dict[str, "APattern"]:
        return {t.__name__: t() for t in APattern.__subclasses__()}

    @classmethod
    def get_pattern(cls, name: str) -> "APattern":
        # TODO: search in old names for compatibility reasons
        if name in APattern.get_patterns():
            return cls.get_patterns()[name]
        by_old_name = {p.old_name: p for p in cls.get_patterns().values()}
        if name in by_old_name:
            return by_old_name[name]
        raise KeyError(name)

    @classmethod
    def to_frontent_dict(cls) -> dict:
        result = dict()
        for name, pattern in APattern.get_patterns().items():
            result[name] = {
                "env": pattern.env,
                "countertraces": pattern.countertraces,
            }
        return result


class AAutomatonPattern:

    def __init__(self):
        pass

    @staticmethod
    def get_hulls():
        # TODO figure out which requirements belongs to what automaton
        pass

    def get_formulas(self):
        # TODO use formulas from paper to build formulas for any automaton pattern
        pass


################################################################################
#                             Available patterns                               #
################################################################################


class NotFormalizable(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "no pattern set"
        self.old_name = "Plumbing"
        self.env: dict[str, list[str]] = {}
        self.group: str = "not_formalizable"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class Response(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that if {R} holds then {S} eventually holds"
        self.old_name = "Response"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Order"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true"],
            "AFTER": [],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": [],
        }


class ResponseChain12(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}"
        )
        self.old_name = "ResponseChain1-2"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 2
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = (
            "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, where {U} does not hold between {S} and {T}"
        )
        self.old_name = "ConstrainedChain"
        self.env: dict[str, list[str]] = {"U": ["bool"], "R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 4
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = "it is always the case that if {R} holds then {S} previously held"
        self.old_name = "Precedence"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Order"
        self.order: int = 4
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!S⌉;⌈R⌉;true"],
            "BEFORE": ["⌈(!P && !S)⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!S⌉;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true"],
        }


class PrecedenceChain21(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds then {S} previously held and was preceded by {T}"
        )
        self.old_name = "PrecedenceChain2-1"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 5
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = (
            "it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held"
        )
        self.old_name = "PrecedenceChain1-2"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Order"
        self.order: int = 6
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BEFORE": ["⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true"],
        }


class Universality(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that {R} holds"
        self.old_name = "Universality"
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true"],
        }


class UniversalityDelay(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that {R} holds after at most {S} time units"
        self.old_name = "UniversalityDelay"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 5
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉ ∧ ℓ ≥ S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true"],
        }


class ExistenceBoundU(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "transitions to states in which {R} holds occur at most twice"
        self.old_name = "BoundedExistence"
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 3
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = "it is always the case that if {R} holds, then {S} holds as well"
        self.old_name = "Invariant"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 2
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈(R && !S)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true"],
        }


class Absence(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is never the case that {R} holds"
        self.old_name = "Absence"
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Occurence"
        self.order: int = 4
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true"],
        }


class ResponseDelay(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that if {R} holds, then {S} holds after at most {T} time units"
        self.old_name = "BoundedResponse"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        }


class ReccurrenceBound(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that {R} holds at least every {S} time units"
        self.old_name = "BoundedRecurrence"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉ ∧ ℓ > S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;true"],
        }


class DurationBoundU(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, it holds for less than {S} time units"
        )
        self.old_name = "MaxDuration"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;true"],
        }


class ResponseBoundL12(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units"
        )
        self.old_name = "TimeConstrainedMinDuration"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && T)⌉ ∧ ℓ <₀ U;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true"],
        }


class InvarianceBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that if {R} holds, then {S} holds for at least {T} time units"
        self.old_name = "BoundedInvariance"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true"],
        }


class ResponseBoundL1(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards"
        )
        self.old_name = "TimeConstrainedInvariant"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;true"],
        }


class DurationBoundL(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, it holds for at least {S} time units"
        )
        self.old_name = "MinDuration"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;true"],
        }


class ResponseDelayBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} time units"
        )
        self.old_name = "ConstrainedTimedExistence"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = (
            "it is always the case that after {R} holds for at least {S} time units and {T} holds, then {U} holds"
        )
        self.old_name = "BndTriggeredEntryConditionPattern"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (R && (T && !U)))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true"],
        }


class TriggerResponseDelayBoundL1(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that after {R} holds for at least {S}  time units and {T} holds, then {U} holds after at most {V}  time units"
        )
        self.old_name = "BndTriggeredEntryConditionPatternDelayed"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"], "V": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units"
        )
        self.old_name = "EdgeResponsePatternDelayed"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        }


class EdgeResponseBoundL2(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds for at least {T} time units"
        )
        self.old_name = "BndEdgeResponsePattern"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = (
            "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units for at least {U} time units"
        )
        self.old_name = "BndEdgeResponsePatternDelayed"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
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
        self.pattern_text: str = (
            "it is always the case that once {R} becomes satisfied and holds for at most {S} time units, then {T} holds  afterwards"
        )
        self.old_name = "BndEdgeResponsePatternTU "
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self.group: str = "Real-time"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (!R && !T))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;true"],
        }


class Initialization(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that initially {R} holds"
        self.old_name = "Initialization "
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Order"
        self.order: int = 6
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["⌈!R⌉;true"],
            "BEFORE": ["⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !R)⌉;true"],
        }


class Persistence(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that if {R} holds, then it holds persistently"
        self.old_name = "Persistence"
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Order"
        self.order: int = 7
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R⌉;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;true"],
        }


class InvarianceDelay(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds, then {S} holds as well after at most {T} time units"
        )
        self.old_name = "InvarianceDelay"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["real"]}
        self.group: str = "Real-time"
        self.order: int = 10
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": ["true;⌈R && S⌉;⌈R && !S⌉;true", "true;⌈R && !S⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class InitialLoc(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "location {R} is an initial location"
        self.old_name = "InitialLoc "
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = -1
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class Toggle1(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "it is always the case that if {R} holds then {S} toggles {T}"
        self.old_name = "Toggle1"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class Toggle2(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later"
        )
        self.old_name = "Toggle2"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"], "U": ["real"]}
        self.group: str = "Legacy"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class BndEntryConditionPattern(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that after {R} holds for at least {S}  time units, then {T} holds"
        )
        self.old_name = "BndEntryConditionPattern"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["real"], "T": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class ResponseChain21(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "it is always the case that if {R} holds and is succeeded by {S}, then {T} eventually holds after {S}"
        )
        self.old_name = "ResponseChain2-1"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 1
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class Existence(APattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "{R} eventually holds"
        self.old_name = "Existence"
        self.env: dict[str, list[str]] = {"R": ["bool"]}
        self.group: str = "Legacy"
        self.order: int = 1
        self.countertraces: dict[str, list[str]] = {
            "GLOBALLY": [],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        }


class Transition(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} then transition to {S} is enabled ."
        self.old_name = "Transition"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"]}
        self.group: str = "Automaton"
        self.order: int = 0
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionG(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} then transition to {S} is enabled if guard {V} holds."
        self.old_name = "TransitionG"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": "bool"}
        self.group: str = "Automaton"
        self.order: int = 1
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionLG(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled if guard {V} holds."
        self.old_name = "TransitionLG"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real", "V": "bool"}
        self.group: str = "Automaton"
        self.order: int = 2
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionUG(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled if guard {V} holds."
        self.old_name = "TransitionUG"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real", "V": "bool"}
        self.group: str = "Automaton"
        self.order: int = 3
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionL(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} for at least {T} transition to {S} is enabled ."
        self.old_name = "TransitionL"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real"}
        self.group: str = "Automaton"
        self.order: int = 4
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionU(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} for at most {T} transition to {S} is enabled ."
        self.old_name = "TransitionU"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real"}
        self.group: str = "Automaton"
        self.order: int = 5
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionE(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} then transition to {S} if event {U} fires ."
        self.old_name = "TransitionE"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "U": "bool"}
        self.group: str = "Automaton"
        self.order: int = 6
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionGE(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} then transition to {S} if event {U} fires and guard {V} holds."
        self.old_name = "TransitionGE"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "V": "bool", "U": "bool"}
        self.group: str = "Automaton"
        self.order: int = 7
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionLGE(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "if in location {R} for at least {T} transition to {S} if event {U} fires and guard {V} holds."
        )
        self.old_name = "TransitionLGE"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real", "V": "bool", "U": "bool"}
        self.group: str = "Automaton"
        self.order: int = 8
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionUGE(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = (
            "if in location {R} for at most {T} transition to {S} if event {U} fires and guard {V} holds."
        )
        self.old_name = "TransitionUGE"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real", "V": "bool", "U": "bool"}
        self.group: str = "Automaton"
        self.order: int = 9
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionLE(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} for at least {T} transition to {S} if event {U} fires ."
        self.old_name = "TransitionLE"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real", "U": "bool"}
        self.group: str = "Automaton"
        self.order: int = 10
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}


class TransitionUE(APattern, AAutomatonPattern):

    def __init__(self):
        super().__init__()
        self.pattern_text: str = "if in location {R} for at most {T} transition to {S} if event {U} fires ."
        self.old_name = "TransitionUE"
        self.env: dict[str, list[str]] = {"R": ["bool"], "S": ["bool"], "T": "real", "U": "bool"}
        self.group: str = "Automaton"
        self.order: int = 11
        self.countertraces: dict[str, list[str]] = {"GLOBALLY": []}
