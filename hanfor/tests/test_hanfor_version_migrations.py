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

HERE = os.path.dirname(os.path.realpath(__file__))
MOCK_DATA_FOLDER = os.path.join(HERE, "test_sessions", "test_hanfor_migrations")
SESSION_BASE_FOLDER = os.path.join(HERE, "test_sessions", "tmp")

VERSION_TAGS = {
    "0_0_0": "simple_0_0_0",
    "1_0_0": "simple_1_0_0",
}


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
        self.fetch_mock_data()
        self.create_temp_data()
        self.app = app.test_client()
        self.load_expected_result_files()

    @patch("builtins.input", mock_user_input)
    def startup_hanfor(self, args, user_mock_answers):
        global mock_results
        global count
        count = -1
        mock_results = user_mock_answers

        startup_hanfor(args, HERE)
        app.config["TEMPLATES_FOLDER"] = os.path.join(HERE, "..", "templates")

    def test_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Get the available requirements.
            initial_req_gets = self.app.get("api/req/gets")
            self.assertEqual("always look on the bright side of life", initial_req_gets.json["data"][1]["desc"])
            self.assertListEqual(["unseen"], initial_req_gets.json["data"][1]["tags"])

    def test_req_file_after_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test generated req_file consistency.
            req_file_content = self.app.get("/api/tools/req_file").data.decode("utf-8").replace("\r\n", "\n")
            self.assertEqual(self.expected_req_files[version_slug], req_file_content)

    def test_csv_file_after_migrations(self):
        # Starting each version to trigger migrations.
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test generated req_file consistency.
            csv_file_content = self.app.get("/api/tools/csv_file").data.decode("utf-8").replace("\r\n", "\n")
            self.assertEqual(self.expected_csv_files[version_slug], csv_file_content)

    def test_adding_formalizations(self):
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            new_formalization_result = self.app.post("api/req/new_formalization", data={"id": "SysRS FooXY_42"})
            self.assertEqual("200 OK", new_formalization_result.status)
            self.assertEqual("application/json", new_formalization_result.mimetype)
            update = {
                "0": {
                    "id": "0",
                    "scope": "GLOBALLY",
                    "pattern": "Absence",
                    "expression_mapping": {"P": "", "Q": "", "R": "foo!= bar", "S": "", "T": "", "U": ""},
                },
                "1": {
                    "id": "1",
                    "scope": "BEFORE",
                    "pattern": "Existence",
                    "expression_mapping": {"P": "foo", "Q": "", "R": "something_else", "S": "", "T": "", "U": ""},
                },
            }
            add_formalization = self.app.post(
                "api/req/update",
                data={
                    "id": "SysRS FooXY_42",
                    "row_idx": "0",
                    "update_formalization": "true",
                    "tags": json.dumps({}),
                    "status": "Todo",
                    "formalizations": json.dumps(update),
                },
            )
            self.assertEqual("200 OK", add_formalization.status)
            self.assertEqual("application/json", add_formalization.mimetype)
            updated_reqs = self.app.get("api/req/gets")
            self.assertEqual(
                'Before "foo", "something_else" eventually holds', updated_reqs.json["data"][0]["formal"][1]
            )

    def test_adding_tags(self):
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            update = {
                "0": {
                    "id": "0",
                    "scope": "GLOBALLY",
                    "pattern": "Absence",
                    "expression_mapping": {"P": "", "Q": "", "R": "foo!= bar", "S": "", "T": "", "U": ""},
                }
            }
            add_formalization = self.app.post(
                "api/req/update",
                data={
                    "id": "SysRS FooXY_42",
                    "row_idx": "0",
                    "update_formalization": "false",
                    "tags": json.dumps({"yolo": ""}),
                    "status": "Todo",
                    "formalizations": json.dumps(update),
                },
            )
            self.assertEqual("200 OK", add_formalization.status)
            self.assertEqual("application/json", add_formalization.mimetype)
            updated_reqs = self.app.get("api/req/gets")
            self.assertEqual(
                ["yolo"],
                updated_reqs.json["data"][0]["tags"],
            )

    def test_removing_formalization(self):
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            reqs = self.app.get("api/req/gets")
            self.assertEqual(
                'Globally, it is never the case that "foo != bar" holds', reqs.json["data"][0]["formal"][0]
            )
            add_formalization = self.app.post(
                "api/req/del_formalization",
                data={
                    "requirement_id": "SysRS FooXY_42",
                    "formalization_id": 0,
                },
            )
            self.assertEqual("200 OK", add_formalization.status)
            self.assertEqual("application/json", add_formalization.mimetype)
            reqs = self.app.get("api/req/gets")
            self.assertEqual([], reqs.json["data"][0]["formal"])

    def test_generating_a_new_import_session(self):
        for version_slug, version_tag in VERSION_TAGS.items():
            # Cleanup test_env in each iteration to be consistent.
            self.clean_folders()
            self.create_temp_data()
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            # Test correct variable import session infos
            import_session_details = self.app.post(
                "api/var/var_import_info",
                data={"sess_name": "simple_0_0_0_var_import_source", "sess_revision": "revision_0"},
            )
            self.assertEqual({"new_vars": 6, "tot_vars": 11}, import_session_details.json)
            # Start a new import session.
            start_import_session_result = self.app.post(
                "api/var/start_import_session",
                data={"sess_name": "simple_0_0_0_var_import_source", "sess_revision": "revision_0"},
            )
            self.assertEqual({"errormsg": "", "session_id": 0, "success": True}, start_import_session_result.json)
            # Check import session consistency.
            import_session_data = self.app.post(
                "variable_import/api/0/get_table_data",
                data={"sess_name": "simple_0_0_0_var_import_source", "sess_revision": "revision_0"},
            )

            self.assertEqual(11, len(import_session_data.json["data"]))
            # Mark variables to be imported.
            self.app.post(
                "variable_import/api/0/store_table",
                data={"rows": json.dumps({"enum_with_constraint": {"action": "source"}})},
            )
            # Mark variables to be imported.
            self.app.post("variable_import/api/0/apply_import", data={})
            # Check consistency of for imported variables.
            new_var_collection_contents = self.app.get("api/var/gets")
            self.assertIn(
                {
                    "used_by": ["Constraint_enum_with_constraint_0"],
                    "type_inference_errors": {},
                    "constraints": [
                        'Globally, it is never the case that "0 < enum_with_constraint && enum_with_constraint  < 3" holds'
                    ],
                    "const_val": None,
                    "tags": [],
                    "type": "ENUM_INT",
                    "name": "enum_with_constraint",
                    "script_results": "",
                    "belongs_to_enum": "",
                },
                new_var_collection_contents.json["data"],
            )

    def test_change_var_name(self):
        for version_slug, version_tag in VERSION_TAGS.items():
            args = utils.HanforArgumentParser(app).parse_args(
                [VERSION_TAGS[version_slug], "-c", self.csv_files[version_slug]]
            )
            self.startup_hanfor(args, user_mock_answers=[])
            self.app.post(
                "api/var/update",
                data={
                    "name": "foo_bar",
                    "name_old": "foo",
                    "type": "bool",
                    "const_val": "",
                    "const_val_old": "",
                    "type_old": "unknown",
                    "occurrences": "SysRS FooXY_42",
                    "constraints": json.dumps({}),
                    "updated_constraints": False,
                    "enumerators": json.dumps([]),
                },
            )
            updated_affected_req = self.app.get("api/req/get?id=SysRS FooXY_42&row_idx=0")
            self.assertEqual(
                'Globally, it is never the case that "foo_bar!=bar" holds', updated_affected_req.json["formal"][0]
            )

    def tearDown(self):
        # Clean test dir.
        self.clean_folders()

    def create_temp_data(self):
        print("Create tmp Data for `{}`.".format(self.__class__.__name__))
        src = os.path.join(HERE, "test_sessions", "test_hanfor_migrations")
        dst = os.path.join(SESSION_BASE_FOLDER)
        shutil.copytree(src, dst)

    def clean_folders(self):
        print("Clean test env of test `{}`.".format(self.__class__.__name__))
        try:
            shutil.rmtree(SESSION_BASE_FOLDER)
        except FileNotFoundError:
            pass

    def load_expected_result_files(self):
        self.expected_req_files = dict()
        self.expected_csv_files = dict()

        for version_slug, version_tag in VERSION_TAGS.items():
            with open(os.path.join(MOCK_DATA_FOLDER, version_tag, "expected_generated_csv.csv")) as f:
                self.expected_csv_files[version_slug] = f.read()
            with open(os.path.join(MOCK_DATA_FOLDER, version_tag, "expected_generated_req_file.req")) as f:
                self.expected_req_files[version_slug] = f.read()

    def fetch_mock_data(self):
        self.csv_files = dict()

        for version_slug, version_tag in VERSION_TAGS.items():
            self.csv_files[version_slug] = os.path.join(MOCK_DATA_FOLDER, version_tag, "simple.csv")
