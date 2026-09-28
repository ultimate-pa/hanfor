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
        fid = self.variables.create(self.ctx, "tmp-1", {"name": "handlervar", "type": "bool"})

        with self.assertRaises(SubtypeNotFound):
            self.formalizations.fetch(self.ctx, str(fid))

    def test_fetch_rejects_a_missing_id(self):
        with self.assertRaises(SubtypeNotFound) as caught:
            self.variables.fetch(self.ctx, "404")

        self.assertEqual("Variable not found.", str(caught.exception))

    # create
    def test_create_assigns_the_id_and_returns_it(self):
        fid = self.formalizations.create(self.ctx, "tmp-1", FORMALIZATION)

        self.assertIn(fid, self.ctx.requirement.formalizations)

    def test_create_gives_two_drafts_sharing_a_temp_id_distinct_ids(self):
        """Two clients both propose `tmp-1`; neither may land on the other."""
        first = self.formalizations.create(self.ctx, "tmp-1", FORMALIZATION)
        second = self.formalizations.create(self.ctx, "tmp-1", FORMALIZATION)

        self.assertNotEqual(first, second)
        self.assertIn(first, self.ctx.requirement.formalizations)
        self.assertIn(second, self.ctx.requirement.formalizations)

    def test_create_rejects_an_incomplete_payload_without_mutating(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload):
            self.formalizations.create(self.ctx, "tmp-1", {})

        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    def test_create_rolls_back_a_draft_it_could_not_fill(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload):
            self.formalizations.create(self.ctx, "tmp-1", {**FORMALIZATION, "scope": "NOT_A_SCOPE"})

        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    # patch
    def test_patch_leaves_the_fields_it_was_not_given(self):
        self.formalizations.patch(self.ctx, "0", {"scope": "AFTER"})

        formalization = self.ctx.requirement.formalizations[0]
        self.assertEqual("AFTER", formalization.scoped_pattern.scope.name)
        self.assertEqual("Absence", formalization.scoped_pattern.pattern.get_name())

    def test_patch_rejects_an_illegal_variable_name(self):
        fid = self.variables.create(self.ctx, "tmp-1", {"name": "goodname", "type": "bool"})

        with self.assertRaises(InvalidPayload):
            self.variables.patch(self.ctx, str(fid), {"name": "9illegal"})

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
            self.formalizations.create(self.ctx, "tmp-1", {**FORMALIZATION, "scope": None})

        self.assertEqual("Missing required field(s): scope", str(caught.exception))

    def test_create_rejects_a_null_pattern_without_mutating(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload):
            self.formalizations.create(self.ctx, "tmp-1", {**FORMALIZATION, "pattern": None})

        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    def test_create_registers_an_enum_variable_exactly_once(self):
        """`create_enum_variable` used to find the name free and build a second object under it, leaving both there"""
        self.variables.create(
            self.ctx,
            "tmp-1",
            {"name": "myenum", "type": "ENUM_INT", "enumerators": [["A", "1"], ["B", "2"]]},
        )

        names = [v.name for v in current_app.db.get_objects(Variable).values()]
        self.assertEqual(1, names.count("myenum"))

    def test_create_attaches_the_object_the_collection_holds(self):
        fid = self.variables.create(self.ctx, "tmp-1", {"name": "fresh", "type": "bool"})

        self.assertIs(self.ctx.variable_collection.collection["fresh"], self.ctx.requirement.formalizations[fid])

    def test_create_rejects_a_taken_name_without_attaching(self):
        before = dict(self.ctx.requirement.formalizations)

        with self.assertRaises(InvalidPayload) as caught:
            self.variables.create(self.ctx, "tmp-1", {"name": "foo", "type": "bool"})

        self.assertEqual("A variable named `foo` already exists.", str(caught.exception))
        self.assertDictEqual(before, self.ctx.requirement.formalizations)

    def test_patch_rejects_a_rename_onto_a_taken_name(self):
        fid = self.variables.create(self.ctx, "tmp-1", {"name": "fresh", "type": "bool"})
        with self.assertRaises(InvalidPayload):
            self.variables.patch(self.ctx, str(fid), {"name": "foo"})

        self.assertEqual("fresh", self.ctx.requirement.formalizations[fid].name)

    def test_patch_rekeys_the_collection_on_a_rename(self):
        fid = self.variables.create(self.ctx, "tmp-1", {"name": "fresh", "type": "bool"})

        self.variables.patch(self.ctx, str(fid), {"name": "renamed"})

        collection = self.ctx.variable_collection.collection
        self.assertNotIn("fresh", collection)
        self.assertIs(self.ctx.requirement.formalizations[fid], collection["renamed"])

    def test_patch_carries_the_enumerators_through_a_rename(self):
        """A plain `set_name` renamed the enum alone, leaving `<old>_<variant>` under a dead enum."""
        fid = self.variables.create(
            self.ctx,
            "tmp-1",
            {"name": "myenum", "type": "ENUM_INT", "enumerators": [["A", "1"], ["B", "2"]]},
        )

        self.variables.patch(self.ctx, str(fid), {"name": "renamed"})

        variables = {v.name: v for v in current_app.db.get_objects(Variable).values()}
        self.assertNotIn("myenum_A", variables)
        self.assertNotIn("myenum_B", variables)
        self.assertEqual("renamed", variables["renamed_A"].belongs_to_enum)
        self.assertEqual("renamed", variables["renamed_B"].belongs_to_enum)
