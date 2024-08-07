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

from unittest import TestCase


class TestParseExpressions(TestCase):
    def test_used_variables(self):
        parsers = [
            Lark.open("../hanfor_boogie_grammar.lark", rel_to=__file__, start="exprcommastar", parser="lalr")
            for _ in range(10)
        ]
        expressions = ["true", "false"]
        for parser in parsers:
            for expr in expressions:
                tree = parser.parse(expr)
                for node in tree.iter_subtrees():
                    for child in node.children:
                        # Variables are called ID in the grammar.
                        if isinstance(child, Token):
                            self.assertTrue(
                                child.type in ["TRUE", "FALSE"],
                                "Token `{}` has false type `{}`".format(child.value, child.type),
                            )
