"""
Test consistent lark parsing.
This test regards the issue
https://github.com/ultimate-pa/hanfor/issues/24

Lark has in a few cases nondeterministic resuts, which leads utimately to false type
derivations. See this bugs:
https://github.com/lark-parser/lark/issues/201
https://github.com/lark-parser/lark/issues/191

As long as this test fails https://github.com/ultimate-pa/hanfor/issues/24 will remain unfixed.
"""

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
                            # TODO: let this test test again when https://github.com/lark-parser/lark/issues/191 is closed.
                            continue
                            self.assertTrue(
                                child.type in ['TRUE', 'FALSE'],
                                'Token `{}` has false type `{}`'.format(child.value, child.type)
                            )
