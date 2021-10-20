from typing import Any
from unittest import TestCase

from parameterized import parameterized
from lark import Tree
from pysmt.environment import reset_env

import boogie_parsing
from simulator import BoogieToPysmtTransformer


class TestBoogieToPysmtTransformer(TestCase):
    def parse(self, expression: str) -> tuple[Tree, dict[Any, boogie_parsing.BoogieType]]:
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(expression)
        type, type_env = boogie_parsing.infer_variable_types(tree, {}).derive_type()

        return tree, type_env

    @parameterized.expand([
        # Int
        ("x + 1 == 1 && x - 1 == 0", "(((x + 1) = 1) & ((x - 1) = 0))"),
        ("x * 2 == 8 && x / 2 == 4", "(((x * 2) = 8) & ((x / 2) = 4))"),
        ("(0 < x || x < 4) && x == 2", "(((0 < x) | (x < 4)) & (x = 2))"),
        ("x >= 0 && x <= 4 && x != 2", "((0 <= x) & ((x <= 4) & (! (x = 2))))"),
        ("x > 0 && x < 2 ==> x == 1", "(((0 < x) & (x < 2)) -> (x = 1))"),

        # Real
        ("x + 1.0 == 1.0 && x - 1.0 == 0.0", "(((x + 1.0) = 1.0) & ((x - 1.0) = 0.0))"),
        ("x * 2.0 == 8.0 && x / 2.0 == 4.0", "(((x * 2.0) = 8.0) & ((x * 1/2) = 4.0))"),
        ("(0.0 < x || x < 4.0) && x == 2.0", "(((0.0 < x) | (x < 4.0)) & (x = 2.0))"),
        ("x >= 0.0 && x <= 4.0 && x != 2.0", "((0.0 <= x) & ((x <= 4.0) & (! (x = 2.0))))"),
        ("x > 0.0 && x < 2.0 ==> x == 1.0", "(((0.0 < x) & (x < 2.0)) -> (x = 1.0))")
    ])
    def test_int_expressions(self, test_input, expected):
        tree, type_env = self.parse(test_input)

        reset_env()
        actual = str(BoogieToPysmtTransformer(type_env).transform(tree))
        self.assertEqual(expected, actual, msg="Error while transforming boogie expression to pysmt formula.")