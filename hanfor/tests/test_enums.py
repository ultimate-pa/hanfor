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
            'api/var/add_new_variable',
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
            'api/var/add_new_variable',
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

    def test_new_int_enumerator_generation(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])

        # Fetch the initial vars.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': 'my_first_enum', 'type': 'ENUM_INT'}
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
                'enumerators': json.dumps([["foo", "12"], ["bar", "11"]])
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

    def test_int_enumerator_renaming(self):
        """Test renaming an enumeration while more than one enum exit."""
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])

        # Fetch the initial vars.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': 'my_first_enum', 'type': 'ENUM_INT'}
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
                'enumerators': json.dumps([["foo", "12"], ["bar", "11"]])
            }
        )
        # Add another enum for populated data structures
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': 'my_second_enum', 'type': 'ENUM_INT'}
        )
        self.assertEqual(response.json['success'], True)
        # We add 2 enumerators for "my_first_enum".
        response = self.mock_hanfor.app.post(
            'api/var/update',
            data={
                'name': 'my_second_enum',
                'name_old': 'my_second_enum',
                'type': 'ENUM_INT',
                'const_val': '',
                'const_val_old': '',
                'type_old': 'ENUM_INT',
                'occurrences': '',
                'constraints': json.dumps({}),
                'updated_constraints': False,
                'enumerators': json.dumps([["fupp", "5"], ["flii", "6"]])
            }
        )
        # Test renaming the first enum
        self.assertEqual(response.json['success'], True)
        response = self.mock_hanfor.app.post(
            'api/var/update',
            data={
                'name': 'my_renamed_enum',
                'name_old': 'my_first_enum',
                'type': 'ENUM_INT',
                'const_val': '',
                'const_val_old': '',
                'type_old': 'ENUM_INT',
                'occurrences': '',
                'constraints': json.dumps({}),
                'updated_constraints': False,
                'enumerators': json.dumps([["foo", "12"], ["bar", "11"]])
            }
        )
        self.assertEqual(response.json['success'], True)

        # We expect the introduced ENUMERATORS are now also in the generated .req file.
        req_file_content = self.mock_hanfor.app.get('/api/tools/req_file').data.decode('utf-8').replace('\r\n', '\n')
        self.assertIn('CONST my_second_enum_fupp IS 5', req_file_content)
        self.assertIn('CONST my_second_enum_flii IS 6', req_file_content)
        self.assertIn('CONST my_renamed_enum_bar IS 11', req_file_content)
        self.assertIn('CONST my_renamed_enum_foo IS 12', req_file_content)
        self.assertNotIn('CONST my_first_enum IS 11', req_file_content)
        self.assertNotIn('CONST my_first_enum IS 12', req_file_content)

    def test_new_real_enumerator_generation(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])

        # Fetch the initial vars.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': 'my_first_enum', 'type': 'ENUM_REAL'}
        )
        self.assertEqual(response.json['success'], True)
        # We add 2 enumerators for "my_first_enum".
        response = self.mock_hanfor.app.post(
            'api/var/update',
            data={
                'name': 'my_first_enum',
                'name_old': 'my_first_enum',
                'type': 'ENUM_REAL',
                'const_val': '',
                'const_val_old': '',
                'type_old': 'ENUM_REAL',
                'occurrences': '',
                'constraints': json.dumps({}),
                'updated_constraints': False,
                'enumerators': json.dumps([["foo", "12.123"], ["bar", "11.123"]])
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
                'type': 'ENUM_REAL',
                'const_val': None,
                'belongs_to_enum': ''
            }
        )
        expected_updated_vars.append(
            {
                'name': 'my_first_enum_foo',
                'used_by': [],
                'type_inference_errors': {},
                'const_val': '12.123',
                'type': 'ENUMERATOR_REAL',
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
                'const_val': '11.123',
                'type': 'ENUMERATOR_REAL',
                'tags': [],
                'constraints': [],
                'script_results': '',
                'belongs_to_enum': 'my_first_enum'
            }
        )

        # We delete one of the added vars
        self.assertCountEqual(updated_vars, expected_updated_vars)

        # We expect the introduced ENUMERATORS are now also in the generated .req file.
        req_file_content = self.mock_hanfor.app.get('/api/tools/req_file').data.decode('utf-8').replace('\r\n', '\n')
        self.assertIn('CONST my_first_enum_bar IS 11.123', req_file_content)
        self.assertIn('CONST my_first_enum_foo IS 12.123', req_file_content)

    def test_get_enumerators(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])

        # Fetch the initial vars.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list

        # We create a new ENUM "my_third_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': 'my_third_enum', 'type': 'ENUM_REAL'}
        )

        self.assertEqual(response.json['success'], True)

        # We add 2 enumerators for "my_third_enum".
        response = self.mock_hanfor.app.post(
            'api/var/update',
            data={
                'name': 'my_third_enum',
                'name_old': 'my_third_enum',
                'type': 'ENUM_REAL',
                'const_val': '',
                'const_val_old': '',
                'type_old': 'ENUM_REAL',
                'occurrences': '',
                'constraints': json.dumps({}),
                'updated_constraints': False,
                'enumerators': json.dumps([["foo", "12.123"], ["bar", "11.123"]])
            }
        )
        self.assertEqual(response.json['success'], True)

        response = self.mock_hanfor.app.get(
            'api/var/get_enumerators',
            data={
                'name': 'my_third_enum'
            }
        )
        self.assertEqual(response.json['enumerators'][0][0], 'my_third_enum_bar')
        self.assertEqual(response.json['enumerators'][1][0], 'my_third_enum_foo')

    def test_delete_var(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])

        # Fetch the initial vars.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list

        # We create a new ENUM "my_third_enum"
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': 'my_third_enum', 'type': 'ENUM_REAL'}
        )

        self.assertEqual(response.json['success'], True)

        # We add 2 enumerators for "my_third_enum".
        response = self.mock_hanfor.app.post(
            'api/var/update',
            data={
                'name': 'my_third_enum',
                'name_old': 'my_third_enum',
                'type': 'ENUM_REAL',
                'const_val': '',
                'const_val_old': '',
                'type_old': 'ENUM_REAL',
                'occurrences': '',
                'constraints': json.dumps({}),
                'updated_constraints': False,
                'enumerators': json.dumps([["foo", "12.123"], ["bar", "11.123"]])
            }
        )
        self.assertEqual(response.json['success'], True)

        # We expect there is an ENUM "my_third_enum" and the 2 enumerators with the correct value.
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        expected_updated_vars = deepcopy(initial_vars)
        expected_updated_vars.append(
            {
                'name': 'my_third_enum',
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
        expected_updated_vars.append(
            {
                'name': 'my_third_enum_foo',
                'used_by': [],
                'type_inference_errors': {},
                'const_val': '12.123',
                'type': 'ENUMERATOR_REAL',
                'tags': [],
                'constraints': [],
                'script_results': '',
                'belongs_to_enum': 'my_third_enum'
            }
        )
        expected_updated_vars.append(
            {
                'name': 'my_third_enum_bar',
                'used_by': [],
                'type_inference_errors': {},
                'const_val': '11.123',
                'type': 'ENUMERATOR_REAL',
                'tags': [],
                'constraints': [],
                'script_results': '',
                'belongs_to_enum': 'my_third_enum'
            }
        )
        self.assertCountEqual(updated_vars, expected_updated_vars)

        # We expect the introduced ENUMERATORS are now also in the generated .req file.
        req_file_content = self.mock_hanfor.app.get('/api/tools/req_file').data.decode('utf-8').replace('\r\n', '\n')
        self.assertIn('CONST my_third_enum_bar IS 11.123', req_file_content)
        self.assertIn('CONST my_third_enum_foo IS 12.123', req_file_content)

        # We remove one of the added vars
        response = self.mock_hanfor.app.post(
            'api/var/del_var',
            data={
                'name': 'my_third_enum_foo'
            }
        )
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']

        expected_updated_vars.remove(
            {
                'name': 'my_third_enum_foo',
                'used_by': [],
                'type_inference_errors': {},
                'const_val': '12.123',
                'type': 'ENUMERATOR_REAL',
                'tags': [],
                'constraints': [],
                'script_results': '',
                'belongs_to_enum': 'my_third_enum'
            }
        )
        self.assertEqual(response.json['success'], True)
        self.assertCountEqual(updated_vars, expected_updated_vars)

        req_file_content = self.mock_hanfor.app.get('/api/tools/req_file').data.decode('utf-8').replace('\r\n', '\n')

        # We expect my_third_enum_bar to be in the generated .req file.
        self.assertIn('CONST my_third_enum_bar IS 11.123', req_file_content)

        # We expect my_third_enum_foo not to be in the generated .req file.
        self.assertNotIn('CONST my_third_enum_foo IS 12.123', req_file_content)

    def test_add_var_with_no_name(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': '', 'type': 'INT'}
        )
        self.assertEqual(response.json['success'], False)
        # todo: Check well-formed input and return the right status code
        # self.assertEqual(response.status_code, 422)

    def test_add_oddly_named_var(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])
        response = self.mock_hanfor.app.post(
            'api/var/add_new_variable', data={'name': '._', 'type': 'INT'}
        )
        self.assertEqual(response.json['success'], False)
        # todo: Check well-formed input and return the right status code
        # self.assertEqual(response.status_code, 422)


    def apply_update(self, update):
        result = self.mock_hanfor.app.post(
            'api/req/update',
            data={
                'id': 'SysRS FooXY_91',
                'row_idx': '1',
                'update_formalization': 'true',
                'tags': json.dumps({"unseen": ""}),
                'status': 'Todo',
                'formalizations': json.dumps(update)
            }
        )
        self.assertEqual('200 OK', result.status)
        self.assertEqual('application/json', result.mimetype)
        return result

    def test_type_inferences_with_enums(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'inference_tests', [])
        # We do tests given the env:
        # {
        #     foo: ENUM_INT,
        #     foo_one: ENUMERATOR_INT,
        #     bar: ENUM_REAL,
        #     bar_one: ENUMERATOR_REAL,
        #     spam_int: INT,
        #     spam_real: REAL,
        #     ham_unknown: unknown,
        #     ham_bool: bool
        # }

        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "", "S": "", "T": "", "U": ""}
            }
        }

        # Expressions with expected type error outcome
        expressions = [
            ("foo > foo_one", {}),
            ("foo == ham_bool", {'0': ['r']}),
            ("foo_one == foo", {}),
            ("foo == bar", {'0': ['r']}),
            ("bar > bar_one", {}),
            ("bar == ham_bool", {'0': ['r']}),
            ("bar_one == foo_one", {'0': ['r']}),
            ("bar == foo_one", {'0': ['r']}),
            ("spam_int + spam_real", {'0': ['r']}),
        ]

        for expression, expected_type_error in expressions:
            update['0']['expression_mapping']['R'] = expression
            update_result = self.apply_update(update)
            self.assertEqual(
                expected_type_error,
                update_result.json['type_inference_errors'],
                expression
            )

    def test_type_inferences_with_enums_new_var(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'inference_tests', [])
        # We do tests given the env:
        # {
        #     foo: ENUM_INT,
        #     foo_one: ENUMERATOR_INT,
        #     bar: ENUM_REAL,
        #     bar_one: ENUMERATOR_REAL,
        #     spam_int: INT,
        #     spam_real: REAL,
        #     ham_unknown: unknown,
        #     ham_bool: bool
        # }

        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "", "S": "", "T": "", "U": ""}
            }
        }

        # We expect there is no ['new_int', 'new_int_1', 'new_real', 'new_real_1'] we are about to create.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list
        for name in [d['name'] for d in initial_vars]:
            self.assertNotIn(name, ['new_int', 'new_int_1', 'new_real', 'new_real_1'])

        # Add the expression "foo == new_int" which should introduce the new variable new_int of type int.
        expression = "foo == new_int"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # Now we expect there is an int "new_int"
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        new_variable = {
            'name': 'new_int',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'int',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(new_variable, updated_vars)

        # Add the expression "foo_one == new_int_1" which should introduce the new variable new_int_1 of type int.
        expression = "foo_one == new_int_1"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # Now we expect there is an int "new_int_1"
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        new_variable = {
            'name': 'new_int_1',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'int',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(new_variable, updated_vars)

        # Add the expression "bar == new_real" which should introduce the new variable new_real of type real.
        expression = "bar == new_real"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # Now we expect there is a real "new_real"
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        new_variable = {
            'name': 'new_real',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'real',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(new_variable, updated_vars)

        # Add the expression "bar_one == new_real_1" which should introduce the new variable new_real_1 of type real.
        expression = "bar_one == new_real_1"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # Now we expect there is a real "new_real_1"
        updated_vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        new_variable = {
            'name': 'new_real_1',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'real',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(new_variable, updated_vars)

    def test_type_inferences_with_enums_existing_var_update_int_enum(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'inference_tests', [])
        # We do tests given the env:
        # {
        #     foo: ENUM_INT,
        #     foo_one: ENUMERATOR_INT,
        #     bar: ENUM_REAL,
        #     bar_one: ENUMERATOR_REAL,
        #     spam_int: INT,
        #     spam_real: REAL,
        #     ham_unknown: unknown,
        #     ham_bool: bool
        # }

        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "", "S": "", "T": "", "U": ""}
            }
        }

        # We expect there is an unknown "ham_unknown"
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': [],
            'script_results': '',
            'type': 'unknown',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

        # Add the expression "foo == new_int" which should introduce the new variable new_int of type int.
        expression = "foo == ham_unknown"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # We expect "ham_unknown" is now int
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'int',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

    def test_type_inferences_with_enums_existing_var_update_int_enumerator(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'inference_tests', [])
        # We do tests given the env:
        # {
        #     foo: ENUM_INT,
        #     foo_one: ENUMERATOR_INT,
        #     bar: ENUM_REAL,
        #     bar_one: ENUMERATOR_REAL,
        #     spam_int: INT,
        #     spam_real: REAL,
        #     ham_unknown: unknown,
        #     ham_bool: bool
        # }

        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "", "S": "", "T": "", "U": ""}
            }
        }

        # We expect there is an unknown "ham_unknown"
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': [],
            'script_results': '',
            'type': 'unknown',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

        # Add the expression "foo == new_int" which should introduce the new variable new_int of type int.
        expression = "foo_one == ham_unknown"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # We expect "ham_unknown" is now int
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'int',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

    def test_type_inferences_with_enums_existing_var_update_real_enum(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'inference_tests', [])
        # We do tests given the env:
        # {
        #     foo: ENUM_INT,
        #     foo_one: ENUMERATOR_INT,
        #     bar: ENUM_REAL,
        #     bar_one: ENUMERATOR_REAL,
        #     spam_int: INT,
        #     spam_real: REAL,
        #     ham_unknown: unknown,
        #     ham_bool: bool
        # }

        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "", "S": "", "T": "", "U": ""}
            }
        }

        # We expect there is an unknown "ham_unknown"
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': [],
            'script_results': '',
            'type': 'unknown',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

        # Add the expression "foo == new_int" which should introduce the new variable new_int of type int.
        expression = "bar == ham_unknown"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # We expect "ham_unknown" is now int
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'real',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

    def test_type_inferences_with_enums_existing_var_update_real_enumerator(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'inference_tests', [])
        # We do tests given the env:
        # {
        #     foo: ENUM_INT,
        #     foo_one: ENUMERATOR_INT,
        #     bar: ENUM_REAL,
        #     bar_one: ENUMERATOR_REAL,
        #     spam_int: INT,
        #     spam_real: REAL,
        #     ham_unknown: unknown,
        #     ham_bool: bool
        # }

        update = {
            "0": {
                "id": "0",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "", "S": "", "T": "", "U": ""}
            }
        }

        # We expect there is an unknown "ham_unknown"
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': [],
            'script_results': '',
            'type': 'unknown',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)

        # Add the expression "foo == new_int" which should introduce the new variable new_int of type int.
        expression = "bar_one == ham_unknown"
        update['0']['expression_mapping']['R'] = expression
        update_result = self.apply_update(update)
        self.assertEqual(
            {},
            update_result.json['type_inference_errors'],
            expression
        )

        # We expect "ham_unknown" is now int
        vars = self.mock_hanfor.app.get('api/var/gets').json['data']
        unknown = {
            'name': 'ham_unknown',
            'tags': [],
            'constraints': [],
            'type_inference_errors': {},
            'used_by': ['SysRS FooXY_91'],
            'script_results': '',
            'type': 'real',
            'const_val': None,
            'belongs_to_enum': ''
        }
        self.assertIn(unknown, vars)
