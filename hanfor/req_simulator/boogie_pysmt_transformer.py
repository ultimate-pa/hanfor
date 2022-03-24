from lark import Transformer, Token
from pysmt.fnode import FNode
from pysmt.shortcuts import And, Or, Div, FALSE, TRUE, GT, GE, Symbol, Iff, Implies, LT, LE, Minus, Not, \
    NotEquals, \
    Int, Plus, Real, Times, EqualsOrIff
from pysmt.typing import INT, BOOL, REAL


class BoogiePysmtTransformer(Transformer):
    '''
    boogie_to_pysmt_type_mapping = {
        boogie_parsing.BoogieType.bool: BOOL,
        boogie_parsing.BoogieType.int: INT,
        boogie_parsing.BoogieType.real: REAL
    }
    '''

    hanfor_to_pysmt_type_mapping = {
        'bool': BOOL,
        'int': INT,
        'real': REAL,
        'ENUM_INT': INT,
        'ENUM_REAL': REAL,
        'ENUMERATOR_INT': INT,
        'ENUMERATOR_REAL': REAL
    }

    #def __init__(self, type_env: dict[str, boogie_parsing.BoogieType]) -> None:
    def __init__(self, variables: dict[str, str]) -> None:
        super().__init__()
        self.variables_mapping = variables

    def conjunction(self, children) -> FNode:
        #print("conjunction:", children)
        return And(children[0], children[2])

    def disjunction(self, children) -> FNode:
        #print("disjunction:", children)
        return Or(children[0], children[2])

    def divide(self, children) -> FNode:
        #print("devide:", children)
        return Div(children[0], children[2])

    def eq(self, children) -> FNode:
        #print("eq:", children)
        return EqualsOrIff(children[0], children[2])

    def explies(self, children) -> FNode:
        #print("explies:", children)
        raise NotImplementedError("Unsupported operation 'explies'.")

    def false(self, children) -> FNode:
        #print("false:", children)
        return FALSE()

    def gt(self, children) -> FNode:
        #print("gt:", children)
        return GT(children[0], children[2])

    def gteq(self, children) -> FNode:
        #print("gteq:", children)
        return GE(children[0], children[2])

    def id(self, children) -> Symbol:
        #print("id:", children)
        hanfor_type = self.variables_mapping.get(children[0].value)
        pysmt_type = self.hanfor_to_pysmt_type_mapping.get(hanfor_type)

        if pysmt_type is None:
            raise ValueError("Unexpected variable type: %s" % hanfor_type)

        return Symbol(children[0].value, pysmt_type)

    def iff(self, children) -> FNode:
        #print("iff:", children)
        return Iff(children[0], children[2])

    def implies(self, children) -> FNode:
        #print("implies:", children)
        return Implies(children[0], children[2])

    def lt(self, children) -> FNode:
        #print("lt:", children)
        return LT(children[0], children[2])

    def lteq(self, children) -> FNode:
        #print("lteq:", children)
        return LE(children[0], children[2])

    def minus(self, children) -> FNode:
        #print("minus:", children)
        return Minus(children[0], children[2])

    def minus_unary(self, children) -> FNode:
        #print("minus_unary:", children)
        return -children[1]

    def mod(self, children) -> None:
        #print("mod:", children)
        raise NotImplementedError("Unsupported operation 'mod'.")

    def negation(self, children) -> FNode:
        #print("negation:", children)
        return Not(children[1])

    def neq(self, children) -> FNode:
        #print("neq:", children)
        return NotEquals(children[0], children[2])

    def number(self, children) -> Int:
        #print("number:", children)
        return Int(int(children[0]))

    def plus(self, children) -> FNode:
        #print("plus:", children)
        return Plus(children[0], children[2])

    def plus_unary(self, children) -> FNode:
        #print("plus_unary:", children)
        return +children[1]

    def realnumber(self, children) -> Real:
        #print("realnumber:", children)
        return Real(float(children[0]))

    def times(self, children) -> FNode:
        #print("times:", children)
        return Times(children[0], children[2])

    def true(self, children) -> FNode:
        #print("true:", children)
        return TRUE()

    def __default__(self, data, children, meta):
        #print("default:", children)
        children = [child for child in children if not isinstance(child, Token)]

        if len(children) != 1:
            raise ValueError("Unexpected size of children: %d" % len(children))

        return children[0]
