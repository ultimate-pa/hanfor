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

grammar = r"""
// Start with expr
?expr: subexpr?

subexpr: ID
    | TRUE

// Terminals
ID: /[A-Za-z'~#$\^_.?\\][0-9A-Za-z'~#$\^_.?\\]*/
TRUE.1: "true"

// Misc
%import common.WS
%ignore WS
"""


class TestParseExpressions(TestCase):
    def test_used_variables(self):
        parsers = [
            Lark(grammar, start='expr') for _ in range(100)
        ]

        for parser in parsers:
            tree = parser.parse('true')
            for node in tree.iter_subtrees():
                for child in node.children:
                    # Variables are called ID in the grammar.
                    if isinstance(child, Token):
                        self.assertTrue(
                            child.type == 'TRUE',
                            'Token `{}` has false type `{}`'.format(child.value, child.type)
                        )
