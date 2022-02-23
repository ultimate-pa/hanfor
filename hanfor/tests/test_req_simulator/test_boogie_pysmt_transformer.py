from unittest import TestCase

from parameterized import parameterized

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer

parser = boogie_parsing.get_parser_instance()


class TestBoogiePysmtTransformer(TestCase):
    @parameterized.expand([
        # Bool
        # TODO: Check this.
        # ('a && a == a', ''),
        ('!a ==> true', '((! a) -> True)'),

        # Int
        ('x + 1 == 2 && x - 1 == 0', '(((x + 1) = 2) & ((x - 1) = 0))'),
        ('x * 2 == 8 && x / 2 == 4', '(((x * 2) = 8) & ((x / 2) = 4))'),
        ('(0 < x || x < 4) && x == 2', '(((0 < x) | (x < 4)) & (x = 2))'),
        ('x >= 0 && x <= 4 && x != 2', '((0 <= x) & ((x <= 4) & (! (x = 2))))'),
        ('x > 0 && x < 2 ==> x == 1', '(((0 < x) & (x < 2)) -> (x = 1))'),

        # Real
        ('y + 1.0 == 2.0 && y - 1.0 == 0.0', '(((y + 1.0) = 2.0) & ((y - 1.0) = 0.0))'),
        ('y * 2.0 == 8.0 && y / 2.0 == 4.0', '(((y * 2.0) = 8.0) & ((y * 1/2) = 4.0))'),
        ('(0.0 < y || y < 4.0) && y == 2.0', '(((0.0 < y) | (y < 4.0)) & (y = 2.0))'),
        ('y >= 0.0 && y <= 4.0 && y != 2.0', '((0.0 <= y) & ((y <= 4.0) & (! (y = 2.0))))'),
        ('y > 0.0 && y < 2.0 ==> y == 1.0', '(((0.0 < y) & (y < 2.0)) -> (y = 1.0))')
    ])
    def test_int_expressions(self, test_input: str, expected: str):
        lark_tree = parser.parse(test_input)
        type, type_env = boogie_parsing.infer_variable_types(lark_tree, {}).derive_type()

        actual = str(BoogiePysmtTransformer(type_env).transform(lark_tree))
        self.assertEqual(expected, actual, msg='Error while transforming boogie expression to pysmt formula.')
