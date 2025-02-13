"""
Skeleton to test Hanfor API running the actual flask app.

"""

from app import app, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.dirname(os.path.realpath(__file__))
TESTS_BASE_FOLDER = os.path.join(HERE, "test_sessions")

CSV_FILES = {
    "simple": os.path.join(HERE, "test_sessions/test_init/simple.csv"),
    "simple_changed_desc": os.path.join(HERE, "test_sessions/test_init/simple_changed_description.csv"),
}


TEST_TAGS = {
    "simple": "simple",
}


def mock_user_input() -> str:
    """Mocks user input. Returns the mock_results entry at position given by the number of calls.
    :return: mock_results[#of call starting with 0]
    """
    global mock_results  # noqa
    global count  # noqa
    try:
        count += 1
    except:  # noqa
        count = 0

    if count == len(mock_results):
        # Restart after reached the end.
        count = 0

    result = mock_results[count]
    print("Mocked input: {}".format(result))
    return str(result)


class TestHanforApiSkeleton(TestCase):
    def setUp(self):
        # Clean test folder.
        app.config["SESSION_BASE_FOLDER"] = TESTS_BASE_FOLDER
        app.config["LOG_TO_FILE"] = False
        app.config["LOG_LEVEL"] = "DEBUG"
        utils.register_assets(app)
        utils.setup_logging(app)
        self.clean_folders()
        self.app = app.test_client()

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results  # noqa
        global count  # noqa
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(app, args, HERE, no_data_tracing=True)

    def test_new_session_from_csv(self):
        """
        Creates a new session.
        """

        # Create the first initial revision.
        args = utils.HanforArgumentParser(app).parse_args([TEST_TAGS["simple"], "-c", CSV_FILES["simple"]])
        self.startup_hanfor(args, user_mock_answers=[2, 0, 1, 3])
        # Get the available requirements.
        initial_req_gets = self.app.get("api/req/gets")
        self.assertEqual(initial_req_gets.json["data"][1]["desc"], "always look on the bright side of life")
        self.assertListEqual(initial_req_gets.json["data"][1]["tags"], [])

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def clean_folders(self):
        print("Clean test env of test `{}`.".format(self.__class__.__name__))
        try:
            path = os.path.join(TESTS_BASE_FOLDER, "variable_import_sessions.pickle")
            os.remove(path)
        except FileNotFoundError:
            pass
        for tag in TEST_TAGS.values():
            path = os.path.join(TESTS_BASE_FOLDER, tag)
            try:
                shutil.rmtree(path)
                print("Cleaned {}".format(path))
            except FileNotFoundError:
                print("{} already clean".format(path))
