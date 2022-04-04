from lark import Transformer, Token
from pysmt.fnode import FNode
from pysmt.shortcuts import And, Or, Div, FALSE, TRUE, GT, GE, Symbol, Iff, Implies, LT, LE, Minus, Not, \
    NotEquals, \
    Int, Plus, Real, Times, EqualsOrIff
from pysmt.typing import INT, BOOL, REAL


class BoogiePysmtTransformer(Transformer):
    hanfor_to_pysmt_type_mapping = {
        'bool': BOOL,
        'int': INT,
        'real': REAL,
        'ENUM_INT': INT,
        'ENUM_REAL': REAL,
        'ENUMERATOR_INT': INT,
        'ENUMERATOR_REAL': REAL
    }

    def __init__(self, variables: dict[str, str]) -> None:
        super().__init__()
        self.variables_mapping = variables

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
        raise NotImplementedError("Unsupported operation 'explies'.")

    @staticmethod
    def false(children) -> FNode:
        return FALSE()

    @staticmethod
    def gt(children) -> FNode:
        return GT(children[0], children[2])

    @staticmethod
    def gteq(children) -> FNode:
        return GE(children[0], children[2])

    def id(self, children) -> Symbol:
        hanfor_type = self.variables_mapping.get(children[0].value)
        pysmt_type = self.hanfor_to_pysmt_type_mapping.get(hanfor_type)

        if pysmt_type is None:
            raise ValueError("Unexpected variable type: %s" % hanfor_type)

        return Symbol(children[0].value, pysmt_type)

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
    def minus(children) -> FNode:
        return Minus(children[0], children[2])

    @staticmethod
    def minus_unary(children) -> FNode:
        return -children[1]

    @staticmethod
    def mod(children) -> None:
        raise NotImplementedError("Unsupported operation 'mod'.")

    @staticmethod
    def negation(children) -> FNode:
        return Not(children[1])

    @staticmethod
    def neq(children) -> FNode:
        return NotEquals(children[0], children[2])

    @staticmethod
    def number(children) -> Int:
        return Int(int(children[0]))

    @staticmethod
    def plus(children) -> FNode:
        return Plus(children[0], children[2])

    @staticmethod
    def plus_unary(children) -> FNode:
        return +children[1]

    @staticmethod
    def realnumber(children) -> Real:
        return Real(float(children[0]))

    @staticmethod
    def times(children) -> FNode:
        return Times(children[0], children[2])

    @staticmethod
    def true(children) -> FNode:
        return TRUE()

    @staticmethod
    def false(children) -> FNode:
        return FALSE()

    @staticmethod
    def __default__(data, children, meta):
        children = [child for child in children if not isinstance(child, Token)]

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
