from app import app, api, set_session_config_vars, create_revision, user_request_new_revision, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.dirname(os.path.realpath(__file__))
TESTS_BASE_FOLDER = os.path.join(HERE, 'test_sessions')
TEST_CSV = os.path.join(HERE, 'test_sessions/test_init/simple.csv')
TEST_CSV_CHANGED_DESCRIPTION = os.path.join(HERE, 'test_sessions/test_init/simple_changed_description.csv')
TEST_TAG = 'simple'


def mock_user_input(*args, **kwargs) -> str:
    """ Mocks user input. Returns the mock_results entry at position given by the number of calls.
    :return: mock_results[#of call starting with 0]
    """
    global mock_results
    global count
    try:
        count += 1
    except:
        count = 0

    if count == len(mock_results):
        # Restart after reached the end.
        count = 0

    result = mock_results[count]
    print('Mocked input: {}'.format(result))
    return str(result)


desired_reqs = [
            {'formal': [],
             'pattern': 'None',
             'status': 'Todo',
             'pos': 1,
             'vars': {},
             'scope': 'None',
             'tags': [],
             'desc': 'Dont worry, be happy',
             'csv_data': {
                 'formal_header': 'Globally, it is never the case, that WORRY holds; Globally, it is always the case, that HAPPY holds.',
                 'id_header': 'SysRS FooXY_42',
                 'type_header': 'req',
                 'desc_header': 'Dont worry, be happy'
             },
             'id': 'SysRS FooXY_42',
             'type_inference_errors': {},
             'type': 'req'
             },
            {'formal': [],
             'status': 'Todo',
             'pattern': 'None',
             'pos': 0,
             'vars': {},
             'scope': 'None',
             'tags': [],
             'desc': 'always look on the bright side of life',
             'csv_data': {
                 'formal_header': 'Globally, it is always the case that POINT_OF_VIEW==BRIGHT_SIDE_OF_LIVE',
                  'id_header': 'SysRS FooXY_91',
                 'type_header': 'req',
                 'desc_header': 'always look on the bright side of life'
             },
             'id': 'SysRS FooXY_91',
             'type_inference_errors': {},
             'type': 'req'
             }
        ]

class TestMigrations(TestCase):
    def setUp(self):
        app.config['SESSION_BASE_FOLDER'] = TESTS_BASE_FOLDER
        utils.register_assets(app)
        self.app = app.test_client()

    @patch('builtins.input', mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results
        global count
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(args, HERE)

    '''
    Test Cases:
    ###########
    Every test case addresses one single requirement.
    New refers to the new CSV.
    Old refers to the State in the old revision.
    '''

    def test_changed_description(self):
        """
        ### Status in old Revision:
        * No formalization

        ### Changes in CSV
        * Changed description of requirement.

        ### Desired state in New Revision:
        * No Formalization
        * Changed description to new one.
        * Add Tag: migrated_description
        * Change Status -> To do.
        """

        # Create the first initial revision.
        args = utils.HanforArgumentParser(app).parse_args([TEST_CSV, TEST_TAG])
        self.startup_hanfor(args, user_mock_answers=[2, 0, 1, 3])
        # Get the available requirements.
        initial_req_gets = self.app.get('api/req/gets')
        self.assertEqual(initial_req_gets.json['data'][1]['desc'], 'always look on the bright side of life')
        self.assertListEqual(initial_req_gets.json['data'][1]['tags'], [])

        # Create the second revision.
        args = utils.HanforArgumentParser(app).parse_args([TEST_CSV_CHANGED_DESCRIPTION, TEST_TAG, '--revision'])
        self.startup_hanfor(args, user_mock_answers=[0, 0])

        # Load the second revision.
        args = utils.HanforArgumentParser(app).parse_args([TEST_CSV_CHANGED_DESCRIPTION, TEST_TAG])
        self.startup_hanfor(args, user_mock_answers=[1])
        # Get available requirements from new revision.
        new_revision_req_gets = self.app.get('api/req/gets')
        self.assertEqual(new_revision_req_gets.json['data'][1]['desc'], 'Mostly look on the bright side of life')
        self.assertListEqual(
            new_revision_req_gets.json['data'][1]['tags'],
            ['description_changed', 'revision_data_changed']
        )
        self.assertListEqual(
            new_revision_req_gets.json['data'][0]['tags'],
            []
        )

    def tearDown(self):
        # Clean test dir.
        shutil.rmtree(os.path.join(TESTS_BASE_FOLDER, TEST_TAG))