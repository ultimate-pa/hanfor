"""
Test the replacement of variables in expressions when using boogie_parsing
"""
from unittest import TestCase
import boogie_parsing


class TestReplaceVarInExpression(TestCase):
    def test_replace_var_in_expression(self):
        # Replace a var.
        self.assertEqual(
            boogie_parsing.replace_var_in_expression(
                '!BAR&&DISCARD_SOURCE!=YOLO',
                'BAR',
                'FOO'
            ),
            '!FOO&&DISCARD_SOURCE!=YOLO'
        )
        # Replace a var not in expression.
        self.assertEqual(
            boogie_parsing.replace_var_in_expression(
                '!BAR&&DISCARD_SOURCE!=YOLO',
                'SPAM',
                'FOO'
            ),
            '!BAR&&DISCARD_SOURCE!=YOLO'
        )
        # Replace a var.
        self.assertEqual(
            boogie_parsing.replace_var_in_expression(
                'ASYNCHRONOUS_ROUTING&&(!PDU||!SIGNAL_UPDATE)',
                'PDU',
                'THIS_IS_NEW',
            ),
            'ASYNCHRONOUS_ROUTING&&(!THIS_IS_NEW||!SIGNAL_UPDATE)'
        )
