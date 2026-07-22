from dataclasses import dataclass

from lark import Transformer, Token
from pysmt.environment import Environment
from pysmt.fnode import FNode


@dataclass
class Variable:
    name: str
    type: str
    value: str


class BoogiePysmtTransformer(Transformer):

    def __init__(self, smt_env: Environment, variables: set[Variable]) -> None:
        super().__init__()
        self.variables = variables
        self.additional_assertions = []
        self.__smt_env = smt_env
        self.__fmgr = self.__smt_env.formula_manager
        self.__tmgr = self.__smt_env.type_manager

        self.hanfor_to_pysmt_mapping = {
            "bool": lambda name, value: self.__fmgr.Symbol(name, self.__tmgr.BOOL()),
            "int": lambda name, value: self.__fmgr.Symbol(name, self.__tmgr.INT()),
            "real": lambda name, value: self.__fmgr.Symbol(name, self.__tmgr.REAL()),
            "ENUM_INT": lambda name, value: self.__fmgr.Symbol(name, self.__tmgr.INT()),
            "ENUM_REAL": lambda name, value: self.__fmgr.Symbol(name, self.__tmgr.REAL()),
            "ENUMERATOR_INT": lambda name, value: self.__fmgr.Int(int(value)),
            "ENUMERATOR_REAL": lambda name, value: self.__fmgr.Real(float(value)),
            # TODO: Make this better, please.
            "CONST": lambda name, value: (
                self.__fmgr.Real(float(value)) if "." in value else self.__fmgr.Int(int(value))
            ),
        }
        self.smt_symbols = dict()
        self.smt_vars = dict()
        for v in variables:
            sym = self.hanfor_to_pysmt_mapping[v.type](v.name, v.value)
            self.smt_symbols[v.name] = sym
            if sym.is_symbol():
                self.smt_vars[v.name] = self.hanfor_to_pysmt_mapping[v.type](v.name, v.value)

    def expr(self, children) -> FNode:
        return self.__fmgr.And(children[0], *self.additional_assertions)

    def conjunction(self, children) -> FNode:
        return self.__fmgr.And(children[0], children[2])

    def disjunction(self, children) -> FNode:
        return self.__fmgr.Or(children[0], children[2])

    def divide(self, children) -> FNode:
        return self.__fmgr.Div(children[0], children[2])

    def eq(self, children) -> FNode:
        return self.__fmgr.EqualsOrIff(children[0], children[2])

    def false(self, children) -> FNode:
        return self.__fmgr.FALSE()

    def gt(self, children) -> FNode:
        return self.__fmgr.GT(children[0], children[2])

    def gteq(self, children) -> FNode:
        return self.__fmgr.GE(children[0], children[2])

    def id(self, children) -> FNode:
        name = children[0].value
        return self.smt_symbols[name]

    def implies(self, children) -> FNode:
        return self.__fmgr.Implies(children[0], children[2])

    def explies(self, children) -> FNode:
        return self.__fmgr.Implies(children[2], children[0])

    def iff(self, children) -> FNode:
        return self.__fmgr.Iff(children[0], children[2])

    def lt(self, children) -> FNode:
        return self.__fmgr.LT(children[0], children[2])

    def lteq(self, children) -> FNode:
        return self.__fmgr.LE(children[0], children[2])

    def minus(self, children) -> FNode:
        return self.__fmgr.Minus(children[0], children[2])

    def minus_unary(self, children) -> FNode:
        return self.__fmgr.Times(self.__fmgr.Int(-1), children[1])

    def mod(self, children) -> None:
        D, d = children[0], children[2]
        self.additional_assertions.append(self.__fmgr.NotEquals(d, self.__fmgr.Int(0)))
        return self.__fmgr.Minus(D, self.__fmgr.Times(d, self.__fmgr.Div(D, d)))

    def negation(self, children) -> FNode:
        return self.__fmgr.Not(children[1])

    def neq(self, children) -> FNode:
        return self.__fmgr.NotEquals(children[0], children[2])

    def number(self, children) -> FNode:
        return self.__fmgr.Int(int(children[0]))

    def plus(self, children) -> FNode:
        return self.__fmgr.Plus(children[0], children[2])

    def realnumber(self, children) -> FNode:
        return self.__fmgr.Real(float(children[0]))

    def times(self, children) -> FNode:
        return self.__fmgr.Times(children[0], children[2])

    def true(self, children) -> FNode:
        return self.__fmgr.TRUE()

    def abs(self, children) -> FNode:
        return self.__fmgr.Ite(children[1] < 0, -children[1], children[1])

    def min(self, children) -> FNode:
        return self.__fmgr.Min(children[1], children[2])

    def max(self, children) -> FNode:
        return self.__fmgr.Max(children[1], children[2])

    @staticmethod
    def old(children) -> FNode:
        raise NotImplementedError

    @staticmethod
    def __default__(data, children, meta):
        children = [child for child in children if not isinstance(child, Token)]

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
