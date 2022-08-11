from collections import defaultdict

from enum import Enum
from typing import List

from frozendict import frozendict
from lark import Lark, Tree, Transformer
from lark.lexer import Token
from lark.reconstruct import Reconstructor
from dataclasses import dataclass, field

from lark.visitors import v_args


def get_variables_list(tree):
    """ Returns a list of variables in a expression.

    :param tree: An lark parsed tree.
    :type tree: Tree
    """
    result = list()
    for node in tree.iter_subtrees():
        for child in node.children:
            # Variables are called ID in the grammar.
            if isinstance(child, Token) and child.type == 'ID':
                result.append(child.value)

    return result

lark = None

def get_parser_instance():
    global lark
    if lark is None:
        lark = Lark.open("hanfor_boogie_grammar.lark", rel_to=__file__, start='exprcommastar', parser='lalr',
                         propagate_positions=True)
    return lark


def replace_var_in_expression(expression, old_var, new_var, parser=None, matching_terminal_names=('ID')):
    """ Replaces all occurrences of old_var in expression with new_var.

    :param matching_terminal_names: Token names according to the grammar taken into account for replacement.
    :type matching_terminal_names: tuple (of strings)
    :param expression: An expression in the grammar used by parser.
    :type expression: str
    :param old_var: Old variable
    :type old_var: str
    :param new_var: New variable
    :type new_var: str
    :param parser: Lark parser
    :type parser: Lark (if not set default parser will be used.)
    :return: Expression with replaced variable.
    :rtype: str
    """
    if parser is None:
        parser = get_parser_instance()
    tree = parser.parse(expression)
    recons = Reconstructor(parser)

    for node in tree.iter_subtrees():  # type: Tree
        #children = []
        #for child in node.children:
        #    if isinstance(child, Token) and child.type in matching_terminal_names and child.value == old_var:
        #        children.append(child.update(value=new_var))
        #    else:
        #        children.append(child)

        #node.set(data=node.data, children=children)

        for child in node.children:
            if isinstance(child, Token) and child.type in matching_terminal_names:
                if child.value == old_var:
                    node.set(data=node.data, children=[Token(child.type, new_var)])

    return recons.reconstruct(tree)


class BoogieType(Enum):
    bool = 1
    int = 2
    real = 3
    unknown = 4
    error = 5

    @staticmethod
    def get_valid_types():
        return [BoogieType.bool, BoogieType.int, BoogieType.real, BoogieType.unknown]

    @staticmethod
    def get_alias_mapping():
        mapping = defaultdict(lambda: BoogieType.unknown)
        for t in BoogieType.get_valid_types():
            mapping[t.name] = t

        mapping['ENUMERATOR_INT'] = BoogieType.int
        mapping['ENUMERATOR_REAL'] = BoogieType.real
        mapping['ENUM_INT'] = BoogieType.int
        mapping['ENUM_REAL'] = BoogieType.real

        return mapping

    @staticmethod
    def get_valid_type_names():
        return BoogieType.get_alias_mapping().keys()

    @staticmethod
    def alias_env_to_instanciated_env(alias_env):
        """ Return a copy of a Boogie type alias environment to a instanciated one

        Args:
            alias_env (dict): {'R': ['bool']}

        Returns (dict): {'R': [BoogieType.bool]}

        """
        result = dict()
        alias_mapping = BoogieType.get_alias_mapping()
        for position in alias_env.keys():
            result[position] = [alias_mapping[alias] for alias in alias_env[position]]

        return result


    @staticmethod
    def aliases(type):
        """ Get allowed name aliases for type

        :param type: BoogieType
        :return: set containing the allowed alias names in hanfor.
        """
        result = {type.name}

        if type in BoogieType.get_alias_mapping().values():
            result |= {alias for alias, alias_type in BoogieType.get_alias_mapping().items() if alias_type == type}

        return result

    @staticmethod
    def reverse_alias(name):

        return BoogieType.get_alias_mapping()[name]

@dataclass(init=True)
class TypeNode:
    expr: str
    t: BoogieType
    type_leaf: list['TypeNode'] = field(default_factory=list)
    children: list['TypeNode'] = field(default_factory=list)

    def __str__(self):
        return self.expr


