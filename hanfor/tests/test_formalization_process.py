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

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertListEqual(result.json['vars'], ['bar', 'foo'])

        # Adding a new (empty) Formalization:
        self.mock_hanfor.app.post('api/req/new_formalization', data={'id': 'SysRS FooXY_42'})
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds',
                                                     '// None, no pattern set'])
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
                'tags': json.dumps({"tag1": "comment 1 with some character", "tag2": "äüö%&/+= coment330+-# chars"}),
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
        self.assertListEqual(result.json['tags'], ["tag1", "tag2", 'unknown_type', 'has_formalization'])
        self.assertDictContainsSubset({"tag1": "comment 1 with some character",
                                       "tag2": "äüö%&/+= coment330+-# chars"}, result.json['tags_comments'])

    def test_changing_var_in_formalization(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertCountEqual(result.json['vars'], ['bar', 'foo'])

        # Check current available variables.
        self.assertCountEqual(result.json['available_vars'], ["spam_ham", "bar", "foo", "spam_egg", "spam"])

        # Change a var in the formalization to a new not available.

        # Add content to the Formalization
        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "foo != bas", "S": "", "T": "", "U": ""}
            }
        }
        self.mock_hanfor.app.post(
            'api/req/update',
            data={
                'id': 'SysRS FooXY_42',
                'row_idx': '0',
                'update_formalization': 'true',
                'tags': json.dumps({}),
                'status': 'Todo',
                'formalizations': json.dumps(update)
            }
        )
        # Check if content is correct.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bas" holds'])
        self.assertCountEqual(result.json['vars'], ['foo', 'bas'])

        # Check current available variables.
        self.assertCountEqual(result.json['available_vars'], ["spam_ham", "bar", "foo", "spam_egg", "spam", "bas"])

    def test_changing_var_name(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertListEqual(result.json['vars'], ['bar', 'foo'])

        # Change the name of foo to bas
        update = {
            "name": "bas",
            "name_old": "foo",
            "type": "unknown",
            "const_val": "",
            "const_val_old": "",
            "type_old": "unknown",
            "occurrences": "SysRS FooXY_42",
            "constraints": "{}",
            "updated_constraints": "true",
            "enumerators": "[]",
            "belongs_to_enum": "",
            "belongs_to_enum_old": ""
        }
        self.mock_hanfor.app.post(
            'api/var/update',
            data=update
        )

        # Check changed formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "bas!=bar" holds'])
        self.assertCountEqual(result.json['vars'], ['bar', 'bas'])

    def test_deleting_a_formalization(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertCountEqual(result.json['vars'], ['bar', 'foo'])

        # Deleting the formalization
        update = {
            "requirement_id": "SysRS FooXY_42",
            "formalization_id": "0"
        }
        self.mock_hanfor.app.post(
            'api/req/del_formalization',
            data=update
        )

        # Check current formalization for `SysRS FooXY_42` now empty
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], [])
        self.assertListEqual(result.json['vars'], [])

    def test_setting_status(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertListEqual(result.json['formal'], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertCountEqual(result.json['vars'], ['bar', 'foo'])

        # Check current available variables.
        self.assertCountEqual(result.json['available_vars'], ["spam_ham", "bar", "foo", "spam_egg", "spam"])

        self.mock_hanfor.app.post(
            'api/req/update',
            data={
                'id': 'SysRS FooXY_42',
                'row_idx': '0',
                'update_formalization': 'true',
                'tags': json.dumps({}),
                'status': 'Done',
                'formalizations': json.dumps({})
            }
        )
        # Check if content is correct.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertEqual(result.json['status'], 'Done')

    def test_multi_update(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])
        result = self.mock_hanfor.app.post(
            'api/req/multi_update',
            data={
                'add_tag': "some-mass-added-tag",
                'remove_tag': "",
                'set_status': "Done",
                'selected_ids': json.dumps(["SysRS FooXY_42", "SysRS FooXY_91"])
            }
        )
        self.assertEqual(result.status, "200 OK")

        # Check if content is correct.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertEqual(result.status, "200 OK")
        self.assertIn("some-mass-added-tag", result.json['tags'])
        self.assertIn("Done", result.json['status'])

        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_91')
        self.assertEqual(result.status, "200 OK")
        self.assertIn("some-mass-added-tag", result.json['tags'])
        self.assertIn("Done", result.json['status'])

        # tests the other way round
        result = self.mock_hanfor.app.post(
            'api/req/multi_update',
            data={
                'add_tag': "",
                'remove_tag': "some-mass-added-tag",
                'set_status': "Todo",
                'selected_ids': json.dumps(["SysRS FooXY_42", "SysRS FooXY_91"])
            }
        )
        self.assertEqual(result.status, "200 OK")

        # Check if content is correct.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertEqual(result.status, "200 OK")
        self.assertEqual([], result.json['tags'])
        self.assertEquals("Todo", result.json['status'])

        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_91')
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(["unseen"], result.json['tags'])
        self.assertEquals("Todo", result.json['status'])

        # test multi updating with no content selected
        result = self.mock_hanfor.app.post(
            'api/req/multi_update',
            data={
                'add_tag': "some-mass-added-tag",
                'remove_tag': "",
                'set_status': "Todo",
                'selected_ids': json.dumps([])
            }
        )
        self.assertEqual(result.status, "200 OK")
        # self.assertEqual(result.json['errormsg'], 'No requirements selected.')
        self.assertEqual(result.json['errormsg'], '')
        self.assertEqual(result.json['success'], True)

        # Check to see the new tag has not been added to the requirements.
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertEqual(result.status, "200 OK")
        self.assertEqual([], result.json['tags'])
        self.assertEquals("Todo", result.json['status'])

        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_91')
        self.assertEqual(["unseen"], result.json['tags'])
        self.assertEqual(result.status, "200 OK")
        self.assertEquals("Todo", result.json['status'])

    def test_get_available_guesses(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])
        result = self.mock_hanfor.app.post(
            'api/req/get_available_guesses',
            data={
                'requirement_id': 'SysRS FooXY_42',
            }
        )
        self.assertEqual(result.status, "200 OK")
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertEqual(result.status, "200 OK")

    def test_add_formalization_from_guess(self):
        result = self.mock_hanfor.app.post(
            'api/req/add_formalization_from_guess',
            data={
                'requirement_id': 'SysRS FooXY_42',
                'scope': 'Globally',
                'pattern': 'It is always the case that if "{R}" holds then "{S}" eventually holds',
                'mapping': '{"R": "", "S": ""}'
            }
        )
        self.assertEqual(result.status, "200 OK")
        result = self.mock_hanfor.app.get('api/req/get?id=SysRS FooXY_42')
        self.assertEqual(result.status, "200 OK")












