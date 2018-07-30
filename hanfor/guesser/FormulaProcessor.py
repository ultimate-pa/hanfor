import re

from enum import IntEnum

class Operator(IntEnum):
    MULTIPLY = 9,
    DIVIDE = 9,
    ADD = 8,
    SUBTRACT = 8,
    LTEQ = 7,
    GTEQ = 7,
    LT = 7,
    GT = 7,
    EQ = 7,
    DOUBLEEQ = 7,
    NOTEQ = 7,
    ASSIGN = 7,
    CHANGES = 7,
    NOTCHANGES = 7,
    AND = 6,
    DOUBLEAND = 6,
    ANDTEXT = 6,
    OR = 5,
    DOUBLEOR = 5,
    ORTEXT = 5

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)



class FormulaProcessor(object):

    def __init__(self):
        self.operators = {
            "+": Operator.ADD,
            "-": Operator.SUBTRACT,
            "*": Operator.MULTIPLY,
            "/": Operator.DIVIDE,
            "<=": Operator.LTEQ,
            ">=": Operator.GTEQ,
            "<": Operator.LT,
            ">": Operator.GT,
            "==": Operator.DOUBLEEQ,
            "!=": Operator.NOTEQ,
            "=": Operator.EQ,
            ":=": Operator.ASSIGN,
            "== ->": Operator.CHANGES,
            "==->": Operator.CHANGES,
            "!=->": Operator.NOTCHANGES,
            "!= ->": Operator.NOTCHANGES,
            "&&": Operator.DOUBLEAND,
            "&": Operator.AND,
            "AND": Operator.ANDTEXT,
            "|": Operator.OR,
            "||": Operator.DOUBLEOR,
            "OR": Operator.ORTEXT,
        }

    def process_formula(self, infix_formula, term_wise=False):
        result = ""
        # convert infix formula into an array
        infix_array = self.expression_to_array(infix_formula, term_wise)
        # convert infix to postfix
        postfix_array = self.infix_to_postfix(infix_array)
        # process postfix.
        processed_posfix_array = self.process_postfix(postfix_array)
        processed_infix = self.postfix_to_infix(processed_posfix_array)

        return processed_infix

    def process_postfix(self, postfix):
        """

        :param postfix:
        :return:
        """


    def infix_to_postfix(self, infix_array):
        """
        Function which converts a given infix expression (in arrayform) to postfix.
        (Shunting yard algorithm)

        >>> f = FormulaProcessor()
        >>> f.infix_to_postfix(['x', '==', 'y'])
        ['x', 'y', '==']
        >>> f.infix_to_postfix(['(','x','==','y',')','&&', 'z'])
        ['x', 'y', '==', 'z', '&&']

        :param infix_array:
        :return postfix_array:
        """

        output = []
        stack = Stack()

        for element in infix_array:
            # handle operators.
            if self.is_operator(element):
                while not stack.isEmpty() and self.is_higher_precedence(element, stack.peek()):
                    output.append(stack.pop())
                stack.push(element)
            # handle left bracket.
            elif element == "(":
                stack.push(element)
            # handle right bracket.
            elif element == ")":
                while stack.peek() is not "(":
                    output.append(stack.pop())
                # digit
                stack.pop()
            else:
                output.append(element)

        while not stack.isEmpty():
            output.append(stack.pop())

        return output

    def postfix_to_infix(self, postfix_array):
        """
        Function which converts a given infix expression (in arrayform) to postfix.
        >>> f = FormulaProcessor()
        >>> post = f.infix_to_postfix(['x', '==', 'y'])
        >>> f.postfix_to_infix(post)
        '(x == y)'
        >>> arr = f.expression_to_array("x==y && z", term_wise=True)
        >>> post = f.infix_to_postfix(arr)
        >>> f.postfix_to_infix(post)
        '(x==y && z)'
        >>> arr = f.expression_to_array("(x==y) && z")
        >>> post = f.infix_to_postfix(arr)
        >>> f.postfix_to_infix(post)
        '((x == y) && z)'


        :param postfix_array:
        :return infix:
        """
        stack = Stack()
        for element in postfix_array:
            if self.is_operator(element):
                operand1 = stack.pop()
                operand2 = stack.pop()
                stack.push("(%s %s %s)" % (operand2, element, operand1))
            else:
                stack.push(element)
        return stack.pop()


    def expression_to_array(self, expression, term_wise=False):
        """
        >>> f = FormulaProcessor()
        >>> f.expression_to_array("x == y")
        ['x', '==', 'y']
        >>> f.expression_to_array("x >= y")
        ['x', '>=', 'y']
        >>> f.expression_to_array("x > y")
        ['x', '>', 'y']
        >>> f.expression_to_array("x + y")
        ['x', '+', 'y']
        >>> f.expression_to_array("x + (-y)")
        ['x', '+', '(', '-', 'y', ')']
        >>> f.expression_to_array("x ==-> y")
        ['x', '==->', 'y']
        >>> f.expression_to_array("x !=-> y")
        ['x', '!=->', 'y']
        >>> f.expression_to_array("x == -> y")
        ['x', '==->', 'y']
        >>> f.expression_to_array("x != -> y")
        ['x', '!=->', 'y']
        >>> f.expression_to_array("x && y", term_wise=True)
        ['x', '&&', 'y']
        >>> f.expression_to_array("x || y",term_wise=True)
        ['x', '||', 'y']
        >>> f.expression_to_array("x + y", term_wise=True)
        ['x + y']
        >>> f.expression_to_array("x OR y OR z", term_wise=True)
        ['x', 'OR', 'y', 'OR', 'z']
        >>> f.expression_to_array('s_KL_15 == "FALSE" AND s_zat_betaetigt == -> "TRUE"', term_wise=True)
        ['s_KL_15 == "FALSE"', 'AND', 's_zat_betaetigt == -> "TRUE"']
        >>> f.expression_to_array('s_KL_15 == "FALSE" AND s_zat_betaetigt == -> "TRUE"')
        ['s_KL_15', '==', '"FALSE"', 'AND', 's_zat_betaetigt', '==->', '"TRUE"']


        Function which converts an expression into an arry.
        :param expression:
        :return expression as array, splitted at operators/atoms/brackets:
        """
        # operators we split at.
        # Todo: generate from operators.
        if term_wise:
            pattern = re.compile("([&]{1,2}|OR|AND|[|]{1,2}|\\(|\\))")
        else:
            pattern = re.compile(
                "([&]{1,2}|[|]{1,2}|>=?|<=?|==->?|== ->?|!=->?|!= ->?|<(?!=)|>(?!=)|==(?!->)|!=(?!->)|:=|OR|AND|\\+|(?<!=|&)-|/|\\*|\\||\\(|\\))")

        if not term_wise:
            expression = expression.replace(" ","")
        splitted = re.split(pattern=pattern,string=expression)
        splitted = [x.strip() for x in splitted if x is not '']
        return splitted


    def is_operator(self, expr):
        """
        >>> f = FormulaProcessor()
        >>> f.is_operator("==")
        True
        >>> f.is_operator("!")
        False

        :param expression:
        :return True if expression is operator, else False:
        """
        return expr in self.operators.keys()

    def is_higher_precedence(self, op1, op2):
        """
        >>> f = FormulaProcessor()
        >>> f.is_higher_precedence("==", "+")
        False
        >>> f.is_higher_precedence("*", "+")
        True

        :param op1, op2:
        :return True, if precedence(op1) >= precedence(op2):
        """

        if op1 in self.operators and op2 in self.operators:
            return self.operators[op1] >= self.operators[op2]
        else:
            return False

    def process_term(self, term):
        # x == y
        equals = re.search(r'(.*)\s*(==)\s*([^\"\s]+).*',
                           term.replace(" := ", " == ").replace("== ->", "==").replace("==->", "=="), re.DOTALL)
        # x == "lel"
        equals_value = re.search(r'(.*)\s*(==)\s*\"(.+)\".*',
                                 term.replace(" := ", " == ").replace("== ->", "==").replace("==->", "=="), re.DOTALL)
        # x != y
        not_equals = re.search(r'(.*)\s*(!=)\s*([^\"\s]+).*', term.replace("!= ->", "!=").replace("!=->", "!="),
                               re.DOTALL)
        not_equals_value = re.search(r'(.*)\s*(!=)\s*\"(.+)\".*', term.replace("!= ->", "!=").replace("!=->", "!="),
                                     re.DOTALL)
        gt_lt = re.search(r'(.*)\s(<|>=|>|<=)\s(.*)', term, re.DOTALL)
        not_available = re.search(r'(.*) not available', term, re.DOTALL)
        available = re.search(r'(.*)(is)* available', term, re.DOTALL)
        received = re.search(r'(.*)(is)* received', term, re.DOTALL)
        not_received = re.search(r'(.*) not received', term, re.DOTALL)
        timer = re.search(r'(start|stop) timer (.*)', term, re.DOTALL)

        sep = "=="
        case = False

        if equals_value:
            sep = "=="
            case = equals_value
        elif not_equals_value:
            sep = "!="
            case = not_equals_value
        elif equals:
            sep = "=="
            case = equals
        elif not_equals:
            sep = "!="
            case = not_equals
        elif not_available:
            sep = None
            case = not_available
        elif not_received:
            sep = None
            case = not_received
        elif received:
            sep = None
            case = received
        elif available:
            sep = None
            case = available
        elif gt_lt:
            sep = gt_lt.group(2)
            case = gt_lt
        elif timer:
            sep = "=="
            case = timer

        if equals or not_equals:
            LHS = case.group(1).strip()
            RHS = case.group(3).strip().replace('"', '').replace(" ", "_").replace("-", "").lower().replace("(",
                                                                                                            "").replace(
                ")", "").replace("&", "AND")
            new_term = "%s %s %s" % (LHS, sep, RHS)
        elif equals_value or not_equals_value:
            LHS = case.group(1).strip()
            RHS = case.group(3).strip().replace('"', '').replace(" ", "_").replace("-", "_").lower().replace("(",
                                                                                                             "").replace(
                ")", "").replace("&", "AND")
            if RHS != "true" and RHS != "false":
                RHS = "%s_%s" % (LHS, RHS.upper())
                new_term = "%s %s %s" % (LHS, sep, RHS)
            elif RHS == "true":
                new_term = "%s" % (LHS)
            elif RHS == "false":
                new_term = "!%s" % (LHS)
        elif not_available or not_received:
            new_term = "!%s" % case.group(1).strip().replace(" is", "")
        elif received or available:
            new_term = "%s" % case.group(1).strip().replace(" is", "")
        elif gt_lt:
            LHS = case.group(1).strip()
            RHS = case.group(3).strip().replace('"', '').replace(" ", "_").replace("(", "").replace(")", "").replace(
                "&", "AND")
            new_term = "%s %s %s" % (LHS, sep, RHS)
        elif timer:
            LHS = case.group(2).strip()
            RHS = 0.0
            new_term = "%s %s %s" % (LHS, sep, RHS)
        else:
            new_term = None

        return new_term

    def process_if_part(self, part, and_logic):
        lines = part.strip().split("\n")
        processed_lines = []
        for line in lines:
            terms_array = self.expression_to_array(line, term_wise=True)
            print(terms_array)
            processed_terms = []
            for term in terms_array:
                print("term: %s" % term)
                if term == 'OR':
                    processed_terms.append(' || ')
                elif term == 'AND':
                    processed_terms.append(' && ')
                else:
                    processed_term = self.process_term(term)
                    if processed_term is not None:
                        print("processed: %s" % processed_term)
                        processed_terms.append(processed_term)
            if processed_terms:
                processed_lines.append("("+ "".join(processed_terms)+ ")")
        print(processed_lines)
        if and_logic:
            new_part = "\n&& ".join(processed_lines)
        else:
            new_part = "\n|| ".join(processed_lines)

        return new_part
