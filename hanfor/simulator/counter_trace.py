from __future__ import annotations

from enum import Enum

from lark.visitors import Transformer
from pysmt.fnode import FNode
from pysmt.shortcuts import TRUE, Not, And, Or


class CounterTrace:
    def __init__(self, *dc_phases: DCPhase) -> None:
        self.dc_phases = [dc_phase for dc_phase in dc_phases]

    def __str__(self) -> str:
        return ';'.join([str(phase) for phase in self.dc_phases])

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
            self.bound: int = bound
            self.forbid: set[str] = forbid
            self.allow_empty: bool = allow_empty

        def is_upper_bound(self) -> bool:
            return self.bound_type == CounterTrace.BoundTypes.LESS or \
                   self.bound_type == CounterTrace.BoundTypes.LESSEQUAL

        def is_lower_bound(self) -> bool:
            return self.bound_type == CounterTrace.BoundTypes.GREATER or \
                   self.bound_type == CounterTrace.BoundTypes.GREATEREQUAL

        def __str__(self, unicode: bool = True) -> str:
            result = ''

            AND = '\u2227' if unicode else '/\\'
            NOEVENT = '\u229F' if unicode else '[-]'
            EMPTY = '\u2080' if unicode else '0'
            GEQ = '\u2265' if unicode else '>='
            LEQ = '\u2264' if unicode else '<='
            LCEIL = '\u2308' if unicode else '['
            RCEIL = '\u2309' if unicode else ']'
            ELL = '\u2113' if unicode else 'L'

            result += str(self.entry_events) + ';' if self.entry_events != TRUE() else ''
            result += str(self.invariant) if self.invariant == TRUE() else LCEIL + str(self.invariant) + RCEIL

            for forbid in self.forbid:
                result += ' ' + AND + ' ' + NOEVENT + ' ' + forbid

            if self.bound_type == CounterTrace.BoundTypes.NONE:
                return result

            result += ' ' + AND + ' ' + ELL

            if self.bound_type == CounterTrace.BoundTypes.LESS:
                result += ' <' + EMPTY + ' ' if self.allow_empty else ' < '
            elif self.bound_type == CounterTrace.BoundTypes.LESSEQUAL:
                result += ' ' + LEQ + EMPTY + ' ' if self.allow_empty else ' ' + LEQ + ' '
            elif self.bound_type == CounterTrace.BoundTypes.GREATER:
                result += ' >' + EMPTY + ' ' if self.allow_empty else ' > '
            elif self.bound_type == CounterTrace.BoundTypes.GREATEREQUAL:
                result += ' ' + GEQ + EMPTY + ' ' if self.allow_empty else ' ' + GEQ + ' '
            else:
                raise ValueError("Unexpected value of `bound_type`: %s" % self.bound_type)

            result += str(self.bound)

            return result


def phaseT() -> CounterTrace.DCPhase:
    return CounterTrace.DCPhase(TRUE(), TRUE(), CounterTrace.BoundTypes.NONE, 0, set(), True)


def phaseE(invariant: FNode, bound_type: CounterTrace.BoundTypes, bound: int) -> CounterTrace.DCPhase:
    return CounterTrace.DCPhase(TRUE(), invariant, bound_type, bound, set(), True)


def phase(invariant: FNode, bound_type: CounterTrace.BoundTypes = CounterTrace.BoundTypes.NONE,
          bound: int = 0) -> CounterTrace.DCPhase:
    return CounterTrace.DCPhase(TRUE(), invariant, bound_type, bound, set(), False)


# TODO: Obsolete.
def create_counter_trace(scope: str, pattern: str, expressions: dict[str, FNode]) -> CounterTrace:
    P = expressions.get('P')  # Scope
    Q = expressions.get('Q')  # Scope
    R = expressions.get('R')
    S = expressions.get('S')
    T = expressions.get('T')
    U = expressions.get('U')
    V = expressions.get('V')

    if pattern == 'BndResponsePatternUT':
        if scope == 'GLOBALLY':
            return CounterTrace(phaseT(), phase(R.And(Not(S))), phase(Not(S), CounterTrace.BoundTypes.GREATER, T),
                                phaseT())
        if scope == 'BEFORE':
            return CounterTrace(phase(Not(P)), phase(Not(P).And(R).And(Not(S))),
                                phase(Not(P).And(Not(S)), CounterTrace.BoundTypes.GREATER, T), phaseT())
        if scope == 'AFTER':
            return CounterTrace(phaseT(), phase(P), phaseT(), phase(R.And(Not(S))),
                                phase(Not(S), CounterTrace.BoundTypes.GREATER, T), phaseT())
        if scope == 'BETWEEN':
            return CounterTrace(phaseT(), phase(P.And(Not(Q))), phase(Not(Q)), phase(Not(Q).And(R).And(Not(S))),
                                phase(Not(Q).And(Not(S)), CounterTrace.BoundTypes.GREATER, T), phase(Not(Q)), phase(Q),
                                phaseT())
        if scope == 'AFTER_UNTIL':
            return CounterTrace(phaseT(), phase(P), phase(Not(Q)), phase(Not(Q).And(R).And(Not(S))),
                                phase(Not(Q).And(Not(S)), CounterTrace.BoundTypes.GREATER, T), phaseT())
    else:
        raise NotImplementedError('Pattern is not implemented: %s %s' % (scope, pattern))


class CounterTraceTransformer(Transformer):
    def __init__(self, expressions: dict[str, FNode]) -> None:
        super().__init__()
        self.expressions = expressions

    def counter_trace(self, children) -> CounterTrace:
        print("counter_trace:", children)
        return CounterTrace(*children)

    def phase_t(self, children) -> CounterTrace.DCPhase:
        print("phase_t:", children)
        return phaseT()

    def phase_unbounded(self, children) -> CounterTrace.DCPhase:
        print("phase_unbounded:", children)
        return phase(children[0])

    def phase(self, children) -> CounterTrace.DCPhase:
        print("phase:", children)
        return phase(children[0], children[1], children[2])

    def phase_e(self, children) -> CounterTrace.DCPhase:
        print("phase_e:", children)
        return phaseE(children[0], children[1], children[2])

    def conjunction(self, children) -> CounterTrace.DCPhase:
        print("conjunction:", children)
        return And(children[0], children[1])

    def disjunction(self, children) -> CounterTrace.DCPhase:
        print("disjunction:", children)
        return Or(children[0], children[1])

    def negation(self, children) -> CounterTrace.DCPhase:
        print("negation:", children)
        return Not(children[0])

    def bound_type_lt(self, children) -> CounterTrace.BoundTypes:
        print("bound_type_lt:", children)
        return CounterTrace.BoundTypes.LESS

    def bound_type_lteq(self, children) -> CounterTrace.BoundTypes:
        print("bound_type_lteq:", children)
        return CounterTrace.BoundTypes.LESSEQUAL

    def bound_type_gt(self, children) -> CounterTrace.BoundTypes:
        print("bound_type_gt:", children)
        return CounterTrace.BoundTypes.GREATER

    def bound_type_gteq(self, children) -> CounterTrace.BoundTypes:
        print("bound_type_gteq:", children)
        return CounterTrace.BoundTypes.GREATEREQUAL

    def variable(self, children) -> FNode:
        print("variable:", children)
        return self.expressions.get(children[0])

    def __default__(self, data, children, meta):
        print("default:", children)

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
