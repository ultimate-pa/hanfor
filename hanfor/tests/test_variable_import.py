import json
from textwrap import dedent

from app import app, startup_hanfor
import os
import shutil
import utils
from unittest import TestCase
from unittest.mock import patch

HERE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_sessions")
MOCK_DATA_FOLDER = os.path.join(HERE, "test_empty_session")
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


class TestVariableImport(TestCase):
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

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print("Create tmp Data for `{}`.".format(self.__class__.__name__))
        dest = os.path.join(SESSION_BASE_FOLDER, "test_variable_import")
        shutil.copytree(MOCK_DATA_FOLDER, dest)

    def clean_folders(self):
        print("Clean test env of test `{}`.".format(self.__class__.__name__))
        try:
            shutil.rmtree(SESSION_BASE_FOLDER)
        except FileNotFoundError:
            pass

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results
        global count
        count = -1
        mock_results = user_mock_answers

        with app.app_context():
            startup_hanfor(args, HERE, db_test_mode=True)
        app.config["TEMPLATES_FOLDER"] = os.path.join(HERE, "..", "..", "templates")

    def test_import_from_csv(self):
        csv_str = dedent(
            """\
            "name","enum_name","description","type","value","constraint"
            "integer_constant",,"variable description","CONST","0","integer_constant >= 0 && integer_constant <= 0"
            "real_constant",,"variable description","CONST","0.0","real_constant >= 0.0 && real_constant <= 0.0"
            "boolean_variable",,"variable description","bool",,"boolean_variable != false"
            "integer_variable",,"variable description","int",,"integer_variable >= 0 && integer_variable <= 10"
            "real_variable",,"variable description","real",,"real_variable >= 0.0 && real_variable <= 10.0"
            "integer_enum",,"variable description","ENUM_INT",,"integer_enum >= 0 && integer_enum <= 10"
            "integer_enum_enumerator_0","integer_enum","variable description","ENUMERATOR_INT","0",
            "real_enum",,"variable description","ENUM_REAL",,"real_enum >= 0.0 && real_enum <= 10.0"
            "real_enum_enumerator_0","real_enum","variable description","ENUMERATOR_REAL","0.0",
        """
        )

        args = utils.HanforArgumentParser(app).parse_args(["test_variable_import"])
        self.startup_hanfor(args, user_mock_answers=[])
        # Get the available requirements.
        var_gets = self.app.get("api/var/gets")
        self.assertEqual(var_gets.json["data"], [])

        response = self.app.post(
            "api/var/import_csv",
            data={
                "variables_csv_str": csv_str,
            },
        )
        self.assertEqual(True, response.json["success"])

        var_gets = self.app.get("api/var/gets")
        self.assertEqual(
            {
                "integer_constant",
                "real_constant",
                "boolean_variable",
                "integer_variable",
                "real_variable",
                "integer_enum",
                "integer_enum_enumerator_0",
                "real_enum",
                "real_enum_enumerator_0",
            },
            {var[key] for var in var_gets.json["data"] for key in var if key == "name"},
        )
