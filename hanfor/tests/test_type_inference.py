from lark import Tree

import boogie_parsing
from unittest import TestCase

class TestParseExpressions(TestCase):

    def parse(self, code: str) -> Tree:
        parser = boogie_parsing.get_parser_instance()
        return parser.parse(code)

    def test_type_nested_large(self):
        tree = self.parse("(((((b + a) + d) * 23) < 4) && x ==> y )")
        t = boogie_parsing.infere_variable_types(tree, {"a": "?"})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("int", type_env["a"], msg="Error deriving variable type int")
        self.assertEqual("int", type_env["b"], msg="Error deriving variable type int")
        self.assertEqual("int", type_env["d"], msg="Error deriving variable type int")
        self.assertEqual("bool", type_env["x"], msg="Error deriving variable type bool")
        self.assertEqual("bool", type_env["y"], msg="Error deriving variable type bool")
        self.assertEqual("bool", t, msg="Error deriving expression type")

    def test_type_nested_inf(self):
        tree = self.parse("(b + a) + 23")
        t = boogie_parsing.infere_variable_types(tree, {"a": "?"})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")
        self.assertEqual("int", t, msg="Error deriving expression type")

    def test_type_tree_gen(self):
        tree = self.parse("23 + a")
        t = boogie_parsing.infere_variable_types(tree, {})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")
        self.assertEqual("int", t, msg="Error deriving expression type")

    def test_single_prop_must_be_bool(self):
        tree = self.parse("x")
        t = boogie_parsing.infere_variable_types(tree, {})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("bool", type_env["x"], msg="Error deriving expression type")
        self.assertEqual("bool", t, msg="Error deriving expression type")

    def test_single_prop_int(self):
        tree = self.parse("3")
        t = boogie_parsing.infere_variable_types(tree, {})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("int", t, msg="Error deriving int from a NUMBER")

    def test_single_prop_bool(self):
        tree = self.parse("TRUE")
        t = boogie_parsing.infere_variable_types(tree, {})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("bool", t, msg="Error deriving bool from TRUE")

    def test_type_tree_gen2(self):
        tree = self.parse("(23.1 + 47.2 + x) < 44 && (b && a)")
        t = boogie_parsing.infere_variable_types(tree, {"a": "bool", "x": "real"})
        td = t.derive_type()
        t, type_env = t.derive_type()
        self.assertEqual("bool", type_env["b"], msg="Infering bool from mixed expression failed.")
        self.assertEqual("error", type_env["x"], msg="Detecting variable in real/int mixed expression failed.")
        self.assertEqual("bool", t, msg="Error deriving expression type")