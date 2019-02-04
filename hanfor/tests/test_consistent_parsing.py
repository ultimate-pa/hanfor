from lark import Lark
from lark.lexer import Token

import boogie_parsing
from unittest import TestCase


class TestParseExpressions(TestCase):
    def test_used_variables(self):
        parsers = [
            Lark(boogie_parsing.hanfor_boogie_grammar, start='exprcommastar') for _ in range(10)
        ]
        expressions = [
            'true',
            'false'
        ]
        for parser in parsers:
            for expr in expressions:
                tree = parser.parse(expr)
                for node in tree.iter_subtrees():
                    for child in node.children:
                        # Variables are called ID in the grammar.
                        if isinstance(child, Token):
                            self.assertTrue(
                                child.type in ['TRUE', 'FALSE'],
                                'Token `{}` has false type `{}`'.format(child.value, child.type)
                            )
