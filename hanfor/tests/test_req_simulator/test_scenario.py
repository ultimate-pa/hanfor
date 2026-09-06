import tempfile

from parameterized import parameterized
from pyfakefs.fake_filesystem_unittest import TestCase
from pysmt.environment import Environment

from req_simulator.scenario import Scenario

testcases = [
    (
        {
            "head": {"duration": 10.0, "times": [0.0, 1.0, 2.0, 3.0]},
            "data": {
                "A": {"type": "Bool", "values": [0, 1, 1, 1]},
                "B": {"type": "Int", "values": [0, 5, 10, 0]},
                "C": {"type": "Real", "values": [0.0, 5.0, 10.0, 0.0]},
            },
        },
    )  # Do not remove this comma ;-)
]


class TestScenario(TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.test_file = tempfile.NamedTemporaryFile(suffix=".yaml")
        self.test_dir = tempfile.TemporaryFile()

    def tearDown(self):
        self.test_file.close()
        self.test_dir.close()

    @parameterized.expand(testcases)
    def test_scenario(self, object):
        path = "/test/file.txt"
        self.fs.create_file(path)

        smt_env: Environment = Environment()
        expected = Scenario(smt_env).from_object(object)
        expected.save_to_file(path)
        actual = Scenario(smt_env).load_from_file(path)

        self.assertEqual(expected.variables, actual.variables, msg="Error while parsing scenario.")
        self.assertEqual(expected.times, actual.times, msg="Error while parsing scenario.")
        self.assertEqual(expected.types, actual.types, msg="Error while parsing scenario.")