@v_args(inline=True)
class TypeInference(Transformer):

    def __init__(self, tree: Tree, type_env: dict[str, BoogieType],  expected_types: List[BoogieType] = None):
        super().__init__()
        self.type_env = type_env
        self.type_errors = []
        self.type_root = self.transform(tree)
        if expected_types:
            errors = []
            for possible_type in expected_types:
                errors = self.__propagate_type(self.type_root, possible_type)
                if not errors:
                    break
            self.type_errors += errors

    # Infer leafs (vars, consts)
    def true(self, c: Token) -> TypeNode:
        return TypeNode(c.value, BoogieType.bool, [])

    def false(self, c: Token) -> TypeNode:
        return TypeNode(c.value, BoogieType.bool, [])

    def realnumber(self, c: Token) -> TypeNode:
        return TypeNode(c.value, BoogieType.real, [])

    def number(self, c: Token) -> TypeNode:
        return TypeNode(c.value, BoogieType.int, [])

    def id(self, c: Token) -> TypeNode:
        name = c.value
        if name not in self.type_env:
            self.type_env[name] = BoogieType.unknown
            return TypeNode(name, BoogieType.unknown, [])
        type = self.type_env[name]
        return TypeNode(name, type, [])

    def __typecheck_args(self, arg_type: TypeNode, expected_arg_types: set[BoogieType]) -> list[str]:
        # ignore errors as there is already an error reported and the subsequent errors are noise
        if arg_type.t == BoogieType.unknown or arg_type.t == BoogieType.error:
            return []
        if arg_type.t not in expected_arg_types:
            return [f"Wrong argument type: expected {expected_arg_types} but got {arg_type.t}.",]
        return []

    def __check_unaryop(self, op: Token, c: TypeNode, arg_type: set[BoogieType], return_type: BoogieType = None):
        arg_error = self.__typecheck_args(c, arg_type)
        self.type_errors += arg_error
        type_leaf = [c] + c.type_leaf if not return_type else []
        expr = f"{op} {c.expr}"
        if arg_error:
            return TypeNode(expr, BoogieType.error if not return_type else return_type, type_leaf, [c])
        tn = TypeNode(expr, c.t if not return_type else return_type, type_leaf, [c])
        if len(arg_type) == 1:
            t = arg_type.pop() # TODO: not nice
            self.__propagate_type(c, t)
            arg_type.add(t)
        return tn

    def minus_unary(self, o: Token, c: TypeNode) -> TypeNode:
        return self.__check_unaryop(o, c, {BoogieType.real, BoogieType.int})

    def plus_unary(self, o: Token, c: TypeNode) -> (BoogieType, set[str]):
        return self.__check_unaryop(o, c, {BoogieType.real, BoogieType.int})

    def negation(self, o: Token, c: TypeNode) -> TypeNode:
        return self.__check_unaryop(o, c, {BoogieType.bool}, return_type=BoogieType.bool)

    def __propagate_type(self, tn: TypeNode, t: BoogieType) -> List[str]:
        type_errors = []
        for child in tn.type_leaf + [tn]: # tn is part of its leaf
            if child.t != t and not child.t == BoogieType.unknown:
                type_errors.append(f"Types inconsistent: {child} had Type {tn.t} inferred as {t}")
                child.t = BoogieType.error
                return type_errors
            child.t = t
            if child.expr in self.type_env:
                self.type_env[child.expr] = t
        return type_errors

    # Infer binary operations
    def __check_binaryop(self, c1: TypeNode, op: Token, c2: TypeNode, arg_type: set[BoogieType],
                         return_type: BoogieType = None) -> TypeNode:
        arg_errors = self.__typecheck_args(c1, arg_type) + self.__typecheck_args(c2, arg_type)
        self.type_errors += arg_errors
        expr = f"{c1.expr} {op} {c2.expr}"
        # assume that the return type is the identity if no return type is given, thus all in this leaf are typed equal
        type_leaf = [c1, c2] + c1.type_leaf + c2.type_leaf if not return_type else []
        if arg_errors:
            return TypeNode(expr, BoogieType.error if not return_type else return_type, type_leaf, [c1, c2])
        if c1.t == BoogieType.error or c2.t == BoogieType.error:
            return TypeNode(expr, BoogieType.error if not return_type else return_type, type_leaf, [c1, c2])
        if c1.t == BoogieType.unknown and c2.t == BoogieType.unknown:
            return TypeNode(expr, BoogieType.unknown if not return_type else return_type, type_leaf, [c1, c2])
        if c1.t == c2.t:
            return TypeNode(expr, c1.t if not return_type else return_type, type_leaf, [c1, c2])
        if c1.t != BoogieType.unknown:
            tn = TypeNode(expr, c1.t if not return_type else return_type, type_leaf, [c1, c2])
            errors = self.__propagate_type(c2, c1.t)
            if not errors:
                return tn
            self.type_errors += errors
            return TypeNode(expr, BoogieType.error if not return_type else return_type, type_leaf, [c1, c2])
        if c2.t != BoogieType.unknown:
            tn = TypeNode(expr, c2.t if not return_type else return_type, type_leaf, [c1, c2])
            errors = self.__propagate_type(c1, c2.t)
            if not errors:
                return tn
            self.type_errors += errors
            return TypeNode(expr, BoogieType.error if not return_type else return_type, type_leaf, [c1, c2])
        return TypeNode(expr, BoogieType.error, type_leaf, [c1, c2])

    def neq(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, arg_type={BoogieType.bool, BoogieType.int, BoogieType.real},
                                     return_type=BoogieType.bool)

    def eq(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, arg_type={BoogieType.bool, BoogieType.int, BoogieType.real},
                                     return_type=BoogieType.bool)

    def conjunction(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, arg_type={BoogieType.bool}, return_type=BoogieType.bool)

    def disjunction(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, arg_type={BoogieType.bool}, return_type=BoogieType.bool)

    def divide(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real})

    def explies(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.bool}, return_type=BoogieType.bool)

    def gt(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real}, return_type=BoogieType.bool)

    def gteq(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real}, return_type=BoogieType.bool)

    def iff(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.bool}, return_type=BoogieType.bool)

    def implies(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.bool}, return_type=BoogieType.bool)

    def lt(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real}, return_type=BoogieType.bool)

    def lteq(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real}, return_type=BoogieType.bool)

    def minus(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real})

    def mod(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real})

    def plus(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real})

    def times(self, c1: TypeNode, op: Token, c2: TypeNode) -> TypeNode:
        return self.__check_binaryop(c1, op, c2, {BoogieType.int, BoogieType.real})

    def abs_function(self, o: Token, c1: TypeNode):
        #TODO: replace by abstract handling of functions
        return self.__check_unaryop(o, c1, {BoogieType.int}, return_type=BoogieType.int)

    def __default__(self, data, children, meta):
        if len(children) == 1:
            return children[0]
        self.type_errors += f"Unknown rule {data} found during parsing."
        return TypeNode(data, BoogieType.error, [], children)
