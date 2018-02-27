from unittest import TestCase
import boogie_parsing
from lark.tree import pydot__tree_to_png


class TestReplaceVarInExpression(TestCase):
    def test_parse_real_numbers(self):
        parser = boogie_parsing.get_parser_instance()
        expression = '1.1 < 0.0'
        parsable = True
        try:
            tree = parser.parse(expression)
        except:
            parsable = False
        self.assertEqual(parsable, True)
        # pydot__tree_to_png(tree, "parse_tree.png")
