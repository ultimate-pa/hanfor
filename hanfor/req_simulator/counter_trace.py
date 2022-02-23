from __future__ import annotations

from enum import Enum

from lark.visitors import Transformer
from pysmt.fnode import FNode
from pysmt.shortcuts import TRUE, Not, And, Or


class CounterTrace:
    def __init__(self, *dc_phases: DCPhase) -> None:
        self.dc_phases = [dc_phase for dc_phase in dc_phases]

    def __str__(self) -> str:
        return ';'.join([str(dc_phase) for dc_phase in self.dc_phases])

    class BoundTypes(Enum):
        NONE = 0
        LESS = 1
        LESSEQUAL = 2
        GREATER = 3
        GREATEREQUAL = 4

    class DCPhase:
        def __init__(self, entry_events: FNode, invariant: FNode, bound_type: CounterTrace.BoundTypes, bound: int,
                     forbid: set[str], allow_empty: bool) -> None:
            self.entry_events: FNode = entry_events
            self.invariant: FNode = invariant
            self.bound_type: CounterTrace.BoundTypes = bound_type
            self.bound: float = bound
            self.forbid: set[str] = forbid
            self.allow_empty: bool = allow_empty

        def __str__(self, unicode: bool = True) -> str:
            result = ''

            _AND = '\u2227' if unicode else '/\\'
            _NO_EVENT = '\u229F' if unicode else '[-]'
            _EMPTY = '\u2080' if unicode else '0'
            _GEQ = '\u2265' if unicode else '>='
            _LEQ = '\u2264' if unicode else '<='
            _LCEIL = '\u2308' if unicode else '['
            _RCEIL = '\u2309' if unicode else ']'
            _ELL = '\u2113' if unicode else 'L'

            result += str(self.entry_events) + ';' if self.entry_events != TRUE() else ''
            result += str(self.invariant) if self.invariant == TRUE() else _LCEIL + str(self.invariant) + _RCEIL

            for forbid in self.forbid:
                result += ' ' + _AND + ' ' + _NO_EVENT + ' ' + forbid

            if self.bound_type == CounterTrace.BoundTypes.NONE:
                return result

            result += ' ' + _AND + ' ' + _ELL

            if self.bound_type == CounterTrace.BoundTypes.LESS:
                result += ' <' + _EMPTY + ' ' if self.allow_empty else ' < '
            elif self.bound_type == CounterTrace.BoundTypes.LESSEQUAL:
                result += ' ' + _LEQ + _EMPTY + ' ' if self.allow_empty else ' ' + _LEQ + ' '
            elif self.bound_type == CounterTrace.BoundTypes.GREATER:
                result += ' >' + _EMPTY + ' ' if self.allow_empty else ' > '
            elif self.bound_type == CounterTrace.BoundTypes.GREATEREQUAL:
                result += ' ' + _GEQ + _EMPTY + ' ' if self.allow_empty else ' ' + _GEQ + ' '
            else:
                raise ValueError("Unexpected value of `bound_type`: %s" % self.bound_type)

            result += str(self.bound)

            return result

        def is_upper_bound(self) -> bool:
            return self.bound_type == CounterTrace.BoundTypes.LESS or \
                   self.bound_type == CounterTrace.BoundTypes.LESSEQUAL

        def is_lower_bound(self) -> bool:
            return self.bound_type == CounterTrace.BoundTypes.GREATER or \
                   self.bound_type == CounterTrace.BoundTypes.GREATEREQUAL


def phaseT() -> CounterTrace.DCPhase:
    return CounterTrace.DCPhase(TRUE(), TRUE(), CounterTrace.BoundTypes.NONE, 0, set(), True)


def phaseE(invariant: FNode, bound_type: CounterTrace.BoundTypes, bound: int) -> CounterTrace.DCPhase:
    return CounterTrace.DCPhase(TRUE(), invariant, bound_type, bound, set(), True)


def phase(invariant: FNode, bound_type: CounterTrace.BoundTypes = CounterTrace.BoundTypes.NONE,
          bound: int = 0) -> CounterTrace.DCPhase:
    return CounterTrace.DCPhase(TRUE(), invariant, bound_type, bound, set(), False)


