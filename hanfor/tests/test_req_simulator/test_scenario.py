import tempfile

from parameterized import parameterized
from pyfakefs.fake_filesystem_unittest import TestCase

from req_simulator.scenario import Scenario

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
    ({
         'head': {
             'duration': 8.92,
             'types': {'number': 'int', 'X': 'bool', 'r0': 'real', 'r1': 'real', 'is_active': 'bool'}},
         'data': {
             0: {'r0': -13.45, 'number': 0, 'is_active': False},
             3: {'X': True, 'r1': 6.02, 'number': 41},
             7.5: {'r0': +54, 'number': 4, 'is_active': True},
             8.92: {'X': False, 'r1': -6.2, 'number': 43}}},
    ),
    ({
         'head': {
             'duration': 8.92,
             'types': {'number': 'int', 'X': 'bool', 'r0': 'real', 'r1': 'real', 'is_active': 'bool'}},
         'data': {
             0: {'r0': -13.45, 'number': 0, 'is_active': False},
             3: {'X': True, 'r1': 6.02, 'number': 41},
             7.5: {'r0': +54, 'number': 4, 'is_active': True},
             8.92: {'X': False, 'r1': -6.2, 'number': 43}}},
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
