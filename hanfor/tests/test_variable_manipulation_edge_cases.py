"""
Test the hanfor variable manipulation edge cases.

"""

import json

from app import app, startup_hanfor
from lib_core.utils import setup_logging
import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from lib_core.startup import HanforArgumentParser
from tests.mock_hanfor import variable_url, variables_without_ids

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
        setup_logging(app)
        self.clean_folders()
        self.create_temp_data()
        self.app = app.test_client()

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results  # noqa
        global count  # noqa
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(app, args, HERE, no_data_tracing=True)
        app.config["TEMPLATES_FOLDER"] = os.path.join(HERE, "..", "..", "templates")

    def test_variable_add_constraint_and_change_type_at_the_same_time(self):
        args = HanforArgumentParser(app).parse_args(["test_variable_manipulation_edge_cases"])
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        self.assertIn(
            {
                "name": "egg",
                "constraints": [],
                "type_inference_errors": {},
                "script_results": "",
                "used_by": ["SysRS FooXY_91"],
                "constraint_refs": ["SysRS FooXY_91:0"],
                "const_val": None,
                "tags": [],
                "type": "bool",
                "order": 0,
                "belongs_to_enum": "",
            },
            variables_without_ids(self.app),
        )
        add_constraint = self.app.post(variable_url(self.app, "egg", "/constraints"), json=[{"temp_id": "a"}])
        self.assertEqual({"a": 0}, add_constraint.json["ids"])
        self.assertEqual(201, add_constraint.status_code)
        self.assertEqual([0], [c["id"] for c in self.app.get(variable_url(self.app, "egg", "/constraints")).json])

        delete_constraint = self.app.delete(variable_url(self.app, "egg", "/constraints/0"))
        self.assertEqual(True, delete_constraint.json["success"])
        self.assertEqual(200, delete_constraint.status_code)
        self.assertEqual(404, self.app.delete(variable_url(self.app, "egg", "/constraints/0")).status_code)
        add_constraint = self.app.post(variable_url(self.app, "egg", "/constraints"), json=[{"temp_id": "a"}])
        patch_constraint = self.app.patch(
            variable_url(self.app, "egg", "/constraints/0"),
            json={"scope": "GLOBALLY", "pattern": "Universality", "expression_mapping": {"R": "egg > 10"}},
        )
        self.assertEqual(200, patch_constraint.status_code)
        change_type = self.app.patch(
            variable_url(self.app, "egg"),
            json={"name": "egg", "type": "ENUM_INT", "const_val": "", "enumerators": []},
        )
        self.assertEqual(True, change_type.json["success"])
        self.assertEqual(200, change_type.status_code)
        for t in variables_without_ids(self.app):
            if t["name"] == "egg":
                self.assertEqual(
                    {
                        "name": "egg",
                        "constraints": ['Globally, it is always the case that "egg > 10" holds'],
                        "used_by": ["SysRS FooXY_91"],
                        "constraint_refs": ["SysRS FooXY_91:0", "Constraint_egg_0"],
                        "tags": [],
                        "type_inference_errors": {},
                        "const_val": None,
                        "type": "ENUM_INT",
                        "order": 0,
                        "script_results": "",
                        "belongs_to_enum": "",
                    },
                    t,
                )
        self.assertIn(
            {
                "name": "egg",
                "constraints": ['Globally, it is always the case that "egg > 10" holds'],
                "used_by": ["SysRS FooXY_91"],
                "constraint_refs": ["SysRS FooXY_91:0", "Constraint_egg_0"],
                "tags": [],
                "type_inference_errors": {},
                "const_val": None,
                "type": "ENUM_INT",
                "order": 0,
                "script_results": "",
                "belongs_to_enum": "",
            },
            variables_without_ids(self.app),
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
