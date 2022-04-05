import re

from enum import IntEnum
from collections import namedtuple

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

class TermBuildingCase(IntEnum):
    EQUALS = 1,
    NOT_EQUALS = 2,
    EQUALS_VALUE = 3,
    NOT_EQUALS_VALUE = 4,
    GT_LT = 5,
    AVAILABLE = 6,
    NOT_AVAILABLE = 7,
    RECEIVED = 8,
    NOT_RECEIVED = 9,
    TIMER = 10

TermBuildingTuple = namedtuple("TermBuildingTuple", ["match", "separator", "term_building_case"])

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

        self.umlaut_replacements = {
            'Ä': 'AE',
            'Ö': 'OE',
            'Ü': 'UE',
            'ä': 'ae',
            'ö': 'oe',
            'ü': 'ue',
        }

        self.term_replacements = {
            ' := ': ' == ',
            '== ->': '==->',
            '==->': '==->',
            '!= ->': '!=',
            '!=->': '!='
        }

        self.term_righthand_side_replacements = {
            '"': '',
            ' ': '_',
            '-': '',
            '(': '',
            ')': '',
            '&': 'AND'
        }

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
                while stack.peek() != "(":
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
        ['x', '== ->', 'y']
        >>> f.expression_to_array("x != -> y")
        ['x', '!= ->', 'y']
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
        ['s_KL_15', '==', '"FALSE"', 'AND', 's_zat_betaetigt', '== ->', '"TRUE"']
        >>> f.expression_to_array('adp_Lichtsensor_Typ != "LIN_REGEN_LICHT_SENSOR"', term_wise=True)
        ['adp_Lichtsensor_Typ != "LIN_REGEN_LICHT_SENSOR"']
        >>> f.expression_to_array('adp_Lichtsensor_Typ != "LIN_REGEN_LICHT_SENSOR"')
        ['adp_Lichtsensor_Typ', '!=', '"LIN_REGEN_LICHT_SENSOR"']


        Function which converts an expression into an arry.
        :param expression:
        :return expression as array, splitted at operators/atoms/brackets:
        """
        # operators we split at.
        # Todo: generate from operators.
        if term_wise:
            pattern = re.compile("([&]{1,2}| OR | AND |[|]{1,2}|\\(|\\))")
        else:
            pattern = re.compile(
                "([&]{1,2}|[|]{1,2}|>=?|<=?|==->?|== ->?|!=->?|!= ->?|<(?!=)|>(?!=)|==(?!->)|!=(?!->)|:=| OR | AND |\\+|(?<!=|&)-|/|\\*|\\||\\(|\\))")

        splitted = re.split(pattern=pattern, string=expression)
        splitted = list(filter(bool, [x.strip() for x in splitted]))
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

    def create_term_building_tuple(self, regex, term, term_building_case, separator_match_group=None, separator=""):
        pair = False
        matcher = re.search(regex, term, re.DOTALL)
        if matcher:
            if not separator and separator is not None:
                separator = matcher.group(separator_match_group)
            pair = TermBuildingTuple(match=re.search(regex, term, re.DOTALL), separator=separator, term_building_case=term_building_case)
        return pair

    def process_term(self, term):
        for key, val in self.term_replacements.items():
            term = term.replace(key, val)

        matchers = list()
        matchers.append(self.create_term_building_tuple(regex=r'(.*)\s*(==)\s*([^\"\s]+).*', term=term,
                                                        term_building_case=TermBuildingCase.EQUALS,
                                                        separator="=="))
        matchers.append(self.create_term_building_tuple(regex=r'(.*)\s*(==)\s*\"(.+)\".*', term=term,
                                                        term_building_case=TermBuildingCase.EQUALS_VALUE,
                                                        separator="=="))
        matchers.append(self.create_term_building_tuple(regex=r'(.*)\s*(!=)\s*([^\"\s]+).*', term=term,
                                                        term_building_case=TermBuildingCase.NOT_EQUALS,
                                                        separator="!="))
        matchers.append(self.create_term_building_tuple(regex=r'(.*)\s*(!=)\s*\"(.+)\".*', term=term,
                                                        term_building_case=TermBuildingCase.NOT_EQUALS_VALUE,
                                                        separator="!="))
        matchers.append(self.create_term_building_tuple(regex=r'(.*)\s(<|>=|>|<=)\s(.*)', term=term,
                                                        term_building_case=TermBuildingCase.GT_LT,
                                                        separator_match_group=2))
        matchers.append(self.create_term_building_tuple(regex=r'(.*) not available', term=term,
                                                        term_building_case=TermBuildingCase.NOT_AVAILABLE))
        matchers.append(self.create_term_building_tuple(regex=r'(.*)(is)* available', term=term,
                                                        term_building_case=TermBuildingCase.AVAILABLE,
                                                        separator=None))
        matchers.append(self.create_term_building_tuple(regex=r'(.*)(is)* received', term=term,
                                                        term_building_case=TermBuildingCase.RECEIVED,
                                                        separator=None))
        matchers.append(self.create_term_building_tuple(regex=r'(.*) not received', term=term,
                                                        term_building_case=TermBuildingCase.NOT_RECEIVED,
                                                        separator=None))
        matchers.append(self.create_term_building_tuple(regex=r'(start|stop) timer (.*)', term=term,
                                                        term_building_case=TermBuildingCase.TIMER,
                                                        separator="=="))

        # make pycharm happy and avoid "might be referenced before assigned"-notifications.
        match = None
        term_building_case = None
        separator = None

        for matcher in matchers:
            if matcher:
                match = matcher.match
                separator = matcher.separator
                term_building_case = matcher.term_building_case

        if not match:
            return None

        # build term according to case.
        # x == y,  x != y
        if term_building_case is TermBuildingCase.EQUALS or term_building_case is TermBuildingCase.NOT_EQUALS:
            lhs = match.group(1).strip()
            rhs = match.group(3).strip().lower()
            for key, val in self.term_righthand_side_replacements.items():
                rhs = rhs.replace(key, val)
            new_term = "%s %s %s" % (lhs, separator, rhs)
        # x == "y",  x != "y"
        elif term_building_case is TermBuildingCase.EQUALS_VALUE or term_building_case is TermBuildingCase.NOT_EQUALS_VALUE:
            lhs = match.group(1).strip()
            rhs = match.group(3).strip().lower()
            for key, val in self.term_righthand_side_replacements.items():
                rhs = rhs.replace(key, val)
            if rhs != "true" and rhs != "false":
                rhs = "%s_%s" % (lhs, rhs.upper())
                new_term = "%s %s %s" % (lhs, separator, rhs)
            elif rhs == "true":
                new_term = "%s" % lhs
            elif rhs == "false":
                new_term = "!%s" % lhs
        # x (is) not available/received
        elif term_building_case is TermBuildingCase.NOT_AVAILABLE or term_building_case is TermBuildingCase.NOT_RECEIVED:
            new_term = "!%s" % match.group(1).strip().replace(" is", "")
        # x (is) available/received
        elif term_building_case is TermBuildingCase.RECEIVED or term_building_case is TermBuildingCase.AVAILABLE:
            new_term = "%s" % match.group(1).strip().replace(" is", "")
        # x >= y, x <= y, x > y, x < y
        elif term_building_case is TermBuildingCase.GT_LT:
            lhs = match.group(1).strip()
            rhs = match.group(3).strip()
            for key, val in self.term_righthand_side_replacements.items():
                rhs = rhs.replace(key, val)
            new_term = "%s %s %s" % (lhs, separator, rhs)
        # start/stop timer
        elif term_building_case is TermBuildingCase.TIMER:
            lhs = match.group(2).strip()
            rhs = 0.0
            new_term = "%s %s %s" % (lhs, separator, rhs)
        else:
            new_term = None

        return new_term

    def process_if_part(self, part, and_logic):
        for key, val in self.umlaut_replacements.items():
            part = part.replace(key, val)
        # parts are one or more lines, *usually* separated by a newline "\n"
        lines = part.strip().split("\n")
        processed_lines = []
        for line in lines:
            # Split each line into an array of terms. We split on AND, OR, ||, &&
            terms_array = self.expression_to_array(line, term_wise=True)
            processed_terms = []
            # Each term is processed
            for term in terms_array:
                if term == 'OR':
                    processed_terms.append(' || ')
                elif term == 'AND':
                    processed_terms.append(' && ')
                else:
                    processed_term = self.process_term(term)
                    if processed_term is not None:
                        processed_terms.append(processed_term)
            if processed_terms:
                processed_lines.append("(" + "".join(processed_terms) + ")")
        if and_logic:
            new_part = "\n&& ".join(processed_lines)
        else:
            new_part = "\n|| ".join(processed_lines)

        return new_part

    def preprocess_part(self, part):
        preprocessed = part
        for key, val in self.umlaut_replacements.items():
            preprocessed = preprocessed.replace(key, val)

        return preprocessed
