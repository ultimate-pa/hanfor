import os

from parameterized import parameterized
from pyfakefs.fake_filesystem_unittest import TestCase

testcases = [
    ({
         'head': {
             'duration': 6,
             'types': {'R': bool}
         },
         'data': {
             0: {'R': True},
             5: {'R': True}
         }
     },)
]


class TestScenario(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    @parameterized.expand(testcases)
    def test_simulator(self, a):
        file_path = '/test/file.yaml'
        self.assertFalse(os.path.exists(file_path))
        self.fs.create_file(file_path)
        self.assertTrue(os.path.exists(file_path))

        # scenario = Scenario.parse_from_yaml_string(yaml_str)

        # self.assertEqual(expected, actual, msg="Error while simulating scenario.")

        print()
