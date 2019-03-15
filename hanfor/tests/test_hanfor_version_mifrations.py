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

EXPECTED_REQ_FILES = {
    '0_0_0': '''CONST spam_egg IS 1
CONST spam_ham IS 2

Input bar IS unknown
Input foo IS unknown
Input spam IS int

SysRS_FooXY_42_0: Globally, it is never the case that "foo != bar" holds

''',
    '1_0_0': '''CONST spam_egg IS 1
CONST spam_ham IS 2

Input bar IS unknown
Input foo IS unknown
Input spam IS int

SysRS_FooXY_42_0: Globally, it is never the case that "foo != bar" holds

'''
}

EXPECTED_CSV_FILES = {
    '0_0_0': '''id_header,desc_header,formal_header,type_header,Hanfor_Tags
SysRS FooXY_42,"Dont worry, be happy",,req,
SysRS FooXY_91,always look on the bright side of life,,req,unseen
''',
    '1_0_0': '''id_header,desc_header,formal_header,type_header,Hanfor_Tags
SysRS FooXY_42,"Dont worry, be happy",,req,
SysRS FooXY_91,always look on the bright side of life,,req,unseen
'''
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
        self.create_temp_data()
        self.app = app.test_client()

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
                [CSV_FILES[version_slug], VERSION_TAGS[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Get the available requirements.
            initial_req_gets = self.app.get('api/req/gets')
            self.assertEqual(initial_req_gets.json['data'][1]['desc'], 'always look on the bright side of life')
            self.assertListEqual(initial_req_gets.json['data'][1]['tags'], ['unseen'])
            req_file_content = self.app.get('/api/tools/req_file').data.decode('utf-8')
            print(req_file_content)
            print('#'*80)
            print(EXPECTED_REQ_FILES[version_slug])
            self.assertEqual(EXPECTED_REQ_FILES[version_slug], req_file_content)

    def test_req_file_after_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [CSV_FILES[version_slug], VERSION_TAGS[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test generated req_file consistency.
            req_file_content = self.app.get('/api/tools/req_file').data.decode('utf-8')
            self.assertEqual(EXPECTED_REQ_FILES[version_slug], req_file_content)

    def test_csv_file_after_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [CSV_FILES[version_slug], VERSION_TAGS[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test generated req_file consistency.
            csv_file_content = self.app.get('/api/tools/csv_file').data.decode('utf-8')
            self.assertEqual(EXPECTED_CSV_FILES[version_slug], csv_file_content)

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