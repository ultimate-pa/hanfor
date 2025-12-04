import unittest
from requirements.desc_highlighting import (
    _normalize_variable,
    _normalize_and_group_positions_from_desc,
    _words_between,
    _generate_all_ascending_combinations,
    _filter_combos,
)


class TestNormalizeVariable(unittest.TestCase):

    def assertNorm(self, inp, expected):

        result = _normalize_variable(inp)
        self.assertEqual(expected, result, msg=f"\nInput:    {inp}\nExpected: {expected}\nGot:      {result}")

    def test_simple_cases(self):
        tests = [
            ("vehicle", {"vehicle"}),
            ("foo bar", {"foo", "bar"}),
            ("Speed", {"speed"}),
        ]
        for inp, expected in tests:
            self.assertNorm(inp, expected)

    def test_camel_case(self):
        tests = [
            ("vehicleSpeed", {"vehicle", "speed"}),
            ("ArmoredVehicle", {"armored", "vehicle"}),
            ("JsonHTTPParser", {"json", "http", "parser"}),
            ("xmlParser", {"xml", "parser"}),
            ("userIDNumber", {"user", "id", "number"}),
        ]
        for inp, expected in tests:
            self.assertNorm(inp, expected)

    def test_separators(self):
        tests = [
            ("foo_bar", {"foo", "bar"}),
            ("foo-bar", {"foo", "bar"}),
            ("__vehicle__", {"vehicle"}),
            ("_foo_bar_", {"foo", "bar"}),
        ]
        for inp, expected in tests:
            self.assertNorm(inp, expected)

    def test_spacing(self):
        tests = [
            ("   armored   vehicle  ", {"armored", "vehicle"}),
            (" foo  ", {"foo"}),
            ("foo   bar   baz", {"foo", "bar", "baz"}),
        ]
        for inp, expected in tests:
            self.assertNorm(inp, expected)

    def test_mixed_complex(self):
        tests = [
            ("Speed300MVehicle", {"speed300m", "vehicle"}),
            ("Max-RPM300Value", {"max", "rpm300value"}),
            ("absFoo42Bar", {"abs", "foo42bar"}),
            ("HTTPServer300Error", {"http", "server300error"}),
        ]
        for inp, expected in tests:
            self.assertNorm(inp, expected)

    def test_edge_cases(self):
        tests = [
            ("", set()),
            ("   ", set()),
            ("1234", {"1234"}),
            ("A", {"a"}),
            ("aB", {"a", "b"}),
            ("AB", {"ab"}),
            ("A300X", {"a300x"}),
            ("foo300barBaz", {"foo300bar", "baz"}),
        ]
        for inp, expected in tests:
            self.assertNorm(inp, expected)


class TestNormalizeAndGroupPositions:

    def test_simple_words(self):
        desc = "This is a test"
        result = _normalize_and_group_positions_from_desc(desc)
        expected = {"this": [(0, 4)], "is": [(5, 7)], "a": [(8, 9)], "test": [(10, 14)]}
        assert result == expected

    def test_mixed_case_with_underscore_and_hyphen(self):
        desc = "Power_Input-Speed300M"
        result = _normalize_and_group_positions_from_desc(desc)
        expected = {"power": [(0, 5)], "input": [(6, 11)], "speed300m": [(12, 21)]}
        assert result == expected


class TestWordsBetween(unittest.TestCase):

    def setUp(self):
        self.word_positions = {
            "the": [(0, 3)],
            "quick": [(4, 9)],
            "brown": [(10, 15)],
            "fox": [(16, 19)],
            "jumps": [(20, 25)],
        }

    def test(self):
        self.assertEqual(_words_between((0, 3), (16, 19), self.word_positions), 2)
        self.assertEqual(_words_between((4, 9), (10, 15), self.word_positions), 0)
        self.assertEqual(_words_between((0, 3), (4, 9), self.word_positions), 0)
        self.assertEqual(_words_between((4, 9), (20, 25), self.word_positions), 2)


class TestGenerateAllAscendingCombinations(unittest.TestCase):

    def test_simple_combination(self):
        pos_score_dict = {"speed": [((0, 5), 100)], "vehicle": [((6, 13), 80)]}
        result = _generate_all_ascending_combinations(pos_score_dict, var_word_count=2, threshold=50)
        expected = [(80.0, [(0, 5)]), (60.0, [(6, 13)]), (90.0, [(0, 5), (6, 13)])]
        self.assertEqual(result, expected)

    def test_missing_word_penalty(self):
        pos_score_dict = {"speed": [((0, 5), 100)]}
        result = _generate_all_ascending_combinations(pos_score_dict, var_word_count=2, threshold=50)
        expected = [(80.0, [(0, 5)])]
        self.assertEqual(result, expected)

    def test_threshold_filtering(self):
        pos_score_dict = {"speed": [((0, 5), 30)], "vehicle": [((6, 13), 40)]}
        result = _generate_all_ascending_combinations(pos_score_dict, var_word_count=2, threshold=50)
        expected = []
        self.assertEqual(result, expected)

    def test_multiple_positions_per_word(self):
        pos_score_dict = {"speed": [((0, 5), 100), ((1, 6), 80)], "vehicle": [((6, 13), 90)]}
        result = _generate_all_ascending_combinations(pos_score_dict, var_word_count=2, threshold=50)
        expected = [
            (80.0, [(0, 5)]),
            (60.0, [(1, 6)]),
            (70.0, [(6, 13)]),
            (95.0, [(0, 5), (6, 13)]),
            (85.0, [(1, 6), (6, 13)]),
        ]
        self.assertEqual(result, expected)


class TestFilterCombos(unittest.TestCase):

    def test_simple_gap(self):
        combos = [(90, [(0, 5), (6, 13)]), (80, [(0, 5)]), (60, [(6, 13)])]
        word_positions = {"speed": [(0, 5)], "vehicle": [(6, 13)]}
        result = _filter_combos(combos, max_gap=1, word_positions=word_positions)
        expected = [(90, 0, 13, [(0, 5), (6, 13)])]
        self.assertEqual(result, expected)

    def test_gap_filtering(self):
        combos = [(90, [(0, 5), (10, 15)]), (70, [(0, 5), (6, 13)])]
        word_positions = {"speed": [(0, 5)], "vehicle": [(6, 13)], "fast": [(10, 15)]}
        result = _filter_combos(combos, max_gap=1, word_positions=word_positions)
        expected = [(90, 0, 15, [(0, 5), (10, 15)])]
        self.assertEqual(result, expected)

    def test_overlap_removal(self):
        combos = [(90, [(0, 5), (6, 13)]), (80, [(4, 10)])]
        word_positions = {"speed": [(0, 5)], "vehicle": [(6, 13)], "fast": [(4, 10)]}
        result = _filter_combos(combos, max_gap=1, word_positions=word_positions)
        expected = [(90, 0, 13, [(0, 5), (6, 13)])]
        self.assertEqual(result, expected)

    def test_single_positions(self):
        combos = [(80, [(0, 5)]), (60, [(6, 13)])]
        word_positions = {"speed": [(0, 5)], "vehicle": [(6, 13)]}
        result = _filter_combos(combos, max_gap=0, word_positions=word_positions)
        expected = [(80, 0, 5, [(0, 5)]), (60, 6, 13, [(6, 13)])]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
