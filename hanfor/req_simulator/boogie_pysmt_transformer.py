from lark import Transformer, Token
from pysmt.fnode import FNode
from pysmt.shortcuts import And, Or, Div, FALSE, TRUE, GT, GE, Symbol, Iff, Implies, LT, LE, Minus, Not, \
    NotEquals, \
    Int, Plus, Real, Times, EqualsOrIff, Max, Min, Ite
from pysmt.typing import INT, BOOL, REAL

from reqtransformer import Variable


class BoogiePysmtTransformer(Transformer):
    hanfor_to_pysmt_mapping = {
        'bool': lambda name, value: Symbol(name, BOOL),
        'int': lambda name, value: Symbol(name, INT),
        'real': lambda name, value: Symbol(name, REAL),
        'ENUM_INT': lambda name, value: Symbol(name, INT),
        'ENUM_REAL': lambda name, value: Symbol(name, REAL),
        'ENUMERATOR_INT': lambda name, value: Int(int(value)),
        'ENUMERATOR_REAL': lambda name, value: Real(float(value)),
        # TODO: Make this better, please.
        'CONST': lambda name, value: Real(float(value)) if '.' in value else Int(int(value))
    }

    def __init__(self, variables: dict[str, Variable]) -> None:
        super().__init__()
        self.variables = variables

    @staticmethod
    def abs(children) -> FNode:
        return Ite(children[1] < 0, -children[1], children[1])

    @staticmethod
    def concat(children) -> FNode:
        raise NotImplementedError

    @staticmethod
    def conjunction(children) -> FNode:
        return And(children[0], children[2])

    @staticmethod
    def disjunction(children) -> FNode:
        return Or(children[0], children[2])

    @staticmethod
    def divide(children) -> FNode:
        return Div(children[0], children[2])

    @staticmethod
    def eq(children) -> FNode:
        return EqualsOrIff(children[0], children[2])

    @staticmethod
    def explies(children) -> FNode:
        raise NotImplementedError

    @staticmethod
    def false(children) -> FNode:
        return FALSE()

    @staticmethod
    def gt(children) -> FNode:
        return GT(children[0], children[2])

    @staticmethod
    def gteq(children) -> FNode:
        return GE(children[0], children[2])

    def id(self, children) -> FNode:
        name = children[0].value
        type = self.variables[name].type
        value = self.variables[name].value

        return self.hanfor_to_pysmt_mapping[type](name, value)

    @staticmethod
    def iff(children) -> FNode:
        return Iff(children[0], children[2])

    @staticmethod
    def implies(children) -> FNode:
        return Implies(children[0], children[2])

    @staticmethod
    def lt(children) -> FNode:
        return LT(children[0], children[2])

    @staticmethod
    def lteq(children) -> FNode:
        return LE(children[0], children[2])

    @staticmethod
    def max(children) -> FNode:
        return Max(children[1], children[2])

    @staticmethod
    def min(children) -> FNode:
        return Min(children[1], children[2])

    @staticmethod
    def minus(children) -> FNode:
        return Minus(children[0], children[2])

    @staticmethod
    def minus_unary(children) -> FNode:
        return -children[1]

    @staticmethod
    def mod(children) -> None:
        raise NotImplementedError

    @staticmethod
    def negation(children) -> FNode:
        return Not(children[1])

    @staticmethod
    def neq(children) -> FNode:
        return NotEquals(children[0], children[2])

    @staticmethod
    def number(children) -> FNode:
        return Int(int(children[0]))

    @staticmethod
    def old(children) -> FNode:
        raise NotImplementedError

    @staticmethod
    def partorder(children) -> FNode:
        raise NotImplementedError

    @staticmethod
    def plus(children) -> FNode:
        return Plus(children[0], children[2])

    @staticmethod
    def plus_unary(children) -> FNode:
        return +children[1]

    @staticmethod
    def realnumber(children) -> FNode:
        return Real(float(children[0]))

    @staticmethod
    def times(children) -> FNode:
        return Times(children[0], children[2])

    @staticmethod
    def true(children) -> FNode:
        return TRUE()

    @staticmethod
    def __default__(data, children, meta):
        children = [child for child in children if not isinstance(child, Token)]

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
