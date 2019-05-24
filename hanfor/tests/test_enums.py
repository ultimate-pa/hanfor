import json

from copy import deepcopy
from tests.mock_hanfor import MockHanfor
from unittest import TestCase


class TestEnums(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(
            session_tags=['simple_enum'],
            test_session_source='test_enums'
        )
        self.mock_hanfor.setUp()

    def tearDown(self) -> None:
        self.mock_hanfor.tearDown()

    def test_new_int_enum_generation(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])
        # We expect there is no enum we are about to create.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list
        for name in [d['name'] for d in initial_vars]:
            self.assertNotEqual(name, 'my_first_enum')

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_enum',
            data={'name': 'my_first_enum', 'type': 'ENUM_INT'}
        )
        # We expect the creation to be successful.
        self.assertEqual(response.json['success'], True)
        # Now we expect there is an ENUM "my_first_enum"
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        expected_updated_vars = deepcopy(initial_vars)
        expected_updated_vars.append(
            {
                'name': 'my_first_enum',
                'tags': [],
                'constraints': [],
                'type_inference_errors': {},
                'used_by': [],
                'script_results': '',
                'type': 'ENUM_INT',
                'const_val': None,
                'belongs_to_enum': ''
            }
        )
        self.assertCountEqual(updated_vars, expected_updated_vars)

    def test_new_real_enum_generation(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])
        # We expect there is no enum we are about to create.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list
        for name in [d['name'] for d in initial_vars]:
            self.assertNotEqual(name, 'my_first_enum')

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_enum',
            data={'name': 'my_first_enum', 'type': 'ENUM_REAL'}
        )
        # We expect the creation to be successful.
        self.assertEqual(response.json['success'], True)
        # Now we expect there is an ENUM "my_first_enum"
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        expected_updated_vars = deepcopy(initial_vars)
        expected_updated_vars.append(
            {
                'name': 'my_first_enum',
                'tags': [],
                'constraints': [],
                'type_inference_errors': {},
                'used_by': [],
                'script_results': '',
                'type': 'ENUM_REAL',
                'const_val': None,
                'belongs_to_enum': ''
            }
        )
        self.assertCountEqual(updated_vars, expected_updated_vars)

    def test_new_enumerator_generation(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])

        # Fetch the initial vars.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_enum', data={'name': 'my_first_enum', 'type': 'ENUM_INT'}
        )
        self.assertEqual(response.json['success'], True)
        # We add 2 enumerators for "my_first_enum".
        response = self.mock_hanfor.app.post(
            'api/var/update',
            data={
                'name': 'my_first_enum',
                'name_old': 'my_first_enum',
                'type': 'ENUM_INT',
                'const_val': '',
                'const_val_old': '',
                'type_old': 'ENUM_INT',
                'occurrences': '',
                'constraints': json.dumps({}),
                'updated_constraints': False,
                'enumerators': json.dumps([["foo", "12"],["bar", "11"]])
            }
        )
        self.assertEqual(response.json['success'], True)
        # We expect there is an ENUM "my_first_enum" and the 2 enumerators with the correct value.
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        expected_updated_vars = deepcopy(initial_vars)
        expected_updated_vars.append(
            {
                'name': 'my_first_enum',
                'tags': [],
                'constraints': [],
                'type_inference_errors': {},
                'used_by': [],
                'script_results': '',
                'type': 'ENUM_INT',
                'const_val': None,
                'belongs_to_enum': ''
            }
        )
        expected_updated_vars.append(
            {
                'name': 'my_first_enum_foo',
                'used_by': [],
                'type_inference_errors': {},
                'const_val': '12',
                'type': 'ENUMERATOR_INT',
                'tags': [],
                'constraints': [],
                'script_results': '',
                'belongs_to_enum': 'my_first_enum'
            }
        )
        expected_updated_vars.append(
            {
                'name': 'my_first_enum_bar',
                'used_by': [],
                'type_inference_errors': {},
                'const_val': '11',
                'type': 'ENUMERATOR_INT',
                'tags': [],
                'constraints': [],
                'script_results': '',
                'belongs_to_enum': 'my_first_enum'
            }
        )
        self.assertCountEqual(updated_vars, expected_updated_vars)

        # We expect the introduced ENUMERATORS are now also in the generated .req file.
        req_file_content = self.mock_hanfor.app.get('/api/tools/req_file').data.decode('utf-8').replace('\r\n', '\n')
        self.assertIn('CONST my_first_enum_bar IS 11', req_file_content)
        self.assertIn('CONST my_first_enum_foo IS 12', req_file_content)
