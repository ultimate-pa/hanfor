from collections import ChainMap

from lark import Lark, Transformer
from lark.reconstruct import Reconstructor

from guesser.utils import flatten_list


class ReqSyntaxTree(object):
    """
    Syntax Tree which shall represent the description text of a requirement.
    """

    def __init__(self):
        # @formatter:off
        self.grammar = """
        start: statement

        statement : if_then
                  | if_then_else
                  | assign
                  | comparison
                  | arithmetic
                  | atomic
                  | statement_sequence
                  | newline_separated_statements
                  | statement_in_parentheses
                  | comparison_enumvalue
                  | assign_enumvalue
                  | arithmetic_sequence
        
        separated : comparison
                  | arithmetic
                  | assign
                  | atomic
                  | newline_separated_statements
                  | statement_in_parentheses
                  | assign_enumvalue
                  | comparison_enumvalue
                  | set_condition_active
                  | received
                  | not_received
                  | available
                  | not_available
                  
        newline_separated_statements: separated NEWLINE separated
        
        statement_in_parentheses : LPAR statement RPAR 
                                 | LPAR arithmetic RPAR
                                 | LPAR arithmetic_sequence RPAR
        
        if_logic.1 : LPAR IF_LOGIC RPAR
        if_then.1 : IF NEWLINE* if_logic* NEWLINE* if_part NEWLINE* THEN NEWLINE* then_part NEWLINE*
        if_then_else.2 : IF NEWLINE* if_logic* NEWLINE* if_part NEWLINE* THEN NEWLINE* then_part NEWLINE* ELSE  NEWLINE* else_part
        if_part : statement
        then_part: statement
        else_part: statement
        
        assign : ID COLONEQUALS arithmetic 
               | ID COLONEQUALS statement 
        assign_enumvalue : ID COLONEQUALS ENUMVALUE
        
        
        comparison : ID compare_operator atomic
        comparison_enumvalue : ID compare_operator ENUMVALUE
        
        statement_sequence : statement logic_operator statement
        arithmetic_sequence : arithmetic arithmetic_operator arithmetic 
                            | arithmetic_sequence arithmetic_operator arithmetic_sequence
                            | statement_in_parentheses arithmetic_operator statement_in_parentheses
                            | statement_in_parentheses arithmetic_operator arithmetic_sequence
        
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
                   
        atomic: NUMBER UNIT*
              | REALNUMBER UNIT*
              | ID
              
        set_condition_active: SET_CONDITION_ACTIVE ID
        received: ID RECEIVED
        not_received: ID NOT_RECEIVED
        available: ID AVAILABLE
        not_available: ID NOT_AVAILABLE
        err_detected: ERR_DETECTED statement

        // TEMRINALS
        AND: "&&" | "AND"
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
        ID: /[0-9A-Za-z$\^_.?\{\}]+/
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
        IF_LOGIC: "AND-logic" 
                | "AND logic" 
                | "and logic" 
                | "and-logic" 
                | "or-logic" 
                | "OR-logic" 
                | "or logic" 
                | "OR logic"
        UNIT: /[\(\)A-Za-z]+/
        ENUMVALUE : /"[0-9A-Za-z_ ]+"/ | /"[0-9A-Za-z_ ]+/ | /[0-9A-Za-z_ ]+"/
        SET_CONDITION_ACTIVE: /set condition active for /
        RECEIVED: /(is)* received/
        NOT_RECEIVED: /(is)* not received/
        AVAILABLE: /(is)* available/
        NOT_AVAILABLE: /(is)* not available/
        ERR_DETECTED: /Error detected for the corresponding output/
        TEXT: /^([0-9A-Za-z$\^_.?",\(\)-]+ [0-9A-Za-z$\^_.?",\(\)-]+){5,300}/
        

        // Misc

        %import common.WS
        %ignore WS
        %ignore SET_CONDITION_ACTIVE
        %ignore RECEIVED
        %ignore NOT_RECEIVED
        %ignore AVAILABLE
        %ignore NOT_AVAILABLE
        %ignore ERR_DETECTED
        %ignore TEXT
        
        """
        # @formatter:on

        self.parser = Lark(self.grammar)
        self.tree = self.parser.parse("NONE")

    def create_tree(self, text):
        self.tree = self.parser.parse(text)
        return self.tree

    def reconstruct(self):
        return Reconstructor(self.parser).reconstruct(self.tree)


