import tempfile

from parameterized import parameterized
from pyfakefs.fake_filesystem_unittest import TestCase

from req_simulator.Scenario import Scenario

testcases = [
    ({
         'head': {
             'duration': 5,
             'types': {'A': 'bool', 'B': 'int', 'C': 'real'}},
         'data': {
             0: {'A': True, 'B': 1, 'C': 1.0},
             1: {'A': False, 'B': None}}},
    ),
    ({
         'head': {
             'duration': 5,
             'types': {'A': 'bool', 'B': 'int', 'C': 'real'}},
         'data': {
             0: {},
             1: {'A': True, 'B': 5}}},
    ),
]


class TestScenario(TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.test_file = tempfile.NamedTemporaryFile(suffix='.yaml')
        self.test_dir = tempfile.TemporaryFile()

    def tearDown(self):
        self.test_file.close()
        self.test_dir.close()

    @parameterized.expand(testcases)
    def test_scenario(self, obj):
        path = '/test/file.txt'
        self.fs.create_file(path)

        expected = Scenario.from_object(obj)
        Scenario.save_to_file(expected, path)
        actual = Scenario.load_from_file(path)

        self.assertEqual(expected, actual, msg="Error while parsing scenario.")
