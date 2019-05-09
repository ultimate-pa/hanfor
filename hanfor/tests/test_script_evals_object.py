"""
Test the replacement of variables in expressions when using boogie_parsing
"""
from collections import defaultdict
from unittest import TestCase
from reqtransformer import ScriptEvals


class TestScriptEvalsObject(TestCase):
    def test_script_eval_initialization(self):
        # Replace a var.
        se = ScriptEvals()

        self.assertEqual(
            defaultdict(defaultdict),
            se.get_concatenated_evals()
        )

    def test_script_eval_update_append(self):
        # Replace a var.
        se = ScriptEvals()
        results = {
            'var_one': 'Result for script_a: Foo',
            'var_two': 'Result for script_a: Foo',
        }
        se.update_evals(results, 'script_a')
        results = {
            'var_one': 'Result for script_b: Bar',
            'var_two': 'Result for script_b: Bar',
        }
        se.update_evals(results, 'script_b')

        self.assertEqual(
            {
                'var_one': 'Result for script_a: Foo Result for script_b: Bar',
                'var_two': 'Result for script_a: Foo Result for script_b: Bar'
            },
            se.get_concatenated_evals()
        )

    def test_script_eval_update(self):
        # Replace a var.
        se = ScriptEvals()
        results = {
            'var_one': 'Result for script_a: Foo',
            'var_two': 'Result for script_a: Foo',
        }
        se.update_evals(results, 'script_a')
        results = {
            'var_one': 'Result for script_a: Bar',
            'var_two': 'Result for script_a: bar',
        }
        se.update_evals(results, 'script_a')

        self.assertEqual(
            {
                'var_one': 'Result for script_a: Bar',
                'var_two': 'Result for script_a: bar',
            },
            se.get_concatenated_evals()
        )

    def test_script_eval_update_subset(self):
        # Replace a var.
        se = ScriptEvals()
        results = {
            'var_one': 'Result for script_a: Foo',
            'var_two': 'Result for script_a: Foo',
        }
        se.update_evals(results, 'script_a')
        results = {
            'var_one': 'Result for script_a: Bar'
        }
        se.update_evals(results, 'script_a')

        self.assertEqual(
            {
                'var_one': 'Result for script_a: Bar',
                'var_two': 'Result for script_a: Foo',
            },
            se.get_concatenated_evals()
        )
