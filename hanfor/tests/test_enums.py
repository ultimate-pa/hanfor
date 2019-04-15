from copy import deepcopy
from unittest import TestCase

from tests.mock_hanfor import MockHanfor


class TestEnums(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(
            session_tags=['simple_enum'],
            test_session_source='test_enums'
        )
        self.mock_hanfor.setUp()

    def tearDown(self) -> None:
        self.mock_hanfor.tearDown()

    def test_new_enum_generation(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple_enum', [])
        # We expect there is no enum we are about to create.
        initial_vars = self.mock_hanfor.app.get('api/var/gets').json['data']  # type: list
        for name in [d['name'] for d in initial_vars]:
            self.assertNotEqual(name, 'my_first_enum')

        # We create a new ENUM "my_first_enum"
        response = self.mock_hanfor.app.post('api/var/add_new_enum', data={'name': 'my_first_enum'})
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
                'type': 'ENUM',
                'const_val': None
            }
        )
        self.assertCountEqual(updated_vars, expected_updated_vars)
