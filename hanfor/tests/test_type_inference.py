from unittest import TestCase

from lark import Tree

import boogie_parsing


class TestParseExpressions(TestCase):
    def parse(self, code: str) -> Tree:
        parser = boogie_parsing.get_parser_instance()
        return parser.parse(code)

    def test_type_nested_large(self):
        tree = self.parse("(((((b + a) + d) * 23) < 4) && x ==> y )")
        t = boogie_parsing.infer_variable_types(tree, {"a": "?"})
        t, type_env = t.derive_type()
        self.assertEqual("int", type_env["a"], msg="Error deriving variable type int")
        self.assertEqual("int", type_env["b"], msg="Error deriving variable type int")
        self.assertEqual("int", type_env["d"], msg="Error deriving variable type int")
        self.assertEqual("bool", type_env["x"], msg="Error deriving variable type bool")
        self.assertEqual("bool", type_env["y"], msg="Error deriving variable type bool")
        self.assertEqual("bool", t, msg="Error deriving expression type")

    def test_type_nested_inf(self):
        tree = self.parse("(b + a) + 23")
        t = boogie_parsing.infer_variable_types(tree, {"a": "?"})
        t, type_env = t.derive_type()
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")
        self.assertEqual("int", t, msg="Error deriving expression type")

    def test_type_tree_gen(self):
        tree = self.parse("23 + a")
        t = boogie_parsing.infer_variable_types(tree, {})
        t, type_env = t.derive_type()
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")
        self.assertEqual("int", t, msg="Error deriving expression type")

    def test_single_prop_must_be_bool(self):
        tree = self.parse("x")
        t = boogie_parsing.infer_variable_types(tree, {})
        t, type_env = t.derive_type()
        self.assertEqual("bool", type_env["x"], msg="Error deriving expression type")
        self.assertEqual("bool", t, msg="Error deriving expression type")

    def test_single_prop_int(self):
        tree = self.parse("3")
        t = boogie_parsing.infer_variable_types(tree, {})
        t, type_env = t.derive_type()
        self.assertEqual("int", t, msg="Error deriving int from a NUMBER")

    def test_single_prop_bool(self):
        tree = self.parse("TRUE")
        t = boogie_parsing.infer_variable_types(tree, {})
        t, type_env = t.derive_type()
        self.assertEqual("bool", t, msg="Error deriving bool from TRUE")

    def test_unknown_expr(self):
        tree = self.parse("x == y")
        t = boogie_parsing.infer_variable_types(tree, {})
        t, type_env = t.derive_type()
        self.assertEqual("bool", t, msg="Error deriving bool from TRUE")
        self.assertEqual("?", type_env["x"], msg="Error deriving bool from TRUE")
        self.assertEqual("?", type_env["y"], msg="Error deriving bool from TRUE")

    def test_eq_expr(self):
        for type in ["bool", "real", "int"]:
            tree = self.parse("x == y")
            t = boogie_parsing.infer_variable_types(tree, {"x": type, "y": type})
            t, type_env = t.derive_type()
            self.assertEqual("bool", t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["y"], msg="Error deriving bool from TRUE")

    def test_eq_expr_lunknown(self):
        for type in ["bool", "real", "int"]:
            tree = self.parse("x == y")
            t = boogie_parsing.infer_variable_types(tree, {"y": type})
            t, type_env = t.derive_type()
            self.assertEqual("bool", t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["y"], msg="Error deriving bool from TRUE")

    def test_eq_expr_runknown(self):
        for type in ["bool", "real", "int"]:
            tree = self.parse("x == y")
            t = boogie_parsing.infer_variable_types(tree, {"x": type})
            t, type_env = t.derive_type()
            self.assertEqual("bool", t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["y"], msg="Error deriving bool from TRUE")

    def test_unknown_type(self):
        type = "bllluarg"
        tree = self.parse("x == y")
        t = boogie_parsing.infer_variable_types(tree, {"x": type})
        t, type_env = t.derive_type()
        self.assertEqual("error", t, msg="Error deriving bool from TRUE")
        self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")
        self.assertEqual("?", type_env["y"], msg="Error deriving bool from TRUE")

    def test_singleton(self):
        for type in ["bool", "real", "int"]:
            tree = self.parse("x")
            t = boogie_parsing.infer_variable_types(tree, {"x": type})
            t, type_env = t.derive_type()
            self.assertEqual(type, t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")

    def test_singleton_bad(self):
        for type in ["error", "?", "bloarg"]:
            tree = self.parse("x")
            # the type universe may not contain illegal types. Check after retrieval.
            t = boogie_parsing.infer_variable_types(tree, {"x": type})
            t, type_env = t.derive_type()
            self.assertEqual("error", t, msg="Error deriving bool from TRUE")
            self.assertEqual(type, type_env["x"], msg="Error deriving bool from TRUE")

    def test_type_tree_gen2(self):
        tree = self.parse("(23.1 + 47.2 + x) < 44 && (b && a)")
        t = boogie_parsing.infer_variable_types(tree, {"a": "bool", "x": "real"})
        t, type_env = t.derive_type()
        self.assertEqual("bool", type_env["b"], msg="Infering bool from mixed expression failed.")
        self.assertEqual("error", type_env["x"], msg="Detecting variable in real/int mixed expression failed.")
        self.assertEqual("bool", t, msg="Error deriving expression type")
