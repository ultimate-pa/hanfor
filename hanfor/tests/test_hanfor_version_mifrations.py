"""
Test the hanfor version migrations.

"""
from app import app, api, set_session_config_vars, create_revision, user_request_new_revision, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.dirname(os.path.realpath(__file__))
SESSION_BASE_FOLDER = os.path.join(HERE, 'test_sessions', 'tmp')


CSV_FILES = {
    '0_0_0': os.path.join(HERE, 'test_sessions', 'test_hanfor_migrations', 'simple_0_0_0', 'simple.csv'),
    '1_0_0': os.path.join(HERE, 'test_sessions', 'test_hanfor_migrations', 'simple_1_0_0', 'simple.csv'),
}


VERSION_TAGS = {
    '0_0_0': 'simple_0_0_0',
    '1_0_0': 'simple_1_0_0',
}


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
        utils.register_assets(app)
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
    
    def test_migration(self):
        pass

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print('Create tmp Data for `{}`.'.format(self.__class__.__name__))
        if not os.path.exists(SESSION_BASE_FOLDER):
            os.makedirs(SESSION_BASE_FOLDER)

        for version in VERSION_TAGS.values():
            src = os.path.join(HERE, 'test_sessions', 'test_hanfor_migrations', version)
            dst = os.path.join(SESSION_BASE_FOLDER, version)
            shutil.copytree(src, dst)

    def clean_folders(self):
        print('Clean test env of test `{}`.'.format(self.__class__.__name__))
