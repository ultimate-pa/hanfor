"""Test scenarios: a table of their own, either of one requirement (requirement_id) or global ("")."""

import io
import json
from unittest import TestCase

from app import app
from lib_core.data import Requirement, Variable, VariableCollection
from lib_core.utils import rename_variable_everywhere
from tests.mock_hanfor import MockHanfor
from ultimate.ultimate_job import UltimateJob, apply_test_scenario_results

API = "/api/v1/test_scenarios"
RID = "SysRS FooXY_42"
ALL = ["SysRS FooXY_91", RID]  # every requirement of simple.csv
SCENARIO = {
    "desired_behavior": True,
    "description": "Key turned -> engine on",
    "lanes": ["foo", "spam == spam_egg"],
    "steps": [
        {"duration": 1, "states": {"foo": True}},
        {"duration": 2, "states": {"spam == spam_egg": True}},
    ],
}


class TestTestScenarios(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
        self.mock_hanfor.set_up()
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.client = self.mock_hanfor.app

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def create(self, **changes) -> dict:
        response = self.client.post(API, json={**SCENARIO, **changes})
        self.assertEqual(201, response.status_code, response.json)
        return response.json["scenario"]

    def export(self, ids: list[str], **form) -> str:
        # the export button always sends the visible requirement ids
        data = {"selected_requirement_ids": json.dumps(ids), **form}
        return self.client.post("/api/tools/req_file", data=data).data.decode()

    def test_default_names(self):
        self.assertEqual("TS_GLOBAL_POS_1", self.create()["name"])
        self.assertEqual("TS_GLOBAL_POS_2", self.create()["name"])
        self.assertEqual("TS_GLOBAL_NEG_1", self.create(desired_behavior=False)["name"])
        self.assertEqual("TS_SysRS_FooXY_42_POS_1", self.create(requirement_id=RID)["name"])

    def test_list_by_owner(self):
        local = self.create(requirement_id=RID)
        global_ = self.create()
        self.assertEqual(
            [local["id"]], [s["id"] for s in self.client.get(f"{API}?requirement_id={RID}").json["scenarios"]]
        )
        self.assertEqual([global_["id"]], [s["id"] for s in self.client.get(f"{API}?global=true").json["scenarios"]])
        self.assertEqual(2, len(self.client.get(API).json["scenarios"]))

    def test_unknown_requirement(self):
        response = self.client.post(API, json={**SCENARIO, "requirement_id": "nope"})
        self.assertEqual(404, response.status_code)

    def test_names_are_cleaned_and_unique_over_all(self):
        self.assertEqual("Motor_startet", self.create(name="Motor startet!")["name"])
        response = self.client.post(API, json={**SCENARIO, "requirement_id": RID, "name": "Motor startet"})
        self.assertEqual(400, response.status_code)

    def test_non_boolean_lane_is_rejected(self):
        response = self.client.post(API, json={**SCENARIO, "lanes": ["spam"], "steps": []})
        self.assertEqual(400, response.status_code)

    def test_delete_does_not_reuse_id(self):
        first = self.create()
        self.assertEqual(200, self.client.delete(f"{API}/{first['id']}").status_code)
        self.assertNotEqual(first["id"], self.create()["id"])
        self.assertEqual(404, self.client.delete(f"{API}/{first['id'] + 100}").status_code)

    def test_requirement_has_no_test_scenarios_in_its_formalizations(self):
        self.create(requirement_id=RID)
        types = {f["formalization_type"] for f in self.client.get(f"/api/v1/req/{RID}/formalizations").json}
        self.assertNotIn("test_scenario", types)

    def test_export(self):
        self.create(name="Global")
        self.create(name="Local", requirement_id=RID)
        text = self.export(ALL)
        self.assertIn(
            "Local: TestScenario for SysRS_FooXY_42, trace has to hold: (1.0, foo), (2.0, spam == spam_egg)", text
        )
        self.assertIn("Global: TestScenario for ALL, trace has to hold:", text)
        # the scenario of a requirement comes right after it, the global ones at the end
        self.assertLess(text.index("SysRS_FooXY_42_0:"), text.index("Local:"))
        self.assertLess(text.index("Local:"), text.index("Global:"))
        self.assertNotIn("left out", text)

        # the variables of a scenario are declared, even if no exported requirement uses them
        text = self.export([RID])
        self.assertIn("Input foo IS", text)
        self.assertIn("CONST spam_egg IS 1", text)

        # without the requirement: not its scenario
        self.assertNotIn("Local:", self.export([]))

    def test_global_only_if_all_requirements_are_exported(self):
        self.create(name="Global")
        self.create(name="Local", requirement_id=RID)
        # a part of the requirements: the global scenario would fail or pass for the wrong reason
        text = self.export([])
        self.assertNotIn("Global: TestScenario for", text)
        self.assertIn("// 1 global test scenarios left out: only 0 of 1 formalized requirements exported", text)
        # in this session only RID has a formalization, the other one restricts nothing and is not needed
        text = self.export([RID])
        self.assertIn("Local: TestScenario for", text)
        self.assertIn("Global: TestScenario for ALL", text)
        self.assertNotIn("left out", text)

    def test_export_without_test_scenarios(self):
        self.create(name="Global")
        self.create(name="Local", requirement_id=RID)
        text = self.export([RID], include_test_scenarios="false")
        self.assertNotIn("TestScenario for", text)
        self.assertIn("SysRS_FooXY_42_0:", text)

    def test_ultimate_results(self):
        passed = self.create(name="Pos", requirement_id=RID)
        failed = self.create(name="Neg", desired_behavior=False)
        missing = self.create(name="Missing")
        summary = "\n".join(
            [
                "",
                "Test Scenario Summary",
                "---------------------",
                "Passed: 1/3",
                "Passed (1):",
                "  - TestScenario Pos is possible, as required",
                "Failed (1):",
                "  - TestScenario Neg is possible, though forbidden (test scenario failed)",
                "      Run on which the forbidden trace holds:",
                "        [0;1]       foo=true",
                "",
            ]
        )
        job = UltimateJob(
            job_id="job1",
            requirement_file=self.export(ALL),
            toolchain_id="ReqCheck",
            toolchain_xml="",
            usersettings_name="",
            usersettings_json="",
            results=[{"shortDesc": "Test scenarios: 1/3 passed", "longDesc": summary, "type": "UNDEF"}],
        )
        with app.app_context():
            apply_test_scenario_results(job)

        def result(scenario):
            return self.client.get(f"{API}/{scenario['id']}").json["scenario"]["ultimate_result"]

        self.assertEqual("passed", result(passed)["status"])
        self.assertEqual("failed", result(failed)["status"])
        self.assertEqual("Run on which the forbidden trace holds:\n  [0;1]       foo=true", result(failed)["details"])
        self.assertEqual("not_analyzed", result(missing)["status"])
        self.assertEqual("job1", result(passed)["job_id"])

    def test_rename_variable_reaches_scenarios(self):
        local = self.create(requirement_id=RID)
        global_ = self.create()
        with app.app_context():
            collection = VariableCollection(app.db.get_objects(Variable).values(), app.db.get_objects(Requirement).values())
            rename_variable_everywhere(collection, "foo", "foo2")
        for scenario in (local, global_):
            renamed = self.client.get(f"{API}/{scenario['id']}").json["scenario"]
            self.assertEqual(["foo2", "spam == spam_egg"], renamed["lanes"])
            self.assertEqual({"foo2": True}, renamed["steps"][0]["states"])

    def import_file(self, text: str, replace: bool = False) -> dict:
        data = {"file": (io.BytesIO(text.encode()), "scenarios.req"), "replace": str(replace).lower()}
        return self.client.post(f"{API}/import", data=data, content_type="multipart/form-data").json

    def test_import(self):
        text = (
            "// a comment\n"
            "X1: TestScenario for ALL, trace is forbidden to hold: (1.0, foo && !(spam == spam_egg))\n"
            "X2: TestScenario for SysRS_FooXY_42, trace has to hold: (2, foo), (1.5, true)\n"
            "X3: TestScenario for nope, trace has to hold: (2, foo)\n"
        )
        report = self.import_file(text)
        self.assertEqual(["X1", "X2"], report["imported"])
        self.assertEqual(1, len(report["errors"]))
        self.assertTrue(report["errors"][0].startswith("line 4:"))

        scenarios = {s["name"]: s for s in self.client.get(API).json["scenarios"]}
        self.assertEqual("", scenarios["X1"]["requirement_id"])
        self.assertFalse(scenarios["X1"]["desired_behavior"])
        self.assertEqual({"foo": True, "spam == spam_egg": False}, scenarios["X1"]["steps"][0]["states"])
        self.assertEqual(RID, scenarios["X2"]["requirement_id"])
        self.assertEqual([2.0, 1.5], [step["duration"] for step in scenarios["X2"]["steps"]])

        self.assertEqual(["X1", "X2"], self.import_file(text)["skipped"])
        self.assertEqual(["X1", "X2"], self.import_file(text, replace=True)["imported"])
        self.assertEqual(2, len(self.client.get(API).json["scenarios"]))

    def test_export_can_be_imported_again(self):
        self.create(name="Global")
        self.create(name="Local", requirement_id=RID)
        exported = self.export(ALL)
        for scenario in self.client.get(API).json["scenarios"]:
            self.client.delete(f"{API}/{scenario['id']}")
        self.assertEqual(["Local", "Global"], self.import_file(exported)["imported"])
        self.assertEqual(exported, self.export(ALL))

    def test_page_loads(self):
        self.assertEqual(200, self.client.get("/test_scenarios").status_code)