# TODO: Obsolete.
'''
def create_counter_trace(scope: str, pattern: str, expressions: dict[str, FNode]) -> CounterTrace:
    _P = expressions.get('P')  # Scope
    _Q = expressions.get('Q')  # Scope
    _R = expressions.get('R')
    _S = expressions.get('S')
    _T = expressions.get('T')

    if pattern == 'BndResponsePatternUT':
        if scope == 'GLOBALLY':
            return CounterTrace(phaseT(), phase(_R.And(Not(_S))), phase(Not(_S), CounterTrace.BoundTypes.GREATER, _T),
                                phaseT())
        if scope == 'BEFORE':
            return CounterTrace(phase(Not(_P)), phase(Not(_P).And(_R).And(Not(_S))),
                                phase(Not(_P).And(Not(_S)), CounterTrace.BoundTypes.GREATER, _T), phaseT())
        if scope == 'AFTER':
            return CounterTrace(phaseT(), phase(_P), phaseT(), phase(_R.And(Not(_S))),
                                phase(Not(_S), CounterTrace.BoundTypes.GREATER, _T), phaseT())
        if scope == 'BETWEEN':
            return CounterTrace(phaseT(), phase(_P.And(Not(_Q))), phase(Not(_Q)), phase(Not(_Q).And(_R).And(Not(_S))),
                                phase(Not(_Q).And(Not(_S)), CounterTrace.BoundTypes.GREATER, _T), phase(Not(_Q)),
                                phase(_Q), phaseT())
        if scope == 'AFTER_UNTIL':
            return CounterTrace(phaseT(), phase(_P), phase(Not(_Q)), phase(Not(_Q).And(_R).And(Not(_S))),
                                phase(Not(_Q).And(Not(_S)), CounterTrace.BoundTypes.GREATER, _T), phaseT())
    else:
        raise NotImplementedError('Pattern is not implemented: %s %s' % (scope, pattern))
'''


class CounterTraceTransformer(Transformer):
    def __init__(self, expressions: dict[str, FNode]) -> None:
        super().__init__()
        self.expressions = expressions

    @staticmethod
    def counter_trace(children) -> CounterTrace:
        print("counter_trace:", children)
        return CounterTrace(*children)

    @staticmethod
    def phase_t(children) -> CounterTrace.DCPhase:
        print("phase_t:", children)
        return phaseT()

    @staticmethod
    def phase_unbounded(children) -> CounterTrace.DCPhase:
        print("phase_unbounded:", children)
        return phase(children[0])

    @staticmethod
    def phase(children) -> CounterTrace.DCPhase:
        print("phase:", children)
        return phase(children[0], children[1], children[2])

    @staticmethod
    def phase_e(children) -> CounterTrace.DCPhase:
        print("phase_e:", children)
        return phaseE(children[0], children[1], children[2])

    @staticmethod
    def conjunction(children) -> CounterTrace.DCPhase:
        print("conjunction:", children)
        return And(children[0], children[1])

    @staticmethod
    def disjunction(children) -> CounterTrace.DCPhase:
        print("disjunction:", children)
        return Or(children[0], children[1])

    @staticmethod
    def negation(children) -> CounterTrace.DCPhase:
        print("negation:", children)
        return Not(children[0])

    @staticmethod
    def bound_type_lt(children) -> CounterTrace.BoundTypes:
        print("bound_type_lt:", children)
        return CounterTrace.BoundTypes.LESS

    @staticmethod
    def bound_type_lteq(children) -> CounterTrace.BoundTypes:
        print("bound_type_lteq:", children)
        return CounterTrace.BoundTypes.LESSEQUAL

    @staticmethod
    def bound_type_gt(children) -> CounterTrace.BoundTypes:
        print("bound_type_gt:", children)
        return CounterTrace.BoundTypes.GREATER

    @staticmethod
    def bound_type_gteq(children) -> CounterTrace.BoundTypes:
        print("bound_type_gteq:", children)
        return CounterTrace.BoundTypes.GREATEREQUAL

    def variable(self, children) -> FNode:
        print("variable:", children)
        return self.expressions.get(children[0])

    @staticmethod
    def true(children) -> FNode:
        print("true:", children)
        return TRUE()

    @staticmethod
    def __default__(data, children, meta):
        print("default:", children)

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
