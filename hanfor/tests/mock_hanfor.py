"""
Tests for enum and enumerators.

"""

from app import app, startup_hanfor
import os
import shutil
import utils
from unittest.mock import patch


def mock_user_input(*args, **kwargs) -> str:
    """Mocks user input. Returns the mock_results entry at position given by the number of calls.
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
    print("Mocked input: {}".format(result))
    return str(result)


class MockHanfor:
    def __init__(self, session_tags, test_session_source):
        """

        :param test_session_source: Folder containing the hanfor test data.
        :param session_tags: List of the actual hanfor sessions (session folders) available in test_session_source.
        """
        self.here = os.path.dirname(os.path.realpath(__file__))
        self.test_base_folder = os.path.join(self.here, "test_sessions")
        self.test_session_base_folder = os.path.join(self.here, "test_sessions", "tmp")
        self.session_tags = session_tags
        self.test_session_source = test_session_source
        utils.register_assets(app)
        utils.setup_logging(app)
        self.clean_folders()
        self.create_temp_data()
        self.app = app.test_client()

    def setUp(self):
        # Clean test folder.
        app.config["SESSION_BASE_FOLDER"] = self.test_session_base_folder
        app.config["LOG_TO_FILE"] = False
        app.config["LOG_LEVEL"] = "DEBUG"

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, csv_file, session_tag, user_mock_answers) -> bool:
        global mock_results
        global count
        count = -1

        csv_file = os.path.join(self.test_session_base_folder, session_tag, csv_file)
        args = utils.HanforArgumentParser(app).parse_args([session_tag, "-c", csv_file])
        mock_results = user_mock_answers

        success = startup_hanfor(args, self.here)
        app.config["TEMPLATES_FOLDER"] = os.path.join(self.here, "..", "templates")
        return success

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print("Create tmp Data for `{}`.".format(self.__class__.__name__))
        src = os.path.join(self.here, "test_sessions", self.test_session_source)
        shutil.copytree(src, self.test_session_base_folder)

    def clean_folders(self):
        print("Clean test env of test `{}`.".format(self.__class__.__name__))
        try:
            shutil.rmtree(self.test_session_base_folder)
        except FileNotFoundError:
            print("{} already clean".format(self.test_session_base_folder))
