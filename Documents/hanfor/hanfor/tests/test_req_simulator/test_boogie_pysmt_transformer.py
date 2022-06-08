from unittest import TestCase

from parameterized import parameterized

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer
from reqtransformer import Variable

parser = boogie_parsing.get_parser_instance()


class TestBoogiePysmtTransformer(TestCase):
    variables = {
        'a': Variable('a', 'bool', ''),
        'x': Variable('x', 'int', ''),
        'y': Variable('y', 'real', '')
    }

    @parameterized.expand([
        # Bool
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
        actual = str(BoogiePysmtTransformer(self.variables).transform(parser.parse(test_input)))
        self.assertEqual(expected, actual, msg='Error while transforming boogie expression to pysmt formula.')
