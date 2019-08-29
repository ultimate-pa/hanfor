import json

from tests.mock_hanfor import MockHanfor
from unittest import TestCase


class TestFormalizationProcess(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(
            session_tags=['simple'],
            test_session_source='test_formalization_process'
        )
        self.mock_hanfor.setUp()

    def tearDown(self) -> None:
        self.mock_hanfor.tearDown()

    def test_adding_new_formalization(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])

        # Check if there is only one formalization currently.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertListEqual(result.json['vars'], ['bar', 'foo'])

        # Adding a new (empty) Formalization:
        self.mock_hanfor.app.post('api/req/new_formalization', data={'id': 'SysRS FooXY_42'})
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds', ''])
        self.assertListEqual(result.json['vars'], ['bar', 'foo'])

        # Add content to the Formalization
        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "foo != bar", "S": "", "T": "", "U": ""}
            },
            "1": {
                "id": "1",
                "scope": "BEFORE",
                "pattern": "Existence",
                "expression_mapping": {"P": "the_world_sinks", "Q": "", "R": "spam == ham", "S": "", "T": "", "U": ""}
            }
        }
        self.mock_hanfor.app.post(
            'api/req/update',
            data={
                'id': 'SysRS FooXY_42',
                'row_idx': '0',
                'update_formalization': 'true',
                'tags': '',
                'status': 'Todo',
                'formalizations': json.dumps(update)
            }
        )
        # Check if content is correct.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(
            result.json['formal'],
            [
                'Globally, it is never the case that "foo != bar" holds',
                'Before "the_world_sinks", "spam == ham" eventually holds'
            ]
        )
        self.assertListEqual(result.json['vars'], ['bar', 'foo', 'ham', 'spam', 'the_world_sinks'])

    def test_changing_var_in_formalization(self):
        raise NotImplementedError

    def test_changing_var_name(self):
        raise NotImplementedError

    def test_deleting_a_formalization(self):
        raise NotImplementedError
