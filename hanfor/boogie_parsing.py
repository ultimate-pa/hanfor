from collections import defaultdict

from enum import Enum
from lark import Lark, Tree
from lark.lexer import Token
from lark.reconstruct import Reconstructor

hanfor_boogie_grammar = r"""
// Expressions
// Start with exprcommastar
?exprcommastar: exprcommaplus?

exprcommaplus: expr
    | exprcommaplus COMMA expr

expr: expr1ni IFF expr
    | expr1

expr1: expr2ni IMPLIES exprimplies
    | exprexpliesni EXPLIES expr2
    | expr2

exprimplies: expr2ni IMPLIES exprimplies
    | expr2

expr2: expr3ni AND exprand
    | expr3ni OR  expror
    | expr3

exprand: expr3ni AND exprand
    | expr3

expror: expr3ni OR expror
    | expr3

expr3: expr4ni LESS expr4
    | expr4ni GREATER expr4
    | expr4ni LTEQ expr4
    | expr4ni GTEQ expr4
    | expr4ni EQ expr4
    | expr4ni NEQ expr4
    | expr4ni PARTORDER expr4
    | expr4

expr4: expr4ni CONCAT expr5
    | expr5

expr5: expr5ni PLUS expr6
    | expr5ni MINUS expr6
    | expr6

expr6: expr6ni TIMES expr7
    | expr6ni DIVIDE expr7
    | expr6ni MOD expr7
    | expr7

expr7: NOT   expr7
    | MINUS expr7
    | expr8

expr8: expr8ni LBKT exprcommaplus RBKT
    | expr8ni LBKT exprcommaplus COLONEQUALS expr RBKT
    | expr8ni NOT ID
    | expr8ni LBKT NUMBER COLON NUMBER RBKT
    | expr9

expr9: FALSE
    | TRUE
    | NUMBER
    | REALNUMBER
    | ID
    | ID LPAR exprcommastar RPAR
    | OLD LPAR expr RPAR
    | IF expr THEN expr ELSE expr 
    | LBRC idsexprcommaplus RBRC
    | LPAR expr RPAR

// expressions  without if-then-else

expr1ni: expr2ni IMPLIES exprimpliesni
    | exprexpliesni EXPLIES expr2ni
    | expr2ni

exprimpliesni: expr2ni IMPLIES exprimpliesni
    | expr2ni

exprexpliesni: exprexpliesni EXPLIES expr2ni
    | expr2ni

expr2ni: expr3ni AND exprandni
    | expr3ni OR  exprorni
    | expr3ni

exprandni: expr3ni AND exprandni
    | expr3ni

exprorni: expr3ni OR exprorni
    | expr3ni

expr3ni: expr4ni LESS expr4ni
    | expr4ni GREATER expr4ni
    | expr4ni LTEQ expr4ni
    | expr4ni GTEQ expr4ni
    | expr4ni EQ expr4ni
    | expr4ni NEQ expr4ni
    | expr4ni PARTORDER expr4ni
    | expr4ni

expr4ni: expr4ni CONCAT expr5ni
    | expr5ni

expr5ni: expr5ni PLUS expr6ni
    | expr5ni MINUS expr6ni
    | expr6ni

expr6ni: expr6ni TIMES expr7ni
    | expr6ni DIVIDE expr7ni
    | expr6ni MOD expr7ni
    | expr7ni

expr7ni: NOT   expr7ni
    | MINUS expr7ni
    | expr8ni

expr8ni: expr8ni LBKT exprcommaplus RBKT
    | expr8ni LBKT exprcommaplus COLONEQUALS expr RBKT
    | expr8ni LBKT NUMBER COLON NUMBER RBKT
    | expr8ni NOT ID
    | expr9ni

expr9ni: FALSE
    | TRUE
    | NUMBER
    | REALNUMBER
    | ID
    | ID LPAR exprcommastar RPAR
    | OLD LPAR expr RPAR
    | LBRC idsexprcommaplus RBRC
    | LPAR expr RPAR

quant: FORALL 
    | EXISTS

idsexprcommaplus: ID COLON expr
    | idsexprcommaplus COMMA ID COLON expr

// Terminals

AND: "&&"
COLON: ":"
COLONEQUALS: ":="
COMMA: ","
CONCAT: "++"
DIVIDE: "/"
ELSE.1: "else"
EQ: "=="
EXISTS.1: "exists"
EXPLIES: "<=="
FALSE.1: "false"
FORALL.1: "forall"
GREATER: ">"
GTEQ: ">="
ID: /[A-Za-z'~#$\^_.?\\][0-9A-Za-z'~#$\^_.?\\]*/
IF.1: "if"
IFF: "<==>"
IMPLIES: "==>"
LBKT: "["
LBRC: "{"
LESS: "<"
LPAR: "("
LTEQ: "<="
MINUS: "-"
MOD: "%"
NEQ: "!="
NOT: "!"
NUMBER: "0" | /[1-9][0-9]*/
OLD.1: "old"
OR: "||"
PARTORDER: "<:"
PLUS: "+"
QSEP: "::"
RBKT: "]"
RBRC: "}"
REALNUMBER: NUMBER "." /[0-9]+/
RPAR: ")"
THEN.1: "then"
TIMES: "*"
TRUE.1: "true"

// Misc
%import common.WS
%ignore WS
"""


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
        lark = Lark(hanfor_boogie_grammar, start='exprcommastar')
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
        for child in node.children:
            if isinstance(child, Token):
                pass
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
                                        "PLUS", "TIMES", "DIVIDE", "MINUS", "MOD", "PLUS", "TIMES"]:
                        op = RealIntOperator(child.type)
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
                               "TIMES", "DIVIDE", "MINUS", "MOD", "PLUS", "TIMES"] or t is not BoogieType.unknown:
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
