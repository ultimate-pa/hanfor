from collections import defaultdict

from enum import Enum
from lark import Lark, Tree, Transformer
from lark.lexer import Token
from lark.reconstruct import Reconstructor


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
        lark = Lark.open("hanfor_boogie_grammar.lark", rel_to=__file__, start='exprcommastar', parser='lalr')
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
    unknown = 0
    error = -1

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


class MyTransformer(Transformer):
    def greater(self, args):
        print(args)
        return(Tree("ficken", [arg for arg in args if isinstance(arg, Tree)]))


def infer_variable_types(tree: Tree, type_env: dict):
    class TypeNode:

        def __init__(self):
            self.children = []

        @staticmethod
        def gen_type_tree(tree: Tree, father, type_env: dict):
            op = None
            for child in tree.children:
                if isinstance(child, Token):
                    if child.type in ["AND", "EXPLIES", "IFF", "IMPLIES", "NOT", "OR"]:
                        op = LogicOperator(child.type)
                        father.children.append(op)
                    elif child.type in ["EQ", "GREATER", "GTEQ", "LESS", "LTEQ", "NEQ", "DIVIDE", "MINUS", "MOD",
                                        "PLUS", "TIMES"]:
                        op = RealIntOperator(child.type)
                        father.children.append(op)
                    elif child.type in ["ABS"]:
                        op = FunctionOperator(child.type)
                        father.children.append(op)
            if op is None:
                op = father
            for child in tree.children:
                if isinstance(child, Tree):
                    TypeNode.gen_type_tree(child, op, type_env)
                if isinstance(child, Token):
                    if child.type == "REALNUMBER": op.children.append(Constant(str(child), BoogieType.real))
                    if child.type == "NUMBER": op.children.append(Constant(str(child), BoogieType.int))
                    if child.type == "TRUE": op.children.append(Constant(str(child), BoogieType.bool))
                    if child.type == "FALSE": op.children.append(Constant(str(child), BoogieType.bool))
                    if child.type == "ID":
                        op.children.append(
                            Variable(str(child), type_env[child] if child in type_env else BoogieType.unknown))

        def derive_type(self):
            op_type_env = {}
            t, local, type_env = self.children[0].derive_type(None)
            op_type_env.update(type_env)
            if t is BoogieType.unknown:
                t = BoogieType.bool
            for id in local:
                op_type_env[id] = t
            return t, op_type_env

    class FunctionOperator(TypeNode):
        def __init__(self, op_type):
            super().__init__()
            self.op_type = op_type
            self.return_type = BoogieType.error

        def derive_type(self, next_op):
            op_type_env = {}
            child_types = set()
            locals = set()
            # Get child types and locals for function argument.
            for child in self.children:
                type, local, type_env = child.derive_type(self.op_type)
                op_type_env.update(type_env)
                locals |= local
                child_types |= {type}

            # Derive argument type
            child_types -= {BoogieType.unknown}
            if len(child_types) == 1:
                t = child_types.pop()
            elif len(child_types) == 0 and self.op_type in ["ABS"]:
                # Assume type `int` for ABS function in case of still free argument type.
                t = BoogieType.int
            elif len(child_types) == 0:
                t = BoogieType.unknown
            else:
                t = BoogieType.error

            # Set derived types for locals.
            if t is not BoogieType.unknown:
                for id in locals:
                    op_type_env[id] = t if t is not BoogieType.error else BoogieType.unknown
                locals = set()

            # Handle wrong argument type.
            if self.op_type in ["ABS"] and t is not BoogieType.int:
                t = BoogieType.error

            return t, locals, op_type_env

    class LogicOperator(TypeNode):
        def __init__(self, op_type):
            super().__init__()
            self.op_type = op_type
            self.return_type = BoogieType.error

        def derive_type(self, next_op):
            op_type_env = {}
            child_types = set()
            for child in self.children:
                child_type, local, type_env = child.derive_type(self.op_type)
                op_type_env.update(type_env)
                child_types |= {child_type}
                for id in local:
                    op_type_env[id] = BoogieType.bool
            child_types -= {BoogieType.unknown}
            if len(child_types) == 1:
                t = list(child_types)[0]
            elif len(child_types) == 0:
                t = BoogieType.bool
            else:
                t = BoogieType.error
            return t, set(), op_type_env

    class RealIntOperator(TypeNode):
        def __init__(self, op_type):
            super().__init__()
            self.op_type = op_type
            self.return_type = BoogieType.error

        def derive_type(self, next_op):
            op_type_env = {}
            child_types = set()
            locals = set()
            for child in self.children:
                type, local, type_env = child.derive_type(self.op_type)
                op_type_env.update(type_env)
                locals |= local
                child_types |= {type}
            child_types -= {BoogieType.unknown}
            if len(child_types) == 1:
                t = child_types.pop()
            elif len(child_types) == 0:
                t = BoogieType.unknown
            # elif child_types == {BoogieType.real, BoogieType.int}:  # real + int gets casted to real.
            #     t = BoogieType.real
            else:
                t = BoogieType.error
            if next_op not in ["EQ", "GREATER", "GTEQ", "LESS", "LTEQ", "NEQ", "DIVIDE", "MINUS", "MOD", "PLUS",
                               "TIMES"] or t is not BoogieType.unknown:
                for id in locals:
                    op_type_env[id] = t if t is not BoogieType.error else BoogieType.unknown
                locals = set()
            if self.op_type in ["DIVIDE", "MINUS", "MOD", "PLUS", "TIMES"] or t is BoogieType.error:
                return (t, locals, op_type_env)
            else:
                return (BoogieType.bool, locals, op_type_env)

    class Constant(TypeNode):

        def __init__(self, content, type):
            super().__init__()
            self.type = type
            self.content = content

        def derive_type(self, next_op):
            return self.type, set(), {}

    class Variable(TypeNode):

        def __init__(self, var_name, type):
            super().__init__()

            if type in BoogieType.get_valid_types():
                self.type = type
            else:
                self.type = BoogieType.error
            self.var_name = var_name

        def derive_type(self, next_op):
            # directly dreived type, direct children of the current op, children of a sub-op
            local = {self.var_name} if self.type is BoogieType.unknown else set()
            type_env = {self.var_name: self.type} if self.type is not BoogieType.unknown else set()
            return self.type, local , type_env

    type_node = TypeNode()
    TypeNode.gen_type_tree(tree, type_node, type_env)
    return type_node


class EvilTypeConfusion(Exception):
    def __init__(self, env=None):
        """

        :param env: type environment.
        :type env: dict
        """
        candidates = ''
        if env:
            candidates = 'Error candidates: `{}`.'.format(
                ', '.join([
                    name for name in env.keys() if env[name] == BoogieType.error
                ])
            )
        Exception.__init__(
            self,
            "Error in deriving expression type. {}".format(candidates)
        )
