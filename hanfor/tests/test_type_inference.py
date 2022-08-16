"""
Test type inferences using boogie_parsing.
"""
from unittest import TestCase

from lark import Tree

from boogie_parsing import BoogieType, TypeInference, run_typecheck_fixpoint
import boogie_parsing


class TestParseExpressions(TestCase):
    def parse(self, code: str) -> Tree:
        parser = boogie_parsing.get_parser_instance()
        return parser.parse(code)

    def test_type_nested_large(self):
        tree = self.parse("(((((b + a) + d) * 23) < 4) && x ==> y )")
        ti = run_typecheck_fixpoint(tree, {"a": BoogieType.unknown})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.int, type_env["a"], msg="Error deriving variable type int")
        self.assertEqual(BoogieType.int, type_env["b"], msg="Error deriving variable type int")
        self.assertEqual(BoogieType.int, type_env["d"], msg="Error deriving variable type int")
        self.assertEqual(BoogieType.bool, type_env["x"], msg="Error deriving variable type bool")
        self.assertEqual(BoogieType.bool, type_env["y"], msg="Error deriving variable type bool")
        self.assertEqual(BoogieType.bool, t, msg="Error deriving expression type")
        self.assertFalse(errors)

    def test_propagate_error(self):
        tree = self.parse("(b + a) + 23")
        ti = run_typecheck_fixpoint(tree, {"a": BoogieType.real})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.real, type_env["b"], msg="Error deriving real type")
        self.assertEqual(BoogieType.error, t, msg="Error propagating the error type")
        self.assertTrue(errors)

    def test_type_nested_inf(self):
        tree = self.parse("(b + a) + 23 < 47")
        ti = run_typecheck_fixpoint(tree, {"a": BoogieType.unknown})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.int, type_env["a"], msg="Error deriving expression type")
        self.assertEqual(BoogieType.int, type_env["b"], msg="Error deriving expression type")
        self.assertEqual(BoogieType.bool, t, msg="Error deriving expression type")
        self.assertFalse(errors)

    def test_type_tree_gen(self):
        tree = self.parse("23 + a < 2")
        ti = run_typecheck_fixpoint(tree, {})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.int, type_env["a"], msg="Error deriving expression type")
        self.assertEqual(BoogieType.bool, t, msg="Error deriving expression type")
        self.assertFalse(errors)

    def test_single_prop_must_be_bool(self):
        tree = self.parse("x")
        ti = run_typecheck_fixpoint(tree, {}, expected_types=[BoogieType.bool])
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.bool, type_env["x"], msg="Error deriving variable type")
        self.assertEqual(BoogieType.bool, t, msg="Error deriving expression type")
        self.assertFalse(errors)

    def test_single_prop_bool(self):
        tree = self.parse("true")
        ti = run_typecheck_fixpoint(tree, {})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from TRUE")
        self.assertFalse(errors)

    def test_not_expr(self):
        tree = self.parse("!y")
        ti = run_typecheck_fixpoint(tree, {"y": BoogieType.unknown})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from TRUE")
        self.assertEqual(BoogieType.bool, type_env["y"], msg="Error deriving bool from TRUE")
        self.assertFalse(errors)

    def test_not_expr(self):
        for type in [BoogieType.real, BoogieType.int]:
            tree = self.parse("-y")
            ti = run_typecheck_fixpoint(tree, {"y": type}, expected_types=[type])
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(type, t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["y"], msg="Error deriving bool from TRUE")
            self.assertFalse(errors)

    def test_unknown_expr(self):
        tree = self.parse("x == y")
        ti = run_typecheck_fixpoint(tree, {})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from ==")
        self.assertEqual(BoogieType.unknown, type_env["x"], msg="Error deriving 'unknown' as type")
        self.assertEqual(BoogieType.unknown, type_env["y"], msg="Error deriving 'unknown' as type")
        self.assertFalse(errors)

    def test_eq_expr(self):
        for type in [BoogieType.bool, BoogieType.real, BoogieType.int]:
            tree = self.parse("x == y")
            ti = run_typecheck_fixpoint(tree, {"x": type, "y": type}, expected_types=[BoogieType.bool])
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from x == y")
            self.assertEqual(type, type_env["x"], msg=f"Error keeping x: {type} from x == y")
            self.assertEqual(type, type_env["y"], msg=f"Error keeping y: {type} from x == y")
            self.assertFalse(errors)

    def test_neq_expr(self):
        for type in [BoogieType.bool, BoogieType.real, BoogieType.int]:
            tree = self.parse("x != y")
            ti = run_typecheck_fixpoint(tree, {"x": type, "y": type}, expected_types=[BoogieType.bool])
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["y"], msg="Error deriving bool from TRUE")
            self.assertFalse(errors)

    def test_eq_expr_lunknown(self):
        for type in [BoogieType.bool, BoogieType.real, BoogieType.int]:
            tree = self.parse("x == y")
            ti = run_typecheck_fixpoint(tree, {"y": type})
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from x == y")
            self.assertEqual(type, type_env["x"], msg=f"Error deriving x: {type} from x == y")
            self.assertEqual(type, type_env["y"], msg=f"Error keeping y: {type} from x == y")
            self.assertFalse(errors)

    def test_eq_expr_runknown(self):
        for type in [BoogieType.bool, BoogieType.real, BoogieType.int]:
            tree = self.parse("x == y")
            ti = run_typecheck_fixpoint(tree, {"x": type})
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(BoogieType.bool, t, msg="Error deriving bool from x == y")
            self.assertEqual(type, type_env["x"], msg=f"Error keeping x: {type} from x == y")
            self.assertEqual(type, type_env["y"], msg=f"Error deriving y: {type} from x == y")
            self.assertFalse(errors)

    def test_unknown_type(self):
        type = "bllluarg"
        tree = self.parse("x == y")
        ti = run_typecheck_fixpoint(tree, {"x": type})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.bool, t, msg="Error deriving expression type error from unknown type")
        self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
        self.assertEqual(BoogieType.unknown, type_env["y"], msg="Error deriving bool from TRUE")
        self.assertTrue(errors)

    def test_unary_minus_inference(self):
        for type in [BoogieType.real, BoogieType.int]:
            tree = self.parse("(x + a) + (-y - z)")
            ti = run_typecheck_fixpoint(tree, {"x": type})
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(type, t, msg="Error deriving bool from x == y")
            self.assertEqual(type, type_env["x"], msg=f"Error deriving x: {type}")
            self.assertEqual(type, type_env["y"], msg=f"Error keeping y: {type}")
            self.assertEqual(type, type_env["z"], msg=f"Error keeping z: {type}")
            self.assertEqual(type, type_env["a"], msg=f"Error keeping a: {type}")
            self.assertFalse(errors)

    def test_singleton(self):
        for type in [BoogieType.bool, BoogieType.int, BoogieType.real]:
            tree = self.parse("x")
            ti = run_typecheck_fixpoint(tree, {"x": type})
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(type, t, msg=f"Error deriving {type} from single vairable")
            self.assertEqual(type, type_env["x"], msg=f"Error deriving {type} from single vairable")
            self.assertFalse(errors)

    def test_singleton_bad(self):
        # what do we want to do here,
        # error  -> error
        # unknown -> ?
        # bloarg -> error
        for type in [BoogieType.error, "bloarg"]:
            tree = self.parse("x")
            # the type universe may not contain illegal types. Check after retrieval.
            ti = run_typecheck_fixpoint(tree, {"x": type}, expected_types=[BoogieType.bool])
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(BoogieType.error, t, msg="Error deriving bool from TRUE")
            #self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
            self.assertTrue(errors)

    def test_type_tree_gen2(self):
        tree = self.parse("(23.1 + 47.2 + x) < 44 && (b && a)")
        ti = run_typecheck_fixpoint(tree,  {"a": BoogieType.bool, "x": BoogieType.real})
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
        self.assertEqual(BoogieType.bool, type_env["b"], msg="Infering bool from mixed expression failed.")
        self.assertEqual(BoogieType.real, type_env["x"], msg="Detecting variable in real/int mixed expression failed.")
        self.assertEqual(BoogieType.bool, t, msg="Error deriving expression type")
        self.assertTrue(errors)

    def test_illegal_compare(self):
        expr = 'MAX > 2.2'
        initial_type_env = {"MAX": BoogieType.bool}

        tree = self.parse(expr)
        ti = run_typecheck_fixpoint(tree,  initial_type_env)
        t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors

        self.assertEqual(t, BoogieType.bool, f"Failed to keep `{t}` for `{expr}` with type_env: `{initial_type_env}`")
        self.assertTrue(errors)

    def test_numbers(self):
        expressions = [
            'MAX_TIME',
            'MAX_TIME + OFFSET',
            'MAX_TIME - OFFSET',
            'MAX_TIME * OFFSET',
            'MAX_TIME / OFFSET'
        ]
        initial_type_env = {"MAX_TIME": BoogieType.real}

        for expr in expressions:
            tree = self.parse(expr)
            ti = run_typecheck_fixpoint(tree, initial_type_env)
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(
                t,
                BoogieType.real,
                f"Failed deriving `{t}` for `{expr}` with: `{initial_type_env}`. Expected `{BoogieType.real}`."
            )
            self.assertFalse(errors)

    def test_inference_chain(self):
        expressions = [
            'a < b && b < c && c < d && d < e && e < f && f == 0.2',
            'a < b && b < c && c < d && d < e && e < f && f == 23'
        ]
        expected = [
            BoogieType.real,
            BoogieType.int
        ]

        for expr, exp_t in zip(expressions, expected):
            tree = self.parse(expr)
            ti = run_typecheck_fixpoint(tree, {})
            t, type_env, errors = ti.type_root.t, ti.type_env, ti.type_errors
            self.assertEqual(
                t,
                BoogieType.bool,
                f"Failed deriving `{BoogieType.bool}` for `{expr}`."
            )
            for v, vt in type_env.items():
                self.assertEqual(
                    vt,
                    exp_t,
                    f"Failed deriving `{exp_t}` for `{v}`."
                )
            self.assertFalse(errors)