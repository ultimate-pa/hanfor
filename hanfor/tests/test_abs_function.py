"""
Test correct parsing and type derivation of the abs function.
"""

import boogie_parsing
from unittest import TestCase


class TestAbsFunction(TestCase):
    def test_parse_expressions(self):
        parser = boogie_parsing.get_parser_instance()
        expressions = [
            ('abs(-10)', True),
            ('abs(10)', True),
            ('abs(10 + 12)', True),
            ('abs(foo)', True),
            ('abs(foo + 42)', True),
            ('abs(42 - foo)', True),
            ('abs(+-foo)', True),
            ('abs(42 > foo)', False),
            ('abs(42 < foo)', False),
            ('abs()', False),
            ('abs(foo + bar) > 10', True),
            ('abs(bar + foo) == spam', True)
        ]
        for expression, should_be_parseable in expressions:
            is_parseable = True
            try:
                tree = parser.parse(expression)
                # pydot__tree_to_png(tree, "parse_tree.png")
            except Exception as e:
                is_parseable = False
            self.assertEqual(is_parseable, should_be_parseable, msg='Error parsing ' + expression)

    def generic_test_type_inference(self, expression, given_env, expected_env, expected_expression_type):
        """

        Args:
            expression:
            given_env:
            expected_env:
        """
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(expression)
        t = boogie_parsing.infer_variable_types(tree, given_env)
        t, type_env = t.derive_type()
        for var, derived_type in type_env.items():
            self.assertEqual(
                expected_env[var],
                derived_type,
                msg="Error deriving `{}` type for variable `{}`. Derived `{}` instead.".format(
                    expected_env[var],
                    var,
                    derived_type
                )
            )
        self.assertEqual(
            expected_expression_type,
            t,
            msg="Error deriving expression type `{}`. Got `{}` instead.".format(
                expected_expression_type,
                t
            )
        )

    def test_type_inference_for_abs_function_0(self):
        # Given:
        expression = "abs(bar + foo) == spam"
        given_env = {
            "bar": boogie_parsing.BoogieType.int
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int,
            "bar": boogie_parsing.BoogieType.int,
            "spam": boogie_parsing.BoogieType.int,
        }
        expected_expression_type = boogie_parsing.BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_1(self):
        # Given:
        expression = "abs(bar + foo) + baz == spam"
        given_env = {
            "bar": boogie_parsing.BoogieType.int
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int,
            "bar": boogie_parsing.BoogieType.int,
            "spam": boogie_parsing.BoogieType.int,
            "baz": boogie_parsing.BoogieType.int,
        }
        expected_expression_type = boogie_parsing.BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_2(self):
        # Given:
        expression = "abs(bar + foo) == spam"
        given_env = {
            "bar": boogie_parsing.BoogieType.real
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.real,
            "bar": boogie_parsing.BoogieType.real,
            "spam": boogie_parsing.BoogieType.unknown,
        }
        expected_expression_type = boogie_parsing.BoogieType.error

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_3(self):
        # Given:
        expression = "abs(bar + foo) + spam"
        given_env = {
            "bar": boogie_parsing.BoogieType.int
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int,
            "bar": boogie_parsing.BoogieType.int,
            "spam": boogie_parsing.BoogieType.int,
        }
        expected_expression_type = boogie_parsing.BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_4(self):
        # Given:
        expression = "abs(- bar - foo * 5) > spam"
        given_env = {
            "bar": boogie_parsing.BoogieType.int
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int,
            "bar": boogie_parsing.BoogieType.int,
            "spam": boogie_parsing.BoogieType.int,
        }
        expected_expression_type = boogie_parsing.BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_5(self):
        # Given:
        expression = "abs(foo)"
        given_env = {
            "foo": boogie_parsing.BoogieType.int
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int
        }
        expected_expression_type = boogie_parsing.BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_6(self):
        # Given:
        expression = "abs(foo)"
        given_env = {
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int
        }
        expected_expression_type = boogie_parsing.BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_7(self):
        # Given:
        expression = "abs(foo)"
        given_env = {
            "foo": boogie_parsing.BoogieType.real
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.real
        }
        expected_expression_type = boogie_parsing.BoogieType.error

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_8(self):
        # Given:
        expression = "abs(abs(foo))"
        given_env = {
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int
        }
        expected_expression_type = boogie_parsing.BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_9(self):
        # Given:
        expression = "(abs(abs(foo) + bar) > baz) == buz"
        given_env = {
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int,
            "bar": boogie_parsing.BoogieType.int,
            "baz": boogie_parsing.BoogieType.int,
            "buz": boogie_parsing.BoogieType.bool,
        }
        expected_expression_type = boogie_parsing.BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_10(self):
        # Given:
        expression = "abs(abs(foo) + abs(bar + bar) - 10 * 3) > baz"
        given_env = {
            "baz": boogie_parsing.BoogieType.real
        }
        # We expect:
        expected_env = {
            "foo": boogie_parsing.BoogieType.int,
            "bar": boogie_parsing.BoogieType.int,
            "baz": boogie_parsing.BoogieType.real,
        }
        expected_expression_type = boogie_parsing.BoogieType.error

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)