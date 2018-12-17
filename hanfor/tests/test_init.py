from app import app, api, set_session_config_vars, create_revision
import os
import utils
from unittest import TestCase
from unittest.mock import patch


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

    result = mock_results[count]
    print('Mocked input: {}'.format(result))
    return str(result)


class TestInit(TestCase):
    def setUp(self):
        self.args = utils.HanforArgumentParser(app).parse_args(['test_sessions/test_init/simple.csv', 'simple'])
        app.config['SESSION_BASE_FOLDER'] = 'test_sessions'
        utils.register_assets(app)
        set_session_config_vars(self.args)
        self.app = app.test_client()

    @patch('builtins.input', mock_user_input)
    def test_init_from_csv(self):
        global mock_results
        mock_results = [0, 2, 3, 1]

        create_revision(self.args, None)
