"""example_input/ignition.csv and ignition_testscenarios.req: a new session with the formalizations of the csv, the
.req export of every group and the import of the test scenarios."""

import csv
import io
import json
import os
import shutil
from unittest import TestCase

from tests.mock_hanfor import MockHanfor

EXAMPLES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "example_input")
# headers: ID, Description, formalization (default), Type; import data, formalizations, tags and status: yes;
# Hanfor_Tags and Hanfor_Status (defaults); base variable collection: no
ANSWERS = ["", 0, "", 3, 1, 1, 1, "", "", 0]


class TestIgnitionExample(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=[], test_session_source="test_empty_session")
        self.mock_hanfor.set_up()
        # not inside the session folder, Hanfor would take it for an existing session
        folder = os.path.join(self.mock_hanfor.test_session_base_folder, "csv")
        os.makedirs(folder)
        shutil.copy(os.path.join(EXAMPLES, "ignition.csv"), folder)
        self.assertTrue(self.mock_hanfor.startup_hanfor(os.path.join("..", "csv", "ignition.csv"), "ignition", ANSWERS))
        self.client = self.mock_hanfor.app

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def export(self, ids: list[str], with_test_scenarios: bool = True) -> str:
        data = {"selected_requirement_ids": json.dumps(ids), "include_test_scenarios": str(with_test_scenarios).lower()}
        return self.client.post("/api/tools/req_file", data=data).data.decode()

    def test_groups_are_exported(self):
        text = self.export(["IGN_1", "IGN_2", "IGN_3", "IGN_4", "RT_1", "RT_2", "VAC_1", "VAC_2"])
        for line in [
            "Input key_inserted IS bool",
            "Input battery_low IS bool",
            'IGN_1_0: Globally, it is always the case that if "brake_pressed && key_inserted && key_turned" holds, '
            'then "engine_on" holds after at most "2.0" time units',
            'RT_2_0: Globally, it is always the case that if "battery_low" holds, then "!starter_on" holds for at '
            'least "5.0" time units',
            'VAC_2_0: Globally, it is always the case that if "car_locked" holds, then "door_closed" holds as well',
        ]:
            self.assertIn(line, text)
        self.assertNotIn("IS unknown", text)
        self.assertIn('INC_1_0: Globally, it is always the case that "lights_on" holds', self.export(["INC_1"]))

    def test_test_scenarios_can_be_imported(self):
        with open(os.path.join(EXAMPLES, "ignition_testscenarios.req"), "rb") as f:
            data = {"file": (io.BytesIO(f.read()), "ignition_testscenarios.req")}
        report = self.client.post("/api/v1/test_scenarios/import", data=data, content_type="multipart/form-data").json
        self.assertEqual([], report["errors"])
        self.assertEqual(8, len(report["imported"]))

        # only group_ok: the 3 scenarios of its requirements, the 5 global ones need all requirements
        text = self.export(["IGN_1", "IGN_2", "IGN_3", "IGN_4"])
        self.assertEqual(3, text.count(": TestScenario for "))
        self.assertIn("TS_IGN_1_POS_1: TestScenario for IGN_1, trace has to hold:", text)
        self.assertIn("// 5 global test scenarios left out", text)
        with open(os.path.join(EXAMPLES, "ignition.csv"), newline="") as f:
            self.assertEqual(8, self.export([row["ID"] for row in csv.DictReader(f)]).count(": TestScenario for "))
        self.assertNotIn("TestScenario for", self.export(["IGN_1"], with_test_scenarios=False))
