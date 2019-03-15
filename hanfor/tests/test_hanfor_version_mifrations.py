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
MOCK_DATA_FOLDER = os.path.join(HERE, 'test_sessions', 'test_hanfor_migrations')
SESSION_BASE_FOLDER = os.path.join(HERE, 'test_sessions', 'tmp')

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
        app.config['LOG_TO_FILE'] = False
        app.config['LOG_LEVEL'] = 'DEBUG'
        utils.register_assets(app)
        utils.setup_logging(app)
        self.clean_folders()
        self.fetch_mock_data()
        self.create_temp_data()
        self.app = app.test_client()
        self.load_expected_result_files()

    @patch('builtins.input', mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results
        global count
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(args, HERE)

    def test_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [self.csv_files[version_slug], VERSION_TAGS[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Get the available requirements.
            initial_req_gets = self.app.get('api/req/gets')
            self.assertEqual(initial_req_gets.json['data'][1]['desc'], 'always look on the bright side of life')
            self.assertListEqual(initial_req_gets.json['data'][1]['tags'], ['unseen'])

    def test_req_file_after_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [self.csv_files[version_slug], VERSION_TAGS[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test generated req_file consistency.
            req_file_content = self.app.get('/api/tools/req_file').data.decode('utf-8').replace('\r\n', '\n')
            self.assertEqual(self.expected_req_files[version_slug], req_file_content)

    def test_csv_file_after_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [self.csv_files[version_slug], VERSION_TAGS[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test generated req_file consistency.
            csv_file_content = self.app.get('/api/tools/csv_file').data.decode('utf-8').replace('\r\n', '\n')
            self.assertEqual(self.expected_csv_files[version_slug], csv_file_content)

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
        try:
            shutil.rmtree(SESSION_BASE_FOLDER)
        except FileNotFoundError:
            pass

    def load_expected_result_files(self):
        self.expected_req_files = dict()
        self.expected_csv_files = dict()

        for version_slug, version_tag in VERSION_TAGS.items():
            with open(os.path.join(MOCK_DATA_FOLDER, version_tag, 'expected_generated_csv.csv')) as f:
                self.expected_csv_files[version_slug] = f.read()
            with open(os.path.join(MOCK_DATA_FOLDER, version_tag, 'expected_generated_req_file.req')) as f:
                self.expected_req_files[version_slug] = f.read()

    def fetch_mock_data(self):
        self.csv_files = dict()

        for version_slug, version_tag in VERSION_TAGS.items():
            self.csv_files[version_slug] = os.path.join(MOCK_DATA_FOLDER, version_tag, 'simple.csv')
