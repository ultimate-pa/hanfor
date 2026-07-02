import json

from tests.mock_hanfor import MockHanfor
from unittest import TestCase


class TestFormalizationProcess(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def test_adding_new_formalization(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertListEqual(result.json["vars"], ["bar", "foo"])

        # Add content to the existing Formalization
        update = {
            "0": {
                "id": "0",
                "formalization_type": "formalization",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "foo != bar", "S": "", "T": "", "U": ""},
            },
        }

        # And these are all the new created drafts
        drafts = {
            "1": {
                "id": "1",
                "scope": "BEFORE",
                "pattern": "Existence",
                "expression_mapping": {"P": "the_world_sinks", "Q": "", "R": "spam == ham", "S": "", "T": "", "U": ""},
            },
        }

        # So we submit then the current frontend state to the backend
        for draft in drafts.values():
            self.mock_hanfor.app.post(
                "api/v1/req/add_formalization_from_guess",
                data={
                    "requirement_id": "SysRS FooXY_42",
                    "scope": draft["scope"],
                    "pattern": draft["pattern"],
                    "mapping": json.dumps(draft["expression_mapping"]),
                },
            )
        self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42",
            data={
                "row_idx": "0",
                "update_formalization": "true",
                "formalizations_order": "{}",
                "tags": json.dumps({"tag1": "comment 1 with some character", "tag2": "äüö%&/+= coment330+-# chars"}),
                "status": "Todo",
                "formalizations": json.dumps(update),
            },
        )
        # Check if content is correct.
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(
            result.json["formal"],
            [
                'Globally, it is never the case that "foo != bar" holds',
                'Before "the_world_sinks", "spam == ham" eventually holds',
            ],
        )
        self.assertListEqual(result.json["vars"], ["bar", "foo", "ham", "spam", "the_world_sinks"])
        self.assertCountEqual(result.json["tags"], ["tag1", "tag2", "unknown_type", "has_formalization"])
        self.assertLessEqual(
            {"tag1": "comment 1 with some character", "tag2": "äüö%&/+= coment330+-# chars"}.items(),
            result.json["tags_comments"].items(),
        )

    def test_changing_var_in_formalization(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertCountEqual(result.json["vars"], ["bar", "foo"])

        # Check current available variables.
        self.assertCountEqual(result.json["available_vars"], ["spam_ham", "bar", "foo", "spam_egg", "spam"])

        # Change a var in the formalization to a new not available.

        # Add content to the Formalization
        update = {
            "0": {
                "id": "0",
                "formalization_type": "formalization",
                "scope": "GLOBALLY",
                "pattern": "Absence",
                "expression_mapping": {"P": "", "Q": "", "R": "foo != bas", "S": "", "T": "", "U": ""},
            }
        }
        self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42",
            data={
                "row_idx": "0",
                "update_formalization": "true",
                "tags": json.dumps({}),
                "formalizations_order": "{}",
                "status": "Todo",
                "formalizations": json.dumps(update),
            },
        )
        # Check if content is correct.
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "foo != bas" holds'])
        self.assertCountEqual(result.json["vars"], ["foo", "bas"])

        # Check current available variables.
        self.assertCountEqual(result.json["available_vars"], ["spam_ham", "bar", "foo", "spam_egg", "spam", "bas"])

    def test_changing_var_name(self):  # TODO update names of variables is not allowed anymore
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertListEqual(result.json["vars"], ["bar", "foo"])

        # Change the name of foo to bas
        update = {
            "name": "bas",
            "name_old": "foo",
            "type": "unknown",
            "const_val": "",
            "const_val_old": "",
            "type_old": "unknown",
            "occurrences": "SysRS FooXY_42",
            "constraints": "{}",
            "updated_constraints": "true",
            "enumerators": "[]",
            "belongs_to_enum": "",
            "belongs_to_enum_old": "",
        }
        self.mock_hanfor.app.post("api/var/update", data=update)

        # Check changed formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "bas!=bar" holds'])
        self.assertCountEqual(result.json["vars"], ["bar", "bas"])

    def test_deleting_a_formalization(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertCountEqual(result.json["vars"], ["bar", "foo"])

        # Deleting the formalization
        self.mock_hanfor.app.delete("api/v1/req/formalizations/SysRS%20FooXY_42/0")

        # Check current formalization for `SysRS FooXY_42` now empty
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], [])
        self.assertListEqual(result.json["vars"], [])

    def test_setting_status(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # Check current formalization for `SysRS FooXY_42`
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertListEqual(result.json["formal"], ['Globally, it is never the case that "foo != bar" holds'])
        self.assertCountEqual(result.json["vars"], ["bar", "foo"])

        # Check current available variables.
        self.assertCountEqual(result.json["available_vars"], ["spam_ham", "bar", "foo", "spam_egg", "spam"])

        self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42",
            data={
                "row_idx": "0",
                "update_formalization": "true",
                "formalizations_order": "{}",
                "tags": json.dumps({}),
                "status": "Done",
                "formalizations": json.dumps({}),
            },
        )
        # Check if content is correct.
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertEqual(result.json["status"], "Done")

    def test_add_and_remove_tag(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # POST a tag
        result = self.mock_hanfor.app.post("api/v1/req/SysRS%20FooXY_42/tags/some-mass-added-tag")
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertIn("some-mass-added-tag", result.json["tags"])

        # DELETE a tag
        result = self.mock_hanfor.app.delete("api/v1/req/SysRS%20FooXY_42/tags/some-mass-added-tag")
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertNotIn("some-mass-added-tag", result.json["tags"])

        # Adding a tag that doesn't exist yet creates it
        result = self.mock_hanfor.app.post("api/v1/req/SysRS%20FooXY_42/tags/brand-new-tag")
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertIn("brand-new-tag", result.json["tags"])

        # Removing a non-existent tag is a no-op (200)
        result = self.mock_hanfor.app.delete("api/v1/req/SysRS%20FooXY_42/tags/nonexistent")
        self.assertEqual(result.status, "200 OK")

        # 404 for non-existent requirement
        result = self.mock_hanfor.app.post("api/v1/req/NONEXISTENT/tags/foo")
        self.assertEqual(result.status, "404 NOT FOUND")

        result = self.mock_hanfor.app.delete("api/v1/req/NONEXISTENT/tags/foo")
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_get_available_guesses(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        result = self.mock_hanfor.app.get(
            "api/v1/req/SysRS%20FooXY_42/guesses"
        )
        self.assertEqual(result.status, "200 OK")
        self.assertIn("available_guesses", result.json)
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertEqual(result.status, "200 OK")

    def test_add_formalization_from_guess(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.post(
            "api/v1/req/add_formalization_from_guess",
            data={
                "requirement_id": "SysRS FooXY_42",
                "formalizations_order": "{}",
                "scope": "GLOBALLY",
                "pattern": "Response",
                "mapping": '{"R": "", "S": ""}',
            },
        )
        self.assertEqual(result.status, "200 OK")
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")
        self.assertEqual(result.status, "200 OK")

    def test_get_single_formalization(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0"
        )
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(result.json["id"], 0)
        self.assertEqual(result.json["formalization_type"], "formalization")
        self.assertEqual(
            result.json["text"],
            'Globally, it is never the case that "foo != bar" holds',
        )
        self.assertIn("scope", result.json)
        self.assertIn("pattern", result.json)

        # 404 for non-existent fid
        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/999"
        )
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_get_single_formalization_with_subtype(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0?subtype=formalization"
        )
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(result.json["id"], 0)

        # Mismatching subtype returns 404
        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0?subtype=variable"
        )
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_list_formalizations_with_subtype_filter(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # No filter returns all formalizations
        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42"
        )
        self.assertEqual(result.status, "200 OK")
        all_count = len(result.json)

        # Filter by formalization returns the same set (only formalizations exist)
        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42?subtype=formalization"
        )
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(len(result.json), all_count)

        # Filter by variable returns empty (no variable-type formalizations)
        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42?subtype=variable"
        )
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(len(result.json), 0)

    def test_patch_formalization_scope_only(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/0",
            data={"data": json.dumps({"scope": "AFTER"})},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0"
        )
        self.assertEqual(result.json["scope"], "AFTER")
        self.assertEqual(result.json["pattern"], "Absence")
        self.assertEqual(result.json["expr_R"], "foo != bar")

    def test_patch_formalization_pattern_only(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/0",
            data={"data": json.dumps({"pattern": "Response"})},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0"
        )
        self.assertEqual(result.json["pattern"], "Response")
        self.assertEqual(result.json["scope"], "GLOBALLY")

    def test_patch_formalization_expression(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/0",
            data={"data": json.dumps({"expression_mapping": {"R": "spam == ham"}})},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0"
        )
        self.assertEqual(result.json["expr_R"], "spam == ham")
        self.assertEqual(result.json["scope"], "GLOBALLY")
        self.assertEqual(result.json["pattern"], "Absence")

    def test_patch_formalization_404(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/999",
            data={"data": json.dumps({"scope": "AFTER"})},
        )
        self.assertEqual(result.status, "404 NOT FOUND")

        result = self.mock_hanfor.app.patch(
            "api/v1/req/formalizations/SysRS%20FooXY_42/variable/999",
            data={"data": json.dumps({"name": "newname"})},
        )
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_put_formalization_full_replace(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.put(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/0",
            data={"data": json.dumps({
                "scope": "AFTER",
                "pattern": "Response",
                "expression_mapping": {"R": "spam == ham", "S": "true"},
            })},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0"
        )
        self.assertEqual(result.json["scope"], "AFTER")
        self.assertEqual(result.json["pattern"], "Response")
        self.assertEqual(result.json["expr_R"], "spam == ham")
        self.assertIn("expr_S", result.json)

    def test_put_formalization_404(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.put(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/999",
            data={"data": json.dumps({
                "scope": "AFTER", "pattern": "Response",
                "expression_mapping": {"R": "true"},
            })},
        )
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_put_formalization_missing_field(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.put(
            "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/0",
            data={"data": json.dumps({"scope": "AFTER"})},
        )
        self.assertEqual(result.status, "400 BAD REQUEST")

    def test_put_formalization_idempotent(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        body = {"data": json.dumps({
            "scope": "AFTER", "pattern": "Response",
            "expression_mapping": {"R": "foo != bar"},
        })}
        store_url = "api/v1/req/formalizations/SysRS%20FooXY_42/formalization/0"

        r1 = self.mock_hanfor.app.put(store_url, data=body)
        r2 = self.mock_hanfor.app.put(store_url, data=body)
        self.assertEqual(r1.status, "200 OK")
        self.assertEqual(r2.status, "200 OK")

        result = self.mock_hanfor.app.get(
            "api/v1/req/formalizations/SysRS%20FooXY_42/0"
        )
        self.assertEqual(result.json["scope"], "AFTER")

    def test_update_csv_hashcollision(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        success = self.mock_hanfor.startup_hanfor("simple_hashcollision.csv", "simple", [1])
        self.assertTrue(success, "Startup procedure was not successful")
