from unittest import TestCase

from tests.mock_hanfor import MockHanfor, variable_url


class TestVariableConstraints(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.app = self.mock_hanfor.app
        self.url = variable_url(self.app, "spam", "/constraints")

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def constraints(self) -> dict:
        return {c["id"]: c for c in self.app.get(self.url).json}

    def test_batch_create_keeps_valid_drafts_and_reports_invalid(self):
        response = self.app.post(
            self.url,
            json=[
                {
                    "temp_id": "good",
                    "scope": "GLOBALLY",
                    "pattern": "Universality",
                    "expression_mapping": {"R": "spam > 0"},
                },
                {
                    "temp_id": "bad",
                    "scope": "GLOBALLY",
                    "pattern": "Universality",
                    "expression_mapping": {"R": "spam >"},
                },
            ],
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual({"good": 0}, response.json["ids"])
        self.assertEqual(["bad"], list(response.json["errors"]))
        constraint = self.constraints()[0]
        self.assertEqual("spam > 0", constraint["expr_R"])
        self.assertEqual("formalization", constraint["formalization_type"])
        self.assertIn("spam > 0", constraint["text"])
        self.assertEqual([0], list(self.constraints()))

    def test_body_must_be_a_list_of_drafts(self):
        self.assertEqual(400, self.app.post(self.url, json={"temp_id": "a"}).status_code)
        self.assertEqual(400, self.app.post(self.url, json=["a"]).status_code)
        self.assertEqual({}, self.constraints())

    def test_patch_changes_only_sent_fields_and_rejects_invalid_expression(self):
        draft = {
            "temp_id": "a",
            "scope": "GLOBALLY",
            "pattern": "Universality",
            "expression_mapping": {"R": "spam > 0"},
        }
        self.app.post(self.url, json=[draft])

        response = self.app.patch(f"{self.url}/0", json={"expression_mapping": {"R": "spam > 5"}})
        self.assertEqual(200, response.status_code)
        self.assertEqual("spam > 5", self.constraints()[0]["expr_R"])
        self.assertEqual("GLOBALLY", self.constraints()[0]["scope"])

        response = self.app.patch(f"{self.url}/0", json={"scope": "BEFORE", "expression_mapping": {"R": "spam >"}})
        self.assertEqual(400, response.status_code)
        self.assertEqual("GLOBALLY", self.constraints()[0]["scope"])
        self.assertEqual("spam > 5", self.constraints()[0]["expr_R"])

        self.assertEqual(404, self.app.patch(f"{self.url}/7", json={}).status_code)

    def test_constraint_without_needed_expressions_is_rejected(self):
        draft = {"temp_id": "a", "scope": "BEFORE", "pattern": "Existence", "expression_mapping": {"R": "spam > 0"}}
        response = self.app.post(self.url, json=[draft])
        self.assertEqual(400, response.status_code)
        self.assertIn("P", response.json["errors"]["a"])
        self.assertEqual({}, self.constraints())

        draft = {"temp_id": "b", "scope": "GLOBALLY", "pattern": "Existence", "expression_mapping": {"R": "spam > 0"}}
        self.app.post(self.url, json=[draft])
        response = self.app.patch(f"{self.url}/0", json={"scope": "BETWEEN"})
        self.assertEqual(400, response.status_code)
        self.assertEqual("GLOBALLY", self.constraints()[0]["scope"])
        self.assertEqual(200, self.app.patch(f"{self.url}/0", json={"pattern": "Universality"}).status_code)
