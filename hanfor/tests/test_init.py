"""
Test initializing a new plain hanfor session from csv.

Init a new session from ./test_sessions/test_init/simple.csv
Check if API api/req/gets returns correct requirements.
"""

from app import app, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.dirname(os.path.realpath(__file__))
TESTS_BASE_FOLDER = os.path.join(HERE, "test_sessions")
TEST_CSV = os.path.join(HERE, "test_sessions/test_init/simple.csv")
TEST_TAG = "simple"


def mock_user_input(*args, **kwargs) -> str:
    """Mocks user input. Returns the mock_results entry at position given by the number of calls.
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
    print("Mocked input: {}".format(result))
    return str(result)


class TestInit(TestCase):
    def setUp(self):
        app.config["SESSION_BASE_FOLDER"] = TESTS_BASE_FOLDER
        utils.register_assets(app)
        self.app = app.test_client()

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, args, user_inputs):
        global mock_results
        mock_results = user_inputs

        startup_hanfor(args, HERE, db_test_mode=True)

    def test_1_init_from_csv(self):
        args = utils.HanforArgumentParser(app).parse_args([TEST_TAG, "-c", TEST_CSV])
        self.startup_hanfor(args, [2, 0, 1, 3, 0])
        self.assertTrue(os.path.isdir(os.path.join(TESTS_BASE_FOLDER, TEST_TAG)), msg="No session folder created.")
        self.assertTrue(
            os.path.isdir(os.path.join(TESTS_BASE_FOLDER, TEST_TAG, "revision_0")), msg="No revision folder created."
        )

        # Check contents.
        for file in [
            os.path.join("Requirement", "SysRS FooXY_42.json"),
            os.path.join("Requirement", "SysRS FooXY_91.json"),
            "SessionValue.json",
            "Tag.json",
        ]:
            self.assertTrue(
                os.path.exists(os.path.join(TESTS_BASE_FOLDER, TEST_TAG, "revision_0", file)),
                msg="Missing file: {}".format(file),
            )

    def test_2_get_requirements(self):
        args = utils.HanforArgumentParser(app).parse_args([TEST_TAG, "-c", TEST_CSV])
        self.startup_hanfor(args, [2, 0, 1, 3, 0])
        result = self.app.get("api/req/gets")
        self.maxDiff = None
        desired_reqs = [
            {
                "formal": [],
                "pattern": "None",
                "status": "Todo",
                "pos": 1,
                "revision_diff": {},
                "vars": [],
                "scope": "None",
                "tags": [],
                "tags_comments": {},
                "desc": "Dont worry, be happy",
                "csv_data": {
                    "formal_header": "Globally, it is never the case, that WORRY holds; Globally, it is always the case, that HAPPY holds.",
                    "id_header": "SysRS FooXY_42",
                    "type_header": "req",
                    "desc_header": "Dont worry, be happy",
                },
                "id": "SysRS FooXY_42",
                "type_inference_errors": {},
                "type": "req",
            },
            {
                "formal": [],
                "status": "Todo",
                "pattern": "None",
                "pos": 0,
                "revision_diff": {},
                "vars": [],
                "scope": "None",
                "tags": [],
                "tags_comments": {},
                "desc": "always look on the bright side of life",
                "csv_data": {
                    "formal_header": "Globally, it is always the case that POINT_OF_VIEW==BRIGHT_SIDE_OF_LIVE",
                    "id_header": "SysRS FooXY_91",
                    "type_header": "req",
                    "desc_header": "always look on the bright side of life",
                },
                "id": "SysRS FooXY_91",
                "type_inference_errors": {},
                "type": "req",
            },
        ]
        self.assertListEqual(desired_reqs, result.json["data"])

        result = self.app.get("api/req/get?id=SysRS FooXY_42")
        desired_req = {
            "id": "SysRS FooXY_42",
            "type_inference_errors": {},
            "csv_data": {
                "type_header": "req",
                "id_header": "SysRS FooXY_42",
                "desc_header": "Dont worry, be happy",
                "formal_header": "Globally, it is never the case, that WORRY holds; Globally, it is always the case, that HAPPY holds.",
            },
            "status": "Todo",
            "available_vars": [],
            "additional_static_available_vars": ["abs()"],
            "desc": "Dont worry, be happy",
            "formal": [],
            "vars": [],
            "tags": [],
            "tags_comments": {},
            "pattern": "None",
            "pos": 1,
            "scope": "None",
            "type": "req",
            "formalizations_html": "",
            "revision_diff": {},
        }
        self.assertDictEqual(desired_req, result.json)

    def tearDown(self):
        # Clean test dir.
        shutil.rmtree(os.path.join(TESTS_BASE_FOLDER, TEST_TAG))
