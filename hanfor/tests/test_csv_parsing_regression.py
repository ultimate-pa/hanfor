"""
TODO: Add description here
"""
import json

from app import app
import os
import utils
import shutil
from unittest import TestCase
from unittest.mock import patch
from tests.mock_hanfor import startup_hanfor

HERE = os.path.dirname(os.path.realpath(__file__))
TESTS_BASE_FOLDER = os.path.join(HERE, 'test_sessions')
TEST_CSV = os.path.join(HERE, 'test_sessions/test_csv_parsing/csv_parsing.csv')
TEST_TAG = 'csv_parsing'


def mock_user_input(*args, **kwargs) -> str:
    """ Mocks user input. Returns the mock_results entry at position given by the number of calls.
    :return: mock_results[#of call starting with 0]
    """
    global mock_results
    global count
    try:
        count += 1
    except Exception:
        count = 0

    if count == len(mock_results):
        # Restart after reached the end.
        count = 0

    result = mock_results[count]
    print('Mocked input: {}'.format(result))
    return str(result)

class TestCSVParsing(TestCase):

    def setUp(self):
        app.config['SESSION_BASE_FOLDER'] = TESTS_BASE_FOLDER
        utils.register_assets(app)
        self.app = app.test_client()

    @patch('builtins.input', mock_user_input)
    def startup_hanfor(self, args, user_inputs):
        global mock_results
        mock_results = user_inputs

        startup_hanfor(args, HERE)

    def test_1_quotation_marks(self):
        args = utils.HanforArgumentParser(app).parse_args([TEST_TAG, '-c', TEST_CSV])
        self.startup_hanfor(args, [0, 1, 3, 2, 0])
        self.assertTrue(
            os.path.isdir(os.path.join(TESTS_BASE_FOLDER, TEST_TAG)),
            msg='No session folder created.'
        )
        self.assertTrue(
            os.path.isdir(os.path.join(TESTS_BASE_FOLDER, TEST_TAG, 'revision_0')),
            msg='No revision folder created.'
        )

        # Check parsed requirements
        reqs = self.app.get('api/req/gets')
        self.assertEqual('ELS', reqs.json['data'][0]['type'])

    def tearDown(self):
            # Clean test dir.
            self.clean_folders()

    def clean_folders(self):
        print('Clean test env of test `{}`.'.format(self.__class__.__name__))
        try:
            path = os.path.join(TESTS_BASE_FOLDER, 'variable_import_sessions.pickle')
            os.remove(path)
        except FileNotFoundError:
            pass
        path = os.path.join(TESTS_BASE_FOLDER, TEST_TAG)
        try:
            shutil.rmtree(path)
            print('Cleaned {}'.format(path))
        except FileNotFoundError:
            print('{} already clean'.format(path))