class ReqTransformer(Transformer):
    """
    Transformer, which shall process a ReqSyntaxTree and return a Tree whichs only has one child node,
    this child node contains a dictionary which contains the processed requirement.
    """

    def __init__(self):
        self.req = []
        self.current_part = []
        self.current_logic = "AND-logic"

    @staticmethod
    def statement(args):
        return args

    @staticmethod
    def atomic(args):
        return args[0]

    @staticmethod
    def separated(args):
        return args

    @staticmethod
    def compare_operator(args):
        return args[0]

    @staticmethod
    def arithmetic_operator(args):
        return args[0]

    @staticmethod
    def logic_operator(args):
        return args[0]

    @staticmethod
    def assign_enumvalue(args):
        lhs = args[0]
        sep = args[1]
        rhs = args[2].replace('"', "").upper().strip()
        if rhs == "TRUE":
            transformed = "%s" % lhs
        elif rhs == "FALSE":
            transformed = "!%s" % lhs
        else:
            if isinstance(rhs, list):
                rhs = "%s_%s" % (lhs, " ".join(rhs))
            else:
                rhs = "%s_%s" % (lhs, rhs)
            transformed = "%s %s %s " % (lhs, sep, rhs)
        return transformed

    @staticmethod
    def assign(args):
        transformed = " ".join(list(flatten_list(args)))
        return transformed

    def if_logic(self, args):
        self.current_logic = " ".join(args).replace("(", "").replace(")", "").strip()
        return " ".join(args)

    @staticmethod
    def if_then(args):
        purged = list(filter(lambda elm: isinstance(elm, dict), args))
        merged_dict = dict(ChainMap(*purged))
        return merged_dict

    @staticmethod
    def if_then_else(args):
        purged = list(filter(lambda elm: isinstance(elm, dict), args))
        merged_dict = dict(ChainMap(*purged))
        return merged_dict

    def if_part(self, args):
        return {"if_part": list(flatten_list(args)), "logic": self.current_logic}

    @staticmethod
    def then_part(args):
        return {"then_part": list(flatten_list(args))}

    @staticmethod
    def else_part(args):
        return {"else_part": list(flatten_list(args))}

    @staticmethod
    def comparison(args):
        lhs = args[0]
        rhs = args[2].replace('"', "").upper().strip()
        if rhs == "TRUE":
            transformed = "%s" % lhs
        elif rhs == "FALSE":
            transformed = "!%s" % lhs
        else:
            transformed = " ".join(list(flatten_list(args)))
        return transformed

    @staticmethod
    def comparison_enumvalue(args):
        lhs = args[0]
        sep = args[1]
        rhs = args[2].replace('"', "").upper().strip()
        if rhs == "TRUE":
            transformed = "%s" % lhs
        elif rhs == "FALSE":
            transformed = "!%s" % lhs
        else:
            if isinstance(rhs, list):
                rhs = "%s_%s" % (lhs, " ".join(rhs))
            else:
                rhs = "%s_%s" % (lhs, rhs)
            transformed = "%s %s %s " % (lhs, sep, rhs)
        return transformed

    @staticmethod
    def arithmetic(args):
        transformed = " ".join(list(flatten_list(args)))
        return transformed

    @staticmethod
    def arithmetic_sequence(args):
        return args

    @staticmethod
    def statement_sequence(args):
        return args

    @staticmethod
    def newline_separated_statements(args):
        transformed = []
        for arg in args:
            if isinstance(arg, list):
                transformed.append(arg[0])
        transformed = list(flatten_list(transformed))
        return transformed

    @staticmethod
    def statement_in_parentheses(args):
        transformed = list(flatten_list(args))
        transformed = " ".join(transformed)
        return transformed


# TESTING


if __name__ == "__main__":
    s = ReqSyntaxTree()
    print("########## TREE #########")
    # @formatter:off
    s.create_tree(
        "set condition active for VAR1\n"
        "VAR2 is received\n"
        "VAR3 received\n"
        "VAR4 is not received\n"
        "VAR5 not received\n"
        "VAR6 is available\n"
        "VAR7 available\n"
        "VAR8 is not available\n"
        "VAR9 not available"
    )

    # @formatter:on
    transformer = ReqTransformer()
    new_tree = transformer.transform(s.tree)
    print("########## TRANSFORMED #########")
    print(new_tree)
    from lark.tree import pydot__tree_to_png  # Just a neat utility function

    pydot__tree_to_png(s.tree, "tree.png")
    pydot__tree_to_png(new_tree, "new_tree.png")
