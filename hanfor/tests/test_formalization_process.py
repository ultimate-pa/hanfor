import json
import os

from collections import defaultdict

from app import app
from lib_core.data import Requirement, Tag, Variable, VariableCollection
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
        self.mock_hanfor.app.delete("api/v1/req/SysRS%20FooXY_42/formalizations/0")

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
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/guesses")
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

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0")
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
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/999")
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_get_single_formalization_with_subtype(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0?subtype=formalization")
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(result.json["id"], 0)

        # Mismatching subtype returns 404
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0?subtype=variable")
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_list_formalizations_with_subtype_filter(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        # No filter returns all formalizations
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations")
        self.assertEqual(result.status, "200 OK")
        all_count = len(result.json)

        # Filter by formalization returns the same set (only formalizations exist)
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations?subtype=formalization")
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(len(result.json), all_count)

        # Filter by variable returns empty (no variable-type formalizations)
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations?subtype=variable")
        self.assertEqual(result.status, "200 OK")
        self.assertEqual(len(result.json), 0)

    def test_patch_formalization_scope_only(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/0",
            data={"data": json.dumps({"scope": "AFTER"})},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0")
        self.assertEqual(result.json["scope"], "AFTER")
        self.assertEqual(result.json["pattern"], "Absence")
        self.assertEqual(result.json["expr_R"], "foo != bar")

    def test_patch_formalization_pattern_only(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/0",
            data={"data": json.dumps({"pattern": "Response"})},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0")
        self.assertEqual(result.json["pattern"], "Response")
        self.assertEqual(result.json["scope"], "GLOBALLY")

    def test_patch_formalization_expression(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/0",
            data={"data": json.dumps({"expression_mapping": {"R": "spam == ham"}})},
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0")
        self.assertEqual(result.json["expr_R"], "spam == ham")
        self.assertEqual(result.json["scope"], "GLOBALLY")
        self.assertEqual(result.json["pattern"], "Absence")

    def test_patch_formalization_404(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/999",
            data={"data": json.dumps({"scope": "AFTER"})},
        )
        self.assertEqual(result.status, "404 NOT FOUND")

        result = self.mock_hanfor.app.patch(
            "api/v1/req/SysRS%20FooXY_42/formalizations/variable/999",
            data={"data": json.dumps({"name": "newname"})},
        )
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_put_formalization_full_replace(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.put(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/0",
            data={
                "data": json.dumps(
                    {
                        "scope": "AFTER",
                        "pattern": "Response",
                        "expression_mapping": {"R": "spam == ham", "S": "true"},
                    }
                )
            },
        )
        self.assertEqual(result.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0")
        self.assertEqual(result.json["scope"], "AFTER")
        self.assertEqual(result.json["pattern"], "Response")
        self.assertEqual(result.json["expr_R"], "spam == ham")
        self.assertIn("expr_S", result.json)

    def test_put_formalization_404(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.put(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/999",
            data={
                "data": json.dumps(
                    {
                        "scope": "AFTER",
                        "pattern": "Response",
                        "expression_mapping": {"R": "true"},
                    }
                )
            },
        )
        self.assertEqual(result.status, "404 NOT FOUND")

    def test_put_formalization_missing_field(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        result = self.mock_hanfor.app.put(
            "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/0",
            data={"data": json.dumps({"scope": "AFTER"})},
        )
        self.assertEqual(result.status, "400 BAD REQUEST")

    def test_put_formalization_idempotent(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

        body = {
            "data": json.dumps(
                {
                    "scope": "AFTER",
                    "pattern": "Response",
                    "expression_mapping": {"R": "foo != bar"},
                }
            )
        }
        store_url = "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/0"

        r1 = self.mock_hanfor.app.put(store_url, data=body)
        r2 = self.mock_hanfor.app.put(store_url, data=body)
        self.assertEqual(r1.status, "200 OK")
        self.assertEqual(r2.status, "200 OK")

        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/0")
        self.assertEqual(result.json["scope"], "AFTER")

    def test_update_csv_hashcollision(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        success = self.mock_hanfor.startup_hanfor("simple_hashcollision.csv", "simple", [1])
        self.assertTrue(success, "Startup procedure was not successful")


class TestMixedFormalizationCollection(TestCase):
    """A requirement holding both element subtypes at once.

    No fixture session has a `Variable` inside `Requirement.formalizations`, so every consumer that walks
    that dict was only ever exercised with `Formalization` objects.
    """

    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.mock_hanfor.app.post(
            "api/v1/req/SysRS%20FooXY_42/formalizations/variable/9",
            data={"data": json.dumps({"name": "mixedvar", "type": "bool", "temp_id": 9})},
        )

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def test_requirement_serialises_with_both_subtypes(self):
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42")

        self.assertEqual(200, result.status_code)
        self.assertListEqual(["bar", "foo"], result.json["vars"])

    def test_list_endpoint_returns_both_subtypes(self):
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations")

        self.assertEqual(200, result.status_code)
        self.assertListEqual(["formalization", "variable"], sorted(e["formalization_type"] for e in result.json))
        # Every element answers `is_constraint`, not just the ones that can carry a scoped pattern.
        self.assertListEqual([False, False], [e["is_constraint"] for e in result.json])

    def test_single_endpoint_returns_the_variable(self):
        result = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations/9")

        self.assertEqual(200, result.status_code)
        self.assertEqual("variable", result.json["formalization_type"])
        self.assertEqual("mixedvar", result.json["name"])
        self.assertListEqual([], result.json["constraint_refs"])

    def test_subtype_filter_still_separates_them(self):
        variables = self.mock_hanfor.app.get("api/v1/req/SysRS%20FooXY_42/formalizations?subtype=variable")

        self.assertListEqual(["variable"], [e["formalization_type"] for e in variables.json])


class TestCreateFormalizationValidation(TestCase):
    """A create with an incomplete payload must be rejected before anything is mutated.

    `store.js` posts `{}` whenever `getFormalizationFromDOM` misses its card, which used to reach
    `data["scope"]` and be reported as a missing draft - after the draft had already been attached.
    """

    RID = "SysRS FooXY_42"
    URL = "api/v1/req/SysRS%20FooXY_42/formalizations/formalization/7"

    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def formalization_ids(self) -> list[int]:
        with app.app_context():
            return sorted(app.db.get_object(Requirement, self.RID).formalizations.keys())

    def test_empty_payload_is_rejected(self):
        result = self.mock_hanfor.app.post(self.URL, data={"data": json.dumps({})})

        self.assertEqual(400, result.status_code)
        self.assertFalse(result.json["success"])
        self.assertIn("scope", result.json["errormsg"])

    def test_rejected_create_leaves_no_stray_formalization(self):
        before = self.formalization_ids()

        self.mock_hanfor.app.post(self.URL, data={"data": json.dumps({})})

        self.assertListEqual(before, self.formalization_ids())

    def test_partial_payload_names_every_missing_field(self):
        result = self.mock_hanfor.app.post(self.URL, data={"data": json.dumps({"scope": "GLOBALLY"})})

        self.assertEqual(400, result.status_code)
        self.assertIn("pattern", result.json["errormsg"])
        self.assertIn("expression_mapping", result.json["errormsg"])
        self.assertNotIn("scope", result.json["errormsg"])

    def test_complete_payload_still_creates(self):
        result = self.mock_hanfor.app.post(
            self.URL,
            data={
                "data": json.dumps(
                    {"scope": "GLOBALLY", "pattern": "Absence", "expression_mapping": {"R": "foo != bar"}}
                )
            },
        )

        self.assertEqual(200, result.status_code)
        self.assertTrue(result.json["success"])
        self.assertIn(7, self.formalization_ids())


class TestSubtypeErrorStatuses(TestCase):
    """`post` used to answer 200 with `success: false` for every failure; all three verbs now agree."""

    RID = "SysRS FooXY_42"
    BASE = "api/v1/req/SysRS%20FooXY_42/formalizations"

    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def post(self, url: str, payload: dict):
        return self.mock_hanfor.app.post(url, data={"data": json.dumps(payload)})

    def formalization_ids(self) -> list[int]:
        with app.app_context():
            return sorted(app.db.get_object(Requirement, self.RID).formalizations.keys())

    def test_unparsable_formalization_is_bad_request(self):
        result = self.post(
            f"{self.BASE}/formalization/7",
            {"scope": "NOT_A_SCOPE", "pattern": "Absence", "expression_mapping": {"R": "foo"}},
        )

        self.assertEqual(400, result.status_code)
        self.assertIn("Could not parse draft", result.json["errormsg"])

    def test_unparsable_formalization_rolls_back_the_draft(self):
        before = self.formalization_ids()

        self.post(
            f"{self.BASE}/formalization/7",
            {"scope": "NOT_A_SCOPE", "pattern": "Absence", "expression_mapping": {"R": "foo"}},
        )

        self.assertListEqual(before, self.formalization_ids())

    def test_illegal_variable_name_is_bad_request(self):
        result = self.post(f"{self.BASE}/variable/7", {"name": "9illegal", "type": "bool", "temp_id": 7})

        self.assertEqual(400, result.status_code)
        self.assertIn("9illegal", result.json["errormsg"])

    def test_successful_create_is_unaffected(self):
        result = self.post(
            f"{self.BASE}/formalization/8",
            {"scope": "GLOBALLY", "pattern": "Absence", "expression_mapping": {"R": "foo != bar"}},
        )

        self.assertEqual(200, result.status_code)
        self.assertTrue(result.json["success"])


RID = "SysRS FooXY_42"


class TestVariableRename(TestCase):
    """Renaming a variable from the requirement modal, the path through `_update_formalizations`."""

    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def variable_names(self) -> list[str]:
        with app.app_context():
            return sorted(v.name for v in app.db.get_objects(Variable).values())

    def variable_names_on_disk(self) -> list[str]:
        """What was actually written, which is the only thing that survives the request.

        A failed save still leaves the in-memory objects mutated, so `variable_names` alone cannot tell a
        persisted rename from one that a 500 threw away.
        """
        folder = os.path.join(app.config["SESSION_BASE_FOLDER"], "simple", "revision_0", "Variable")
        return sorted(json.load(open(os.path.join(folder, f)))["name"] for f in os.listdir(folder))

    def create(self, fid: str, data: dict) -> None:
        subtype = "variable" if "temp_id" in data else "formalization"
        self.mock_hanfor.app.post(
            f"api/v1/req/{RID}/formalizations/{subtype}/{fid}", data={"id": RID, "data": json.dumps(data)}
        )

    def save(self, formalizations: dict):
        return self.mock_hanfor.app.patch(
            f"api/v1/req/{RID}",
            data={
                "row_idx": "0",
                "update_formalization": "true",
                "formalizations_order": "{}",
                "tags": "{}",
                "status": "Todo",
                "formalizations": json.dumps(formalizations),
            },
        )

    def test_renaming_a_used_variable_rewrites_the_expression(self):
        """The rename used to leave the expression on the old name, which then 500ed the whole save."""
        self.create("9", {"name": "myvar", "type": "bool", "temp_id": 9})
        self.create("7", {"scope": "GLOBALLY", "pattern": "Absence", "expression_mapping": {"R": "myvar"}})

        result = self.save(
            {
                "9": {
                    "id": "9",
                    "formalization_type": "variable",
                    "name": "renamed",
                    "var_type": "bool",
                    "const_val": "",
                    "enumerators": [],
                },
            }
        )

        self.assertEqual(200, result.status_code)
        formal = self.mock_hanfor.app.get(f"api/v1/req/{RID}").json["formal"]
        self.assertIn('Globally, it is never the case that "renamed" holds', formal)
        self.assertNotIn("myvar", self.variable_names())

    def test_renaming_a_used_variable_persists(self):
        """The 500 skipped `db.update()`, so the old variable survived with everything intact."""
        self.create("9", {"name": "myvar", "type": "bool", "temp_id": 9})
        self.create("7", {"scope": "GLOBALLY", "pattern": "Absence", "expression_mapping": {"R": "myvar"}})

        self.save(
            {
                "9": {
                    "id": "9",
                    "formalization_type": "variable",
                    "name": "renamed",
                    "var_type": "bool",
                    "const_val": "",
                    "enumerators": [],
                },
            }
        )

        self.assertIn("renamed", self.variable_names_on_disk())
        self.assertNotIn("myvar", self.variable_names_on_disk())

    def test_renaming_an_enum_rewrites_expressions_naming_its_enumerators(self):
        enumerators = [["A", "1"], ["B", "2"]]
        self.create("9", {"name": "myenum", "type": "ENUM_INT", "temp_id": 9, "enumerators": enumerators})
        self.create("7", {"scope": "GLOBALLY", "pattern": "Absence", "expression_mapping": {"R": "myenum_A"}})

        self.save(
            {
                "9": {
                    "id": "9",
                    "formalization_type": "variable",
                    "name": "renamed",
                    "var_type": "ENUM_INT",
                    "const_val": "",
                    "enumerators": enumerators,
                },
            }
        )

        formal = self.mock_hanfor.app.get(f"api/v1/req/{RID}").json["formal"]
        self.assertIn('Globally, it is never the case that "renamed_A" holds', formal)
        self.assertNotIn("myenum_A", self.variable_names())


class TestUndefinedVariableInExpression(TestCase):
    """An expression can outlive the variable it names. That is an error to show, not one to crash on."""

    def test_run_type_checks_reports_the_name_instead_of_raising(self):
        req = Requirement("req1", "a requirement", "requirement", {}, 0)
        fid, _ = req.add_empty_formalization()
        collection = VariableCollection([], [req])
        tags = defaultdict(lambda: Tag("test", "color", False, ""))
        req.update_formalization(fid, "GLOBALLY", "Absence", {"R": "ghost"}, collection, tags)

        # Parsing the expression created `ghost`; drop it, the way a rename that missed this expression did.
        collection.collection.pop("ghost")

        req.run_type_checks(collection, tags)

        self.assertEqual(["r"], req.formalizations[fid].type_inference_error_keys())
        self.assertIn("`ghost` is not defined", str(req.formalizations[fid].type_inference_errors))
