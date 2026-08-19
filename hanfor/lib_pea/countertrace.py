from enum import Enum
from typing import Union

from lark.visitors import Transformer
from pysmt.environment import Environment
from pysmt.fnode import FNode


class Countertrace:
    def __init__(self, smt_env: Environment, *dc_phases: "DCPhase") -> None:
        self.__smt_env: Environment = smt_env
        self.dc_phases: list["DCPhase"] = [dc_phase for dc_phase in dc_phases]

    def __str__(self) -> str:
        return ";".join([str(dc_phase) for dc_phase in self.dc_phases])

    def normalize(self) -> None:
        for dc_phase in self.dc_phases:
            dc_phase.normalize()

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

    def invert(self):
        match self:
            case BoundTypes.LESS:
                return BoundTypes.GREATEREQUAL
            case BoundTypes.LESSEQUAL:
                return BoundTypes.GREATER
            case BoundTypes.GREATER:
                return BoundTypes.LESSEQUAL
            case BoundTypes.GREATEREQUAL:
                return BoundTypes.LESS
            case _:
                return BoundTypes.NONE


class DCPhase:
    def __init__(
        self,
        smt_env: Environment,
        entry_events: FNode,
        invariant: FNode,
        bound_type: "BoundTypes",
        bound: Union[FNode, float, None],
        forbid: set[str],
        allow_empty: bool,
    ) -> None:
        self.__smt_env = smt_env
        self.__fmgr = smt_env.formula_manager
        self.entry_events: FNode = entry_events
        self.invariant: FNode = invariant
        self.bound_type: BoundTypes = bound_type
        # TODO: typing for this bound field is all over the place (sometimes None, Int or FNode) fix that
        self.bound: Union[FNode, float, None] = bound
        self.forbid: set[str] = forbid
        self.allow_empty: bool = allow_empty

    def __str__(self, unicode: bool = True) -> str:
        result = ""

        _AND = "\u2227" if unicode else "/\\"
        _NO_EVENT = "\u229f" if unicode else "[-]"
        _EMPTY = "\u2080" if unicode else "0"
        _GEQ = "\u2265" if unicode else ">="
        _LEQ = "\u2264" if unicode else "<="
        _LCEIL = "\u2308" if unicode else "["
        _RCEIL = "\u2309" if unicode else "]"
        _ELL = "\u2113" if unicode else "L"

        result += self.entry_events.serialize() + ";" if self.entry_events != self.__fmgr.TRUE() else ""
        result += (
            self.invariant.serialize()
            if self.invariant == self.__fmgr.TRUE()
            else _LCEIL + self.invariant.serialize() + _RCEIL
        )

        for forbid in self.forbid:
            result += " " + _AND + " " + _NO_EVENT + " " + forbid

        if self.bound_type == BoundTypes.NONE:
            return result

        result += " " + _AND + " " + _ELL

        if self.bound_type == BoundTypes.LESS:
            result += " <" + _EMPTY + " " if self.allow_empty else " < "
        elif self.bound_type == BoundTypes.LESSEQUAL:
            result += " " + _LEQ + _EMPTY + " " if self.allow_empty else " " + _LEQ + " "
        elif self.bound_type == BoundTypes.GREATER:
            result += " >" + _EMPTY + " " if self.allow_empty else " > "
        elif self.bound_type == BoundTypes.GREATEREQUAL:
            result += " " + _GEQ + _EMPTY + " " if self.allow_empty else " " + _GEQ + " "
        else:
            raise ValueError("Unexpected value of `bound_type`: %s" % self.bound_type)

        result += str(self.bound)

        return result

    def normalize(self) -> None:
        if self.entry_events is not None and self.entry_events not in self.__fmgr:
            self.__fmgr.normalize(self.entry_events)

        if self.invariant is not None and self.invariant not in self.__fmgr:
            self.__fmgr.normalize(self.invariant)

    def is_upper_bound(self) -> bool:
        return self.bound_type == BoundTypes.LESS or self.bound_type == BoundTypes.LESSEQUAL

    def is_lower_bound(self) -> bool:
        return self.bound_type == BoundTypes.GREATER or self.bound_type == BoundTypes.GREATEREQUAL

    def extract_variables(self) -> set[FNode]:
        return set(self.__smt_env.fvo.get_free_variables(self.invariant))


def phaseT(smt_env: Environment) -> DCPhase:
    return DCPhase(
        smt_env, smt_env.formula_manager.TRUE(), smt_env.formula_manager.TRUE(), BoundTypes.NONE, None, set(), True
    )


def phaseE(smt_env: Environment, invariant: FNode, bound_type: BoundTypes, bound: int) -> DCPhase:
    return DCPhase(smt_env, smt_env.formula_manager.TRUE(), invariant, bound_type, bound, set(), True)


def phase(smt_env: Environment, invariant: FNode, bound_type: BoundTypes = BoundTypes.NONE, bound: int = 0) -> DCPhase:
    return DCPhase(smt_env, smt_env.formula_manager.TRUE(), invariant, bound_type, bound, set(), False)


class CountertraceTransformer(Transformer):
    def __init__(self, smt_env: Environment, expressions: dict[str, FNode]) -> None:
        super().__init__()
        self.expressions = expressions
        self.__smt_env = smt_env
        self.__fmgr = smt_env.formula_manager

    def countertrace(self, children) -> Countertrace:
        return Countertrace(self.__smt_env, *children)

    def phase_t(self, children) -> DCPhase:
        return phaseT(self.__smt_env)

    def phase_unbounded(self, children) -> DCPhase:
        return phase(self.__smt_env, children[0])

    def phase(self, children) -> DCPhase:
        return phase(self.__smt_env, children[0], children[1], children[2])

    def phase_e(self, children) -> DCPhase:
        return phaseE(self.__smt_env, children[0], children[1], children[2])

    def conjunction(self, children) -> DCPhase:
        return self.__fmgr.And(children[0], children[1])

    def disjunction(self, children) -> DCPhase:
        return self.__fmgr.Or(children[0], children[1])

    def negation(self, children) -> DCPhase:
        return self.__fmgr.Not(children[0])

    @staticmethod
    def bound_type_lt(children) -> BoundTypes:
        return BoundTypes.LESS

    @staticmethod
    def bound_type_lteq(children) -> BoundTypes:
        return BoundTypes.LESSEQUAL

    @staticmethod
    def bound_type_gt(children) -> BoundTypes:
        return BoundTypes.GREATER

    @staticmethod
    def bound_type_gteq(children) -> BoundTypes:
        return BoundTypes.GREATEREQUAL

    def variable(self, children) -> FNode:
        return self.expressions.get(children[0])

    def true(self, children) -> FNode:
        return self.__fmgr.TRUE()

    @staticmethod
    def __default__(data, children, meta):
        if len(children) != 1:
            raise ValueError(f"Unexpected size of children: {len(children)}")

        return children[0]
