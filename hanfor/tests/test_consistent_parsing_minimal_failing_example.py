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
