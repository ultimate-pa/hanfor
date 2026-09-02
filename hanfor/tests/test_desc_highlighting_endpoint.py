"""
Tests for the FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING branch of `GET api/v1/req/<rid>`

The feature is off by default (`config.dist.py`), so without these tests the code is never executed
"""

from unittest import TestCase

from app import app
from requirements.desc_highlighting import requirement_highlighting_data_per_req
from tests.mock_hanfor import MockHanfor

RID = "SysRS FooXY_42"
RID_URL = "api/v1/req/SysRS%20FooXY_42"


class TestHighlightedDescEndpoint(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"] = True
        requirement_highlighting_data_per_req.clear()

    def tearDown(self) -> None:
        app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"] = False
        requirement_highlighting_data_per_req.clear()
        self.mock_hanfor.tear_down()

    def test_empty_cache_is_highlighted_on_the_fly(self):
        self.assertNotIn(RID, requirement_highlighting_data_per_req)

        result = self.mock_hanfor.app.get(RID_URL)

        self.assertEqual(200, result.status_code)
        self.assertTrue(result.json["desc_highlighted"])
        self.assertIn(RID, requirement_highlighting_data_per_req)

    def test_cached_value_is_served_unchanged(self):
        self.mock_hanfor.app.get(RID_URL)
        requirement_highlighting_data_per_req[RID].highlighted_desc = "<mark>cached</mark>"

        result = self.mock_hanfor.app.get(RID_URL)

        self.assertEqual("<mark>cached</mark>", result.json["desc_highlighted"])

    def test_placeholder_entry_is_recomputed(self):
        """`generate_all_highlighted_desc` seeds entries with the plain description, which counts as a miss."""
        plain = self.mock_hanfor.app.get(RID_URL).json["desc"]
        requirement_highlighting_data_per_req[RID].highlighted_desc = plain

        result = self.mock_hanfor.app.get(RID_URL)

        self.assertEqual(200, result.status_code)
        self.assertTrue(result.json["desc_highlighted"])

    def test_feature_disabled_serves_plain_description(self):
        app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"] = False

        result = self.mock_hanfor.app.get(RID_URL)

        self.assertEqual(result.json["desc"], result.json["desc_highlighted"])
        self.assertNotIn(RID, requirement_highlighting_data_per_req)
