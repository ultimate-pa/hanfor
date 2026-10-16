import unittest
from app import app


class TestPatternsApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_returns_200(self):
        resp = self.client.get("/api/v1/patterns")
        self.assertEqual(resp.status_code, 200)

    def test_response_structure(self):
        resp = self.client.get("/api/v1/patterns")
        data = resp.get_json()
        self.assertIn("groups", data)
        self.assertIn("group_order", data)
        self.assertIn("scopes", data)

    def test_group_order_matches_config(self):
        from config import PATTERNS_GROUP_ORDER

        resp = self.client.get("/api/v1/patterns")
        data = resp.get_json()
        for i, group in enumerate(PATTERNS_GROUP_ORDER):
            if group in data["group_order"]:
                self.assertEqual(data["group_order"][i], group)

    def test_known_pattern_present(self):
        resp = self.client.get("/api/v1/patterns")
        data = resp.get_json()
        all_patterns = {}
        for group, patterns in data["groups"].items():
            for p in patterns:
                all_patterns[p["name"]] = p
        self.assertIn("Absence", all_patterns)
        self.assertEqual(
            all_patterns["Absence"]["text"],
            "it is never the case that {R} holds",
        )
        self.assertEqual(all_patterns["Absence"]["env"], {"R": ["bool"]})

    def test_scopes_contain_common_scopes(self):
        resp = self.client.get("/api/v1/patterns")
        data = resp.get_json()
        scope_values = [s["value"] for s in data["scopes"]]
        self.assertIn("GLOBALLY", scope_values)
        self.assertIn("BEFORE", scope_values)
        self.assertIn("AFTER", scope_values)
        self.assertIn("BETWEEN", scope_values)
        self.assertIn("AFTER_UNTIL", scope_values)
        self.assertIn("NONE", scope_values)

    def test_each_pattern_has_required_fields(self):
        resp = self.client.get("/api/v1/patterns")
        data = resp.get_json()
        for group, patterns in data["groups"].items():
            for p in patterns:
                self.assertIn("name", p)
                self.assertIn("text", p)
                self.assertIn("env", p)

    def test_group_count(self):
        resp = self.client.get("/api/v1/patterns")
        data = resp.get_json()
        core_groups = {
            "Occurence",
            "Order",
            "Real-time",
            "Automaton",
            "not_formalizable",
        }
        self.assertTrue(
            core_groups.issubset(set(data["group_order"])),
            f"Missing core groups: {core_groups - set(data['group_order'])}",
        )
