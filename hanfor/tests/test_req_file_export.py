"""
Characterization tests for `generate_req_file_content`, which had no coverage,
now it is introduced since it's a part of the refactor.

The goal was to remove the `try/except` chains that silently swallowed parts of the export
"""

from unittest import TestCase

from app import app
from lib_core.data import Requirement, SessionValue, Variable, VariableCollection
from lib_core.utils import generate_req_file_content
from tests.mock_hanfor import MockHanfor


class TestReqFileExport(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def content(self, **kwargs) -> str:
        with app.app_context():
            return generate_req_file_content(app, **kwargs)

    def test_full_export(self):
        self.assertEqual(
            "CONST spam_egg IS 1\n"
            "CONST spam_ham IS 2\n"
            "\n"
            "Input bar IS unknown\n"
            "Input foo IS unknown\n"
            "Input spam IS int\n"
            "\n"
            'SysRS_FooXY_42_0: Globally, it is never the case that "foo != bar" holds\n'
            "\n",
            self.content(),
        )

    def test_variables_only_omits_requirements(self):
        content = self.content(variables_only=True)

        self.assertIn("Input foo IS unknown", content)
        self.assertNotIn("SysRS_FooXY_42_0", content)

    def test_variable_constraints_are_exported_in_full(self):
        """Pins the whole constraint list: `except Exception: pass` used to abandon it mid-iteration."""
        with app.app_context():
            var = next(v for v in app.db.get_objects(Variable).values() if v.name == "spam")
            var_collection = VariableCollection(
                app.db.get_objects(Variable).values(), app.db.get_objects(Requirement).values()
            )
            standard_tags = SessionValue.get_standard_tags(app.db)
            for expression in ("spam > 0", "spam < 100"):
                cid = var.add_constraint()
                var.update_constraint(cid, "GLOBALLY", "Absence", {"R": expression}, var_collection, standard_tags)

        content = self.content()

        self.assertIn('Constraint_spam_0: Globally, it is never the case that "spam > 0" holds', content)
        self.assertIn('Constraint_spam_1: Globally, it is never the case that "spam < 100" holds', content)

    def test_filter_list_narrows_variables_and_requirements(self):
        self.assertEqual("\n\n\n", self.content(filter_list=["SysRS FooXY_1"]))
