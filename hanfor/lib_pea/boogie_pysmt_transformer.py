from dataclasses import dataclass

from lark import Transformer, Token
from pysmt.fnode import FNode
from pysmt.shortcuts import (
    And,
    Or,
    Div,
    FALSE,
    TRUE,
    GT,
    GE,
    Symbol,
    Implies,
    LT,
    LE,
    Minus,
    Not,
    NotEquals,
    Int,
    Plus,
    Real,
    Times,
    EqualsOrIff,
    Max,
    Min,
    Ite,
    Iff,
)
from pysmt.typing import INT, BOOL, REAL


@dataclass
class Variable:
    name: str
    type: str
    value: str


class BoogiePysmtTransformer(Transformer):
    hanfor_to_pysmt_mapping = {
        "bool": lambda name, value: Symbol(name, BOOL),
        "int": lambda name, value: Symbol(name, INT),
        "real": lambda name, value: Symbol(name, REAL),
        "ENUM_INT": lambda name, value: Symbol(name, INT),
        "ENUM_REAL": lambda name, value: Symbol(name, REAL),
        "ENUMERATOR_INT": lambda name, value: Int(int(value)),
        "ENUMERATOR_REAL": lambda name, value: Real(float(value)),
        # TODO: Make this better, please.
        "CONST": lambda name, value: Real(float(value)) if "." in value else Int(int(value)),
    }

    def __init__(self, variables: set[Variable]) -> None:
        super().__init__()
        self.variables = variables
        self.additional_assertions = []
        self.smt_symbols = dict()
        self.smt_vars = dict()
        for v in variables:
            sym = self.hanfor_to_pysmt_mapping[v.type](v.name, v.value)
            self.smt_symbols[v.name] = sym
            if sym.is_symbol():
                self.smt_vars[v.name] = self.hanfor_to_pysmt_mapping[v.type](v.name, v.value)

    def expr(self, children) -> FNode:
        return And(children[0], *self.additional_assertions)

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
        return self.smt_symbols[name]

    @staticmethod
    def implies(children) -> FNode:
        return Implies(children[0], children[2])

    @staticmethod
    def explies(children) -> FNode:
        return Implies(children[2], children[0])

    @staticmethod
    def iff(children) -> FNode:
        return Iff(children[0], children[2])

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

    # @staticmethod
    def mod(self, children) -> None:
        D, d = children[0], children[2]
        self.additional_assertions.append(NotEquals(d, Int(0)))
        return Minus(D, Times(d, Div(D, d)))

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
    def plus(children) -> FNode:
        return Plus(children[0], children[2])

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
    def abs(children) -> FNode:
        return Ite(children[1] < 0, -children[1], children[1])

    @staticmethod
    def min(children) -> FNode:
        return Min(children[1], children[2])

    @staticmethod
    def max(children) -> FNode:
        return Max(children[1], children[2])

    @staticmethod
    def old(children) -> FNode:
        raise NotImplementedError

    @staticmethod
    def __default__(data, children, meta):
        children = [child for child in children if not isinstance(child, Token)]

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
