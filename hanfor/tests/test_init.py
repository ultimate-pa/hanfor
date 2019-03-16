"""
Test initializing a new plain hanfor session from csv.

Init a new session from ./test_sessions/test_init/simple.csv
Check if API api/req/gets returns correct requirements.
"""

from app import app, api, set_session_config_vars, create_revision, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.dirname(os.path.realpath(__file__))
TESTS_BASE_FOLDER = os.path.join(HERE, 'test_sessions')
TEST_CSV = os.path.join(HERE, 'test_sessions/test_init/simple.csv')
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


class TestInit(TestCase):
    def setUp(self):
        app.config['SESSION_BASE_FOLDER'] = TESTS_BASE_FOLDER
        utils.register_assets(app)
        self.app = app.test_client()

    @patch('builtins.input', mock_user_input)
    def startup_hanfor(self, args):
        global mock_results
        mock_results = [2, 0, 1, 3]

        startup_hanfor(args, HERE)

    def test_1_init_from_csv(self):
        args = utils.HanforArgumentParser(app).parse_args([TEST_CSV, TEST_TAG])
        self.startup_hanfor(args)
        self.assertTrue(
            os.path.isdir(os.path.join(TESTS_BASE_FOLDER, TEST_TAG)),
            msg='No session folder created.'
        )
        self.assertTrue(
            os.path.isdir(os.path.join(TESTS_BASE_FOLDER, TEST_TAG, 'revision_0')),
            msg='No revision folder created.'
        )

        # Check contents.
        for file in ['SysRS FooXY_42.pickle', 'SysRS FooXY_91.pickle', 'session_status.pickle']:
            self.assertTrue(
                os.path.exists(os.path.join(TESTS_BASE_FOLDER, TEST_TAG, 'revision_0', file)),
                msg='Missing file: {}'.format(file)
            )

    def test_2_get_requirements(self):
        args = utils.HanforArgumentParser(app).parse_args([TEST_CSV, TEST_TAG])
        self.startup_hanfor(args)
        result = self.app.get('api/req/gets')
        self.maxDiff = None
        desired_reqs = [
            {'formal': [],
             'pattern': 'None',
             'status': 'Todo',
             'pos': 1,
             'revision_diff': {},
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
             'revision_diff': {},
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
        self.assertListEqual(result.json['data'], desired_reqs)

    def tearDown(self):
        # Clean test dir.
        shutil.rmtree(os.path.join(TESTS_BASE_FOLDER, TEST_TAG))
