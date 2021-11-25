from lark import Transformer, Token
from pysmt.shortcuts import And, Or, Div, Equals, FALSE, TRUE, GT, GE, Symbol, Iff, Implies, LT, LE, Minus, Not, \
    NotEquals, \
    Int, Plus, Real, Times
from pysmt.typing import INT, BOOL, REAL

import boogie_parsing


class BoogiePysmtTransformer(Transformer):
    boogie_to_pysmt_type_mapping = {
        boogie_parsing.BoogieType.bool: BOOL,
        boogie_parsing.BoogieType.int: INT,
        boogie_parsing.BoogieType.real: REAL
    }

    def __init__(self, type_env: dict[str, boogie_parsing.BoogieType]):
        super().__init__()
        self.type_env = type_env
        self.formula = None

    def conjunction(self, children):
        print("conjunction:", children)
        return And(children[0], children[2])

    def disjunction(self, children):
        print("disjunction:", children)
        return Or(children[0], children[2])

    def divide(self, children):
        print("devide:", children)
        return Div(children[0], children[2])

    def eq(self, children):
        print("eq:", children)
        # It is not supported to use equality '=' on boolean terms. One should use  iff '<->' instead.
        if children[0].get_type() == BOOL or children[2].get_type() == BOOL:
            return self.iff(children)
        return Equals(children[0], children[2])

    def explies(self, children):
        print("explies:", children)
        raise NotImplementedError("Unsupported operation 'explies'.")

    def false(self, children):
        print("false:", children)
        return FALSE()

    def gt(self, children):
        print("gt:", children)
        return GT(children[0], children[2])

    def gteq(self, children):
        print("gteq:", children)
        return GE(children[0], children[2])

    def id(self, children):
        print("id:", children)
        boogie_type = self.type_env[children[0].value]
        pysmt_type = self.boogie_to_pysmt_type_mapping.get(boogie_type)

        if not pysmt_type:
            raise ValueError("Unexpected value of `boogie_type`: %s" % boogie_type)

        return Symbol(children[0].value, pysmt_type)

    def iff(self, children):
        print("iff:", children)
        return Iff(children[0], children[2])

    def implies(self, children):
        print("implies:", children)
        return Implies(children[0], children[2])

    def lt(self, children):
        print("lt:", children)
        return LT(children[0], children[2])

    def lteq(self, children):
        print("lteq:", children)
        return LE(children[0], children[2])

    def minus(self, children):
        print("minus:", children)
        return Minus(children[0], children[2])

    def minus_unary(self, children):
        print("minus_unary:", children)
        return -children[1]

    def mod(self, children):
        print("mod:", children)
        raise NotImplementedError("Unsupported operation 'mod'.")

    def negation(self, children):
        print("negation:", children)
        return Not(children[1])

    def neq(self, children):
        print("neq:", children)
        return NotEquals(children[0], children[2])

    def number(self, children):
        print("number:", children)
        return Int(int(children[0]))

    def plus(self, children):
        print("plus:", children)
        return Plus(children[0], children[2])

    def plus_unary(self, children):
        print("plus_unary:", children)
        return +children[1]

    def realnumber(self, children):
        print("realnumber:", children)
        return Real(float(children[0]))

    def times(self, children):
        print("times:", children)
        return Times(children[0], children[2])

    def true(self, children):
        print("true:", children)
        return TRUE()

    def __default__(self, data, children, meta):
        print("default:", children)
        children = [child for child in children if not isinstance(child, Token)]

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]