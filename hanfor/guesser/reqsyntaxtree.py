from lark import Lark, Transformer
from lark.reconstruct import Reconstructor
from lark.lexer import Token
from lark.tree import Visitor
import itertools
from guesser.utils import flatten_list
from collections import ChainMap


class ReqSyntaxTree(object):
    """
    Syntax Tree which shall represent the description text of a requirement.
    """
    def __init__(self):
        self.grammar = """
        start: statement

        statement : if_then
                  | if_then_else
                  | assign
                  | comparison
                  | arithmetic
                  | atomic
                  | arithmetic_operator
                  | compare_operator 
                  | logic_operator
                  | statement_sequence
                  | newline_separated_statements
                  | statement_in_parentheses
        
        separated : comparison
                  | arithmetic
                  | assign
                  | atomic
                  | newline_separated_statements
                  | statement_in_parentheses
        
        if_logic.1 : LPAR IF_LOGIC RPAR
        if_then : IF if_logic* if_part THEN then_part
        if_then_else : IF IF_LOGIC* if_part THEN then_part ELSE else_part
        if_part : statement
        then_part: statement
        else_part: statement
        assign : ID COLONEQUALS statement
        statement_in_parentheses : LPAR (statement) RPAR
        comparison : ID compare_operator atomic
        statement_sequence : statement logic_operator statement
        compare_operator : EQ 
                         | NEQ 
                         | GREATER 
                         | GTEQ 
                         | LESS 
                         | LTEQ
        arithmetic_operator : DIVIDE 
                            | PLUS 
                            | MINUS 
                            | TIMES
        logic_operator: AND | OR
        arithmetic : ID arithmetic_operator ID 
                   | ID arithmetic_operator NUMBER 
                   | ID arithmetic_operator REALNUMBER
        atomic: NUMBER 
              | REALNUMBER 
              | ID
        
        newline_separated_statements: separated NEWLINE separated


        // TEMRINALS
        AND: "&&"
        COLONEQUALS: ":="
        COMMA: ","
        CONCAT: "++"
        DIVIDE: "/"
        ELSE: "else" | "ELSE"
        EQ: "=="
        EXISTS: "exists"
        EXPLIES: "<=="
        FALSE: "false"
        FORALL: "forall"
        GREATER: ">"
        GTEQ: ">="
        ID: /[0-9A-Za-z"'$\^_.?]+/
        IF: "IF" | "WENN"
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
        OR: "||" | " OR "
        PLUS: "+"
        REALNUMBER: NUMBER "." /[0-9]+/
        RPAR: ")"
        THEN: "THEN" | "DANN"
        TIMES: "*"
        TRUE: "true"
        NEWLINE: /\\n+/
        IF_LOGIC: "AND-logic" | "AND logic" | "and logic" | "and-logic" | "or-logic" | "OR-logic" | "or logic" | "OR logic"

        // Misc

        %import common.WS
        %ignore WS
        """

        self.parser = Lark(self.grammar)
        self.tree = self.parser.parse("NONE")

    def create_tree(self, text):
        self.tree = self.parser.parse(text)
        print(self.tree.pretty())

    def reconstruct(self):
        text = Reconstructor(self.parser).reconstruct(self.tree)
        #print(text)


class ReqTransformer(Transformer):
    """
    Transformer, which shall process a ReqSyntaxTree and return a Tree whichs only has one child node,
    this child node contains a dictionary which contains the processed requirement.
    """
    def __init__(self):
        self.req = []
        self.current_part = []
        self.current_logic = "(AND-logic)"
        self.current_node = ""

    def statement(self,args):
        print(args)
        return args

    def atomic(self,args):
        print("Atomic: ", args)
        return args[0]

    def separated(self,args):
        print("separated: ", args)
        return args

    def compare_operator(self,args):
       # print("Compare_op: ", args)
        return args[0]

    def arithmetic_operator(self,args):
        #print("arthimetic_op: ", args)
        return args[0]

    def logic_operator(self,args):
        #print("arthimetic_op: ", args)
        return args[0]

    def assign(self, args):
        print("assignment", args)
        transformed = " ".join(list(flatten_list(args)))
        print("transformed:", transformed)
        return transformed

    def if_logic(self,args):
        self.current_logic = " ".join(args)
        return " ".join(args)

    def if_then(self,args):
        print("if_then: ", args)
        purged = list(filter(lambda elm: isinstance(elm, dict), args))
        merged_dict = dict(ChainMap(*purged))
        return merged_dict

    def if_then_else(self, args):
        print("if_then_else: ", args)
        purged = list(filter(lambda elm: isinstance(elm, dict), args))
        merged_dict = dict(ChainMap(*purged))
        return merged_dict

    def if_part(self,args):
        print("if_part: ",args)
        return {'if_part' : list(flatten_list(args))}

    def then_part(self,args):
        return {'then_part' : list(flatten_list(args))}

    def else_part(self,args):
        print("else_part: ",args)
        return {'else_part' : list(flatten_list(args))}

    def comparison(self,args):
        print("comparison: ", args)
        transformed = " ".join(args)
        print("transformed:", transformed)
        return transformed

    def arithmetic(self,args):
        print("arithmetic: ", args)
        transformed = " ".join(args)
        print("transformed:", transformed)
        return transformed

    def statement_sequence(self,args):
        print("state sequence: ", args)
        return args

    def newline_separated_statements(self,args):
        print("newline separated: ", args)
        transformed = []
        for arg in args:
            if isinstance(arg,list):
                transformed.append(arg[0])
        transformed = list(flatten_list(transformed))
        print("transformed:", transformed)
        return transformed

    def statement_in_parentheses(self,args):
        print("in_parentheses: ", args)
        transformed = list(flatten_list(args))
        transformed = " ".join(transformed)
        print("transformed:", transformed)
        return transformed


# TESTING



if __name__ == '__main__':
    s = ReqSyntaxTree()
    print("########## TREE #########")
    s.create_tree('IF adp_Lichtsensor_Typ THEN s_hmi_afl_autobahn_aktiv := s_pBAP_ExteriorLight.LightOnHighway.Status ELSE s_hmi_afl_autobahn_aktiv := "FALSE"')
    transformer = ReqTransformer()
    new_tree = transformer.transform(s.tree)
    print("########## TRANSFORMED #########")
    print(new_tree)
    from lark.tree import pydot__tree_to_png  # Just a neat utility function
    pydot__tree_to_png(s.tree, "tree.png")
    pydot__tree_to_png(new_tree, "new_tree.png")