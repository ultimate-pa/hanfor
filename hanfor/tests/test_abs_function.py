"""
Test correct parsing and type derivation of the abs function.
"""

from lib_core import boogie_parsing
from lib_core.boogie_parsing import BoogieType, run_typecheck_fixpoint
from unittest import TestCase


class TestAbsFunction(TestCase):
    def test_parse_expressions(self):
        parser = boogie_parsing.get_parser_instance()
        # TODO: use for testing functions in general, not only abs
        # only used abs at the moment, as this is the only function we have
        # Let the type checker do decide if the function is typed right, not the grammar
        expressions = [
            ("abs(-10)", True),
            ("abs(10)", True),
            ("abs(10 + 12)", True),
            ("abs(foo)", True),
            ("abs(foo + 42)", True),
            ("abs(42 - foo)", True),
            # ('abs(+-foo)', True),
            ("abs(42 > foo)", True),
            ("abs(42 < foo)", True),
            ("abs()", False),
            ("abs(foo + bar) > 10", True),
            ("abs(bar + foo) == spam", True),
            # TODO: ('old(bar) == spam', True)
        ]
        for expression, should_be_parseable in expressions:
            is_parseable = True
            try:
                _ = parser.parse(expression)
                # pydot__tree_to_png(tree, "parse_tree.png")
            except Exception:  # noqa
                is_parseable = False
            self.assertEqual(is_parseable, should_be_parseable, msg=f"Error parsing {expression}")

    def generic_test_type_inference(
        self, expression, given_env, expected_env, expected_expression_type, expected_errors: int = 0
    ):
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(expression)
        ti = run_typecheck_fixpoint(tree, given_env)
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        for var, derived_type in type_env.items():
            self.assertEqual(
                expected_env[var],
                derived_type,
                msg=f"Error deriving `{expected_env[var]}` type for variable `{var}`. "
                f"Derived `{derived_type}` instead.",
            )
        self.assertEqual(
            expected_expression_type,
            t,
            msg=f"Error deriving expression type `{expected_expression_type}`. Got `{t}` instead.",
        )
        self.assertEqual(expected_errors, len(errors))

    def test_type_inference_for_abs_function_0(self):
        expression = "abs(bar + foo) == spam"
        given_env = {"bar": BoogieType.int}
        expected_env = {
            "foo": BoogieType.int,
            "bar": BoogieType.int,
            "spam": BoogieType.int,
        }
        expected_expression_type = BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_1(self):
        # Given:
        expression = "abs(bar + foo) + baz == spam"
        given_env = {"bar": BoogieType.int}
        # We expect:
        expected_env = {
            "foo": BoogieType.int,
            "bar": BoogieType.int,
            "spam": BoogieType.int,
            "baz": BoogieType.int,
        }
        expected_expression_type = BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_2(self):
        # Given:
        expression = "abs(bar + foo) == spam"
        given_env = {"bar": BoogieType.real}
        # We expect:
        expected_env = {
            "foo": BoogieType.real,
            "bar": BoogieType.real,
            "spam": BoogieType.int,
        }
        expected_expression_type = BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type, 1)

    def test_type_inference_for_abs_function_3(self):
        # Given:
        expression = "abs(bar + foo) + spam"
        given_env = {"bar": BoogieType.int}
        # We expect:
        expected_env = {
            "foo": BoogieType.int,
            "bar": BoogieType.int,
            "spam": BoogieType.int,
        }
        expected_expression_type = BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_4(self):
        # Given:
        expression = "abs(- bar - foo * 5) > spam"
        given_env = {"bar": BoogieType.int}
        # We expect:
        expected_env = {
            "foo": BoogieType.int,
            "bar": BoogieType.int,
            "spam": BoogieType.int,
        }
        expected_expression_type = BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_5(self):
        # Given:
        expression = "abs(foo)"
        given_env = {"foo": BoogieType.int}
        # We expect:
        expected_env = {"foo": BoogieType.int}
        expected_expression_type = BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_6(self):
        expression = "abs(foo)"
        given_env = {}
        expected_env = {"foo": BoogieType.int}
        expected_expression_type = BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_7(self):
        # Given:
        expression = "abs(foo)"
        given_env = {"foo": BoogieType.real}
        # We expect:
        expected_env = {
            # type stays if it was not unknown, even if there is an error
            "foo": BoogieType.real
        }
        expected_expression_type = BoogieType.int

        # Run the test
        self.generic_test_type_inference(
            expression, given_env, expected_env, expected_expression_type, expected_errors=1
        )

    def test_type_inference_for_abs_function_8(self):
        # Given:
        expression = "abs(abs(foo))"
        given_env = {}
        # We expect:
        expected_env = {"foo": BoogieType.int}
        expected_expression_type = BoogieType.int

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_9(self):
        # Given:
        expression = "(abs(abs(foo) + bar) > baz) == buz"
        given_env = {}
        # We expect:
        expected_env = {
            "foo": BoogieType.int,
            "bar": BoogieType.int,
            "baz": BoogieType.int,
            "buz": BoogieType.bool,
        }
        expected_expression_type = BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type)

    def test_type_inference_for_abs_function_10(self):
        # Given:
        expression = "abs(abs(foo) + abs(bar + bar) - 10 * 3) > baz"
        given_env = {"baz": BoogieType.real}
        # We expect:
        expected_env = {
            "foo": BoogieType.int,
            "bar": BoogieType.int,
            "baz": BoogieType.real,
        }
        expected_expression_type = BoogieType.bool

        # Run the test
        self.generic_test_type_inference(expression, given_env, expected_env, expected_expression_type, 1)
