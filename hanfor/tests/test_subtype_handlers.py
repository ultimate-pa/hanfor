from unittest import TestCase

from app import app
from hanfor_flask import current_app
from lib_core.data import Variable
from requirements.subtypes import (
    SUBTYPES,
    InvalidPayload,
    SubtypeContext,
    SubtypeNotFound,
)
from tests.mock_hanfor import MockHanfor

RID = "SysRS FooXY_42"
FORMALIZATION = {"scope": "GLOBALLY", "pattern": "Absence", "expression_mapping": {"R": "foo != bar"}}


class TestSubtypeHandlers(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.app_context = app.app_context()
        self.app_context.push()
        self.ctx = SubtypeContext.load(RID)

    def tearDown(self) -> None:
        self.app_context.pop()
        self.mock_hanfor.tear_down()

    @property
    def formalizations(self):
        return SUBTYPES["formalization"].handler

    @property
    def variables(self):
        return SUBTYPES["variable"].handler

    # registry
    def test_registry_pairs_each_name_with_its_model(self):
        self.assertEqual("Formalization", SUBTYPES["formalization"].model.__name__)
        self.assertEqual("Variable", SUBTYPES["variable"].model.__name__)

    # fetch
    def test_fetch_returns_the_element_of_its_own_subtype(self):
        element = self.formalizations.fetch(self.ctx, "0")

        self.assertEqual("formalization", element.of_type())

    def test_fetch_rejects_an_element_of_another_subtype(self):
        self.variables.create(self.ctx, "9", {"name": "handlervar", "type": "bool", "temp_id": 9})

        with self.assertRaises(SubtypeNotFound):
            self.formalizations.fetch(self.ctx, "9")

    def test_fetch_rejects_a_missing_id(self):
        with self.assertRaises(SubtypeNotFound) as caught:
            self.variables.fetch(self.ctx, "404")

        self.assertEqual("Variable not found.", str(caught.exception))

    # create
    def test_create_attaches_a_formalization_under_the_given_fid(self):
        self.formalizations.create(self.ctx, "7", FORMALIZATION)

        self.assertIn(7, self.ctx.requirement.formalizations)

    def test_create_keys_a_variable_by_its_own_id_not_the_fid(self):
        """`fid` is only what the client proposed in the URL; a variable brings its own id."""
        self.variables.create(self.ctx, "999", {"name": "ownid", "type": "bool", "temp_id": 4})

        self.assertIn(4, self.ctx.requirement.formalizations)
        self.assertNotIn(999, self.ctx.requirement.formalizations)

    def test_create_rejects_an_incomplete_payload_without_mutating(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload):
            self.formalizations.create(self.ctx, "7", {})

        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    def test_create_rolls_back_a_draft_it_could_not_fill(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload):
            self.formalizations.create(self.ctx, "7", {**FORMALIZATION, "scope": "NOT_A_SCOPE"})

        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    # patch
    def test_patch_leaves_the_fields_it_was_not_given(self):
        self.formalizations.patch(self.ctx, "0", {"scope": "AFTER"})

        formalization = self.ctx.requirement.formalizations[0]
        self.assertEqual("AFTER", formalization.scoped_pattern.scope.name)
        self.assertEqual("Absence", formalization.scoped_pattern.pattern.get_name())

    def test_patch_rejects_an_illegal_variable_name(self):
        self.variables.create(self.ctx, "9", {"name": "goodname", "type": "bool", "temp_id": 9})

        with self.assertRaises(InvalidPayload):
            self.variables.patch(self.ctx, "9", {"name": "9illegal"})

    # replace
    def test_replace_requires_every_field(self):
        with self.assertRaises(InvalidPayload) as caught:
            self.formalizations.replace(self.ctx, "0", {"scope": "GLOBALLY"})

        self.assertIn("required", str(caught.exception))

    def test_replace_overwrites_what_patch_would_have_kept(self):
        self.formalizations.replace(self.ctx, "0", {**FORMALIZATION, "pattern": "Universality"})

        self.assertEqual("Universality", self.ctx.requirement.formalizations[0].scoped_pattern.pattern.get_name())

    # a null field is as missing as an absent one
    def test_create_rejects_a_null_scope(self):
        with self.assertRaises(InvalidPayload) as caught:
            self.formalizations.create(self.ctx, "7", {**FORMALIZATION, "scope": None})

        self.assertEqual("Missing required field(s): scope", str(caught.exception))

    def test_create_rejects_a_null_pattern_without_mutating(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload):
            self.formalizations.create(self.ctx, "7", {**FORMALIZATION, "pattern": None})

        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    def test_create_registers_an_enum_variable_exactly_once(self):
        """`create_enum_variable` used to find the name free and build a second object under it, leaving both there"""
        self.variables.create(
            self.ctx,
            "9",
            {"name": "myenum", "type": "ENUM_INT", "temp_id": 9, "enumerators": [["A", "1"], ["B", "2"]]},
        )

        names = [v.name for v in current_app.db.get_objects(Variable).values()]
        self.assertEqual(1, names.count("myenum"))

    def test_create_attaches_the_object_the_collection_holds(self):
        self.variables.create(self.ctx, "9", {"name": "fresh", "type": "bool", "temp_id": 9})

        self.assertIs(self.ctx.variable_collection.collection["fresh"], self.ctx.requirement.formalizations[9])

    def test_create_rejects_a_taken_name_without_attaching(self):
        with self.assertRaises(InvalidPayload) as caught:
            self.variables.create(self.ctx, "9", {"name": "foo", "type": "bool", "temp_id": 9})

        self.assertEqual("A variable named `foo` already exists.", str(caught.exception))
        self.assertNotIn(9, self.ctx.requirement.formalizations)

    def test_patch_rejects_a_rename_onto_a_taken_name(self):
        self.variables.create(self.ctx, "9", {"name": "fresh", "type": "bool", "temp_id": 9})
        with self.assertRaises(InvalidPayload):
            self.variables.patch(self.ctx, "9", {"name": "foo"})

        self.assertEqual("fresh", self.ctx.requirement.formalizations[9].name)

    def test_patch_rekeys_the_collection_on_a_rename(self):
        self.variables.create(self.ctx, "9", {"name": "fresh", "type": "bool", "temp_id": 9})

        self.variables.patch(self.ctx, "9", {"name": "renamed"})

        collection = self.ctx.variable_collection.collection
        self.assertNotIn("fresh", collection)
        self.assertIs(self.ctx.requirement.formalizations[9], collection["renamed"])

    def test_patch_carries_the_enumerators_through_a_rename(self):
        """A plain `set_name` renamed the enum alone, leaving `<old>_<variant>` under a dead enum."""
        self.variables.create(
            self.ctx,
            "9",
            {"name": "myenum", "type": "ENUM_INT", "temp_id": 9, "enumerators": [["A", "1"], ["B", "2"]]},
        )

        self.variables.patch(self.ctx, "9", {"name": "renamed"})

        variables = {v.name: v for v in current_app.db.get_objects(Variable).values()}
        self.assertNotIn("myenum_A", variables)
        self.assertNotIn("myenum_B", variables)
        self.assertEqual("renamed", variables["renamed_A"].belongs_to_enum)
        self.assertEqual("renamed", variables["renamed_B"].belongs_to_enum)
