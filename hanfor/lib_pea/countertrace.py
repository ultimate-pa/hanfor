from enum import Enum

from lark.visitors import Transformer
from pysmt.fnode import FNode
from pysmt.formula import FormulaManager
from pysmt.shortcuts import TRUE, Not, And, Or, get_free_variables


class Countertrace:
    def __init__(self, *dc_phases: "DCPhase") -> None:
        self.dc_phases: list[Countertrace.DCPhase] = [dc_phase for dc_phase in dc_phases]

    def __str__(self) -> str:
        return ";".join([str(dc_phase) for dc_phase in self.dc_phases])

    def normalize(self, formula_manager: FormulaManager) -> None:
        for dc_phase in self.dc_phases:
            dc_phase.normalize(formula_manager)

    def extract_variables(self) -> frozenset[FNode]:
        variables = set()

        for dc_phase in self.dc_phases:
            variables.update(dc_phase.extract_variables())

        return frozenset(variables)

    class BoundTypes(Enum):
        NONE = 0
        LESS = 1
        LESSEQUAL = 2
        GREATER = 3
        GREATEREQUAL = 4

    class DCPhase:
        def __init__(
            self,
            entry_events: FNode,
            invariant: FNode,
            bound_type: "Countertrace.BoundTypes",
            bound: int,
            forbid: set[str],
            allow_empty: bool,
        ) -> None:
            self.entry_events: FNode = entry_events
            self.invariant: FNode = invariant
            self.bound_type: Countertrace.BoundTypes = bound_type
            self.bound: float = bound
            self.forbid: set[str] = forbid
            self.allow_empty: bool = allow_empty

        def __str__(self, unicode: bool = True) -> str:
            result = ""

            _AND = "\u2227" if unicode else "/\\"
            _NO_EVENT = "\u229F" if unicode else "[-]"
            _EMPTY = "\u2080" if unicode else "0"
            _GEQ = "\u2265" if unicode else ">="
            _LEQ = "\u2264" if unicode else "<="
            _LCEIL = "\u2308" if unicode else "["
            _RCEIL = "\u2309" if unicode else "]"
            _ELL = "\u2113" if unicode else "L"

            result += self.entry_events.serialize() + ";" if self.entry_events != TRUE() else ""
            result += (
                self.invariant.serialize() if self.invariant == TRUE() else _LCEIL + self.invariant.serialize() + _RCEIL
            )

            for forbid in self.forbid:
                result += " " + _AND + " " + _NO_EVENT + " " + forbid

            if self.bound_type == Countertrace.BoundTypes.NONE:
                return result

            result += " " + _AND + " " + _ELL

            if self.bound_type == Countertrace.BoundTypes.LESS:
                result += " <" + _EMPTY + " " if self.allow_empty else " < "
            elif self.bound_type == Countertrace.BoundTypes.LESSEQUAL:
                result += " " + _LEQ + _EMPTY + " " if self.allow_empty else " " + _LEQ + " "
            elif self.bound_type == Countertrace.BoundTypes.GREATER:
                result += " >" + _EMPTY + " " if self.allow_empty else " > "
            elif self.bound_type == Countertrace.BoundTypes.GREATEREQUAL:
                result += " " + _GEQ + _EMPTY + " " if self.allow_empty else " " + _GEQ + " "
            else:
                raise ValueError("Unexpected value of `bound_type`: %s" % self.bound_type)

            result += str(self.bound)

            return result

        def normalize(self, formula_manager: FormulaManager) -> None:
            if self.entry_events is not None and self.entry_events not in formula_manager:
                formula_manager.normalize(self.entry_events)

            if self.invariant is not None and self.invariant not in formula_manager:
                formula_manager.normalize(self.invariant)

        def is_upper_bound(self) -> bool:
            return (
                self.bound_type == Countertrace.BoundTypes.LESS or self.bound_type == Countertrace.BoundTypes.LESSEQUAL
            )

        def is_lower_bound(self) -> bool:
            return (
                self.bound_type == Countertrace.BoundTypes.GREATER
                or self.bound_type == Countertrace.BoundTypes.GREATEREQUAL
            )

        def extract_variables(self) -> set[FNode]:
            return set(get_free_variables(self.invariant))


def phaseT() -> Countertrace.DCPhase:
    return Countertrace.DCPhase(TRUE(), TRUE(), Countertrace.BoundTypes.NONE, 0, set(), True)


def phaseE(invariant: FNode, bound_type: Countertrace.BoundTypes, bound: int) -> Countertrace.DCPhase:
    return Countertrace.DCPhase(TRUE(), invariant, bound_type, bound, set(), True)


def phase(
    invariant: FNode, bound_type: Countertrace.BoundTypes = Countertrace.BoundTypes.NONE, bound: int = 0
) -> Countertrace.DCPhase:
    return Countertrace.DCPhase(TRUE(), invariant, bound_type, bound, set(), False)


class CountertraceTransformer(Transformer):
    def __init__(self, expressions: dict[str, FNode]) -> None:
        super().__init__()
        self.expressions = expressions

    @staticmethod
    def countertrace(children) -> Countertrace:
        return Countertrace(*children)

    @staticmethod
    def phase_t(children) -> Countertrace.DCPhase:
        return phaseT()

    @staticmethod
    def phase_unbounded(children) -> Countertrace.DCPhase:
        return phase(children[0])

    @staticmethod
    def phase(children) -> Countertrace.DCPhase:
        return phase(children[0], children[1], children[2])

    @staticmethod
    def phase_e(children) -> Countertrace.DCPhase:
        return phaseE(children[0], children[1], children[2])

    @staticmethod
    def conjunction(children) -> Countertrace.DCPhase:
        return And(children[0], children[1])

    @staticmethod
    def disjunction(children) -> Countertrace.DCPhase:
        return Or(children[0], children[1])

    @staticmethod
    def negation(children) -> Countertrace.DCPhase:
        return Not(children[0])

    @staticmethod
    def bound_type_lt(children) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.LESS

    @staticmethod
    def bound_type_lteq(children) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.LESSEQUAL

    @staticmethod
    def bound_type_gt(children) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.GREATER

    @staticmethod
    def bound_type_gteq(children) -> Countertrace.BoundTypes:
        return Countertrace.BoundTypes.GREATEREQUAL

    def variable(self, children) -> FNode:
        return self.expressions.get(children[0])

    @staticmethod
    def true(children) -> FNode:
        return TRUE()

    @staticmethod
    def __default__(data, children, meta):
        if len(children) != 1:
            raise ValueError(f"Unexpected size of children: {len(children)}")

        return children[0]
