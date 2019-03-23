"""
Test the hanfor version migrations.

"""
import json

from app import app, api, set_session_config_vars, create_revision, user_request_new_revision, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_sessions')
MOCK_DATA_FOLDER = os.path.join(HERE, 'test_delete_variable')
SESSION_BASE_FOLDER = os.path.join(HERE, 'tmp')


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


class TestHanforVersionMigrations(TestCase):
    def setUp(self):
        # Clean test folder.
        app.config['SESSION_BASE_FOLDER'] = SESSION_BASE_FOLDER
        app.config['LOG_TO_FILE'] = False
        app.config['LOG_LEVEL'] = 'DEBUG'
        utils.register_assets(app)
        utils.setup_logging(app)
        self.clean_folders()
        self.create_temp_data()
        self.app = app.test_client()

    @patch('builtins.input', mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results
        global count
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(args, HERE)
        app.config['TEMPLATES_FOLDER'] = os.path.join(HERE, '..', '..', 'templates')

    def test_variable_with_constraint_deletion(self):
        args = utils.HanforArgumentParser(app).parse_args(
            ['simple.csv', 'test_delete_variable']
        )
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        var_gets = self.app.get('api/var/gets')
        self.assertEqual(5, len(var_gets.json['data']))

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print('Create tmp Data for `{}`.'.format(self.__class__.__name__))
        shutil.copytree(MOCK_DATA_FOLDER, SESSION_BASE_FOLDER)

    def clean_folders(self):
        print('Clean test env of test `{}`.'.format(self.__class__.__name__))
        try:
            shutil.rmtree(SESSION_BASE_FOLDER)
        except FileNotFoundError:
            pass