from lark import Tree

import boogie_parsing
from unittest import TestCase

class TestParseExpressions(TestCase):

    def parse(self, code: str) -> Tree:
        parser = boogie_parsing.get_parser_instance()
        return parser.parse(code)

    def test_type_nested_large(self):
        tree = self.parse("(((((b + a) + d) * 23) < 4) && x ==> y )")
        t = boogie_parsing.inifre_variable_types(tree, {"a": "?"})
        td = t.derive_type()
        t, local, type_env = t.derive_type()
        print(type_env)
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")

    def test_type_nested_inf(self):
        tree = self.parse("(b + a) + 23")
        t = boogie_parsing.inifre_variable_types(tree, {"a": "?"})
        td = t.derive_type()
        t, local, type_env = t.derive_type()
        print(type_env)
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")

    def test_type_tree_gen(self):
        tree = self.parse("23 + a")
        t = boogie_parsing.inifre_variable_types(tree, {})
        td = t.derive_type()
        t, local, type_env = t.derive_type()
        print(type_env)
        self.assertEqual("int", type_env["a"], msg="Error deriving expression type")

    def testx_type_tree_gen(self):
        tree = self.parse("(23.1 + 47.2 + x) < 44 && (b && a)")
        t = boogie_parsing.inifre_variable_types(tree, {"a": "bool", "x":"real"})
        td = t.derive_type()
        t, local, type_env = t.derive_type()
        print(type_env)
        self.assertEqual("bool", type_env["b"], msg="Infering bool from mixed expression failed.")