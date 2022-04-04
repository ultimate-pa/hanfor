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
        ({'a': 'bool'}, '!a ==> true', '((! a) -> True)'),

        # Int
        ({'x': 'int'}, 'x + 1 == 2 && x - 1 == 0', '(((x + 1) = 2) & ((x - 1) = 0))'),
        ({'x': 'int'}, 'x * 2 == 8 && x / 2 == 4', '(((x * 2) = 8) & ((x / 2) = 4))'),
        ({'x': 'int'}, '(0 < x || x < 4) && x == 2', '(((0 < x) | (x < 4)) & (x = 2))'),
        ({'x': 'int'}, 'x >= 0 && x <= 4 && x != 2', '((0 <= x) & ((x <= 4) & (! (x = 2))))'),
        ({'x': 'int'}, 'x > 0 && x < 2 ==> x == 1', '(((0 < x) & (x < 2)) -> (x = 1))'),

        # Real
        ({'y': 'real'}, 'y + 1.0 == 2.0 && y - 1.0 == 0.0', '(((y + 1.0) = 2.0) & ((y - 1.0) = 0.0))'),
        ({'y': 'real'}, 'y * 2.0 == 8.0 && y / 2.0 == 4.0', '(((y * 2.0) = 8.0) & ((y * 1/2) = 4.0))'),
        ({'y': 'real'}, '(0.0 < y || y < 4.0) && y == 2.0', '(((0.0 < y) | (y < 4.0)) & (y = 2.0))'),
        ({'y': 'real'}, 'y >= 0.0 && y <= 4.0 && y != 2.0', '((0.0 <= y) & ((y <= 4.0) & (! (y = 2.0))))'),
        ({'y': 'real'}, 'y > 0.0 && y < 2.0 ==> y == 1.0', '(((0.0 < y) & (y < 2.0)) -> (y = 1.0))')
    ])
    def test_int_expressions(self, variables: str, test_input: str, expected: str):
        lark_tree = parser.parse(test_input)
        actual = str(BoogiePysmtTransformer(variables).transform(lark_tree))

        self.assertEqual(expected, actual, msg='Error while transforming boogie expression to pysmt formula.')
