"""
Test the hanfor version migrations.

"""

import json

from app import app, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_sessions")
MOCK_DATA_FOLDER = os.path.join(HERE, "test_delete_variable")
SESSION_BASE_FOLDER = os.path.join(HERE, "tmp")


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


class TestHanforVersionMigrations(TestCase):
    def setUp(self):
        # Clean test folder.
        app.config["SESSION_BASE_FOLDER"] = SESSION_BASE_FOLDER
        app.config["LOG_TO_FILE"] = False
        app.config["LOG_LEVEL"] = "DEBUG"
        utils.register_assets(app)
        utils.setup_logging(app)
        self.clean_folders()
        self.create_temp_data()
        self.app = app.test_client()

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results
        global count
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(args, HERE)
        app.config["TEMPLATES_FOLDER"] = os.path.join(HERE, "..", "..", "templates")

    def test_variable_with_constraint_deletion(self):
        args = utils.HanforArgumentParser(app).parse_args(["test_delete_variable"])
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        var_gets = self.app.get("api/var/gets")
        self.assertIn(
            {
                "name": "ham",
                "constraints": ['Globally, it is never the case that "ham != foo" holds'],
                "type_inference_errors": {},
                "script_results": "",
                "used_by": ["Constraint_ham_0"],
                "const_val": None,
                "tags": [],
                "type": "bool",
                "belongs_to_enum": "",
            },
            var_gets.json["data"],
        )
        self.assertEqual(
            {"spam", "spam_ham", "foo", "egg", "spam_egg", "spam", "bar", "ham"},
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )
        del_ham_result = self.app.post(
            "api/var/multi_update", data={"change_type": "", "selected_vars": json.dumps(["ham"]), "del": "true"}
        )
        self.assertEqual(True, del_ham_result.json["success"])
        var_gets = self.app.get("api/var/gets")
        self.assertEqual(
            {"spam", "spam_ham", "foo", "egg", "spam_egg", "spam", "bar"},
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )

    def test_deleting_simple_variable(self):
        args = utils.HanforArgumentParser(app).parse_args(["test_delete_variable"])
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        var_gets = self.app.get("api/var/gets")
        self.assertEqual(
            {"spam", "spam_ham", "foo", "egg", "spam_egg", "spam", "bar", "ham"},
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )
        del_ham_result = self.app.post(
            "api/var/multi_update", data={"change_type": "", "selected_vars": json.dumps(["spam_egg"]), "del": "true"}
        )
        self.assertEqual(True, del_ham_result.json["success"])
        var_gets = self.app.get("api/var/gets")
        self.assertEqual(
            {"spam", "spam_ham", "foo", "egg", "spam", "bar", "ham"},
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )

    def test_no_affect_of_deleting_used_variable(self):
        args = utils.HanforArgumentParser(app).parse_args(["test_delete_variable"])
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        var_gets = self.app.get("api/var/gets")
        self.assertEqual(
            {"spam", "spam_ham", "foo", "egg", "spam_egg", "spam", "bar", "ham"},
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )
        del_ham_result = self.app.post(
            "api/var/multi_update", data={"change_type": "", "selected_vars": json.dumps(["foo"]), "del": "true"}
        )
        self.assertEqual(True, del_ham_result.json["success"])
        var_gets = self.app.get("api/var/gets")
        self.assertEqual(
            {"spam", "spam_ham", "foo", "egg", "spam_egg", "spam", "bar", "ham"},
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print("Create tmp Data for `{}`.".format(self.__class__.__name__))
        dest = os.path.join(SESSION_BASE_FOLDER, "test_delete_variable")
        shutil.copytree(MOCK_DATA_FOLDER, dest)

    def clean_folders(self):
        print("Clean test env of test `{}`.".format(self.__class__.__name__))
        try:
            shutil.rmtree(SESSION_BASE_FOLDER)
        except FileNotFoundError:
            pass
