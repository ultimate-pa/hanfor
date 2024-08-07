"""
Test the hanfor variable manipulation edge cases.

"""

import json

from app import app, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_sessions")
MOCK_DATA_FOLDER = os.path.join(HERE, "test_variable_manipulation_edge_cases")
SESSION_BASE_FOLDER = os.path.join(HERE, "tmp")


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
        global mock_results  # noqa
        global count  # noqa
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(args, HERE, no_data_tracing=True)
        app.config["TEMPLATES_FOLDER"] = os.path.join(HERE, "..", "..", "templates")

    def test_variable_add_constraint_and_change_type_at_the_same_time(self):
        args = utils.HanforArgumentParser(app).parse_args(["test_variable_manipulation_edge_cases"])
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        var_gets = self.app.get("api/var/gets")
        self.assertIn(
            {
                "name": "egg",
                "constraints": [],
                "type_inference_errors": {},
                "script_results": "",
                "used_by": ["SysRS FooXY_91"],
                "const_val": None,
                "tags": [],
                "type": "bool",
                "belongs_to_enum": "",
            },
            var_gets.json["data"],
        )
        add_constraint = self.app.post("api/var/new_constraint", data={"name": "egg"})
        self.assertEqual(True, add_constraint.json["success"])
        self.assertEqual(200, add_constraint.status_code)

        delete_constraint = self.app.post("api/var/del_constraint", data={"name": "egg", "constraint_id": 0})
        self.assertEqual(True, delete_constraint.json["success"])
        self.assertEqual(200, add_constraint.status_code)
        add_constraint = self.app.post("api/var/new_constraint", data={"name": "egg"})
        change_type = self.app.post(
            "api/var/update",
            data={
                "name": "egg",
                "name_old": "egg",
                "type": "ENUM_INT",
                "const_val": "",
                "const_val_old": "",
                "type_old": "bool",
                "occurrences": "SysRS+FooXY_91",
                "constraints": json.dumps(
                    {
                        "0": {
                            "id": "0",
                            "scope": "GLOBALLY",
                            "pattern": "Universality",
                            "expression_mapping": {"P": "", "Q": "", "R": "egg > 10", "S": "", "T": "", "U": ""},
                        }
                    }
                ),
                "updated_constraints": "true",
                "enumerators": json.dumps([]),
            },
        )
        self.assertEqual(True, change_type.json["success"])
        self.assertEqual(200, add_constraint.status_code)
        var_gets = self.app.get("api/var/gets")
        for t in var_gets.json["data"]:
            if t["name"] == "egg":
                self.assertEqual(
                    {
                        "name": "egg",
                        "constraints": ['Globally, it is always the case that "egg > 10" holds'],
                        "used_by": ["Constraint_egg_0", "SysRS FooXY_91"],
                        "tags": [],
                        "type_inference_errors": {},
                        "const_val": None,
                        "type": "ENUM_INT",
                        "script_results": "",
                        "belongs_to_enum": "",
                    },
                    t,
                )
        self.assertIn(
            {
                "name": "egg",
                "constraints": ['Globally, it is always the case that "egg > 10" holds'],
                "used_by": ["Constraint_egg_0", "SysRS FooXY_91"],
                "tags": [],
                "type_inference_errors": {},
                "const_val": None,
                "type": "ENUM_INT",
                "script_results": "",
                "belongs_to_enum": "",
            },
            var_gets.json["data"],
        )

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print("Create tmp Data for `{}`.".format(self.__class__.__name__))
        dest = os.path.join(SESSION_BASE_FOLDER, "test_variable_manipulation_edge_cases")
        shutil.copytree(MOCK_DATA_FOLDER, dest)

    def clean_folders(self):
        print("Clean test env of test `{}`.".format(self.__class__.__name__))
        try:
            shutil.rmtree(SESSION_BASE_FOLDER)
        except FileNotFoundError:
            pass
