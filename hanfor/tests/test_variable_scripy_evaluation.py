"""
Test the hanfor version migrations.

"""
import json
import sys
import time

import logging

from app import app, api, set_session_config_vars, create_revision, user_request_new_revision, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_sessions')
MOCK_DATA_FOLDER = os.path.join(HERE, 'test_variable_script_evaluations')
SESSION_BASE_FOLDER = os.path.join(HERE, 'tmp')

VERSION_TAGS = {
    '0_0_0': 'simple_0_0_0',
    '1_0_0': 'simple_1_0_0',
}

SCRIPT_EVALUATIONS = {
    '0_0_0': {
        'test_00': {
            'script_config': {'simple_script.sh': ['arg0', 'arg1', 'arg2']},
            'expected_result': 'Results for `simple_script.sh` <br> arg2\n <br>'
        },
        'test_01': {
            'script_config': {'simple_script.sh': ['arg0', 'arg1', '$VAR_NAME']},
            'expected_result': 'Results for `simple_script.sh` <br> $VAR_NAME\n <br>'
        }
    },
    '1_0_0': {
        'test_00': {
            'script_config': {'simple_script.sh': ['arg0', 'arg1', 'arg2']},
            'expected_result': 'Results for `simple_script.sh` <br> arg2\n <br>'
        },
        'test_01': {
            'script_config': {'simple_script.sh': ['arg0', 'arg1', '$VAR_NAME']},
            'expected_result': 'Results for `simple_script.sh` <br> $VAR_NAME\n <br>'
        }
    }
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


class TestVariableScriptEvaluation(TestCase):
    def setUp(self):
        # Clean test folder.
        app.config['SESSION_BASE_FOLDER'] = SESSION_BASE_FOLDER
        app.config['LOG_TO_FILE'] = False
        app.config['LOG_LEVEL'] = 'DEBUG'
        utils.register_assets(app)
        utils.setup_logging(app)
        logging.StreamHandler(sys.stdout)
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
        app.config['TEMPLATES_FOLDER'] = os.path.join(HERE, '..', '..', 'templates')

    def test_simple_script(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [self.csv_files[version_slug], VERSION_TAGS[version_slug]]
            )
            for test_name, settings in SCRIPT_EVALUATIONS[version_slug].items():
                app.config['SCRIPT_EVALUATIONS'] = settings['script_config']
                self.startup_hanfor(args, user_mock_answers=[])
                # Let the background task do its work.
                time.sleep(0.5)
                # Get the available requirements.
                var_gets = self.app.get('api/var/gets')
                self.assertEqual(5, len(var_gets.json['data']))
                for result in var_gets.json['data']:
                    self.assertEqual(
                        settings['expected_result'].replace('$VAR_NAME', result['name']),
                        result['script_results']
                    )

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print('Create tmp Data for `{}`.'.format(self.__class__.__name__))
        src = os.path.join(HERE, 'test_variable_script_evaluations')
        dst = os.path.join(SESSION_BASE_FOLDER)
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
