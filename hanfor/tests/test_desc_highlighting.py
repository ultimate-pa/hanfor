import time
from unittest import TestCase

from ai_addons.threading_ai_socketio import SendUpdateThreadingAndAi
from lib_core.data import Requirement
from requirements.desc_highlighting import (
    _words_between,
    _normalize_variable,
    _generate_combinations,
    _filter_combos,
    RequirementHighlightingData,
    requirement_highlighting_data_per_req,
    generate_all_highlighted_desc,
    VariableMatch,
    delete_variables,
    _highlight_desc_variable,
    _generate_md_description,
)
from thread_handling.threading_core import ThreadHandler, ThreadTask, SchedulingClass, ThreadGroup


class TestWordsBetween(TestCase):
    def test_direct_word_starts(self):
        all_word_starts = [0, 5, 10, 15, 20, 25, 30]
        self.assertTrue(_words_between(0, 5, all_word_starts, max_gap=1))
        self.assertFalse(_words_between(0, 10, all_word_starts, max_gap=1))
        self.assertTrue(_words_between(5, 15, all_word_starts, max_gap=2))
        self.assertFalse(_words_between(10, 20, all_word_starts, max_gap=1))
        self.assertTrue(_words_between(15, 20, all_word_starts, max_gap=1))

    def test_between_word_starts(self):
        all_word_starts = [0, 5, 10, 15, 20, 25, 30]
        self.assertTrue(_words_between(2, 12, all_word_starts, max_gap=2))
        self.assertFalse(_words_between(2, 17, all_word_starts, max_gap=2))
        self.assertTrue(_words_between(6, 18, all_word_starts, max_gap=3))
        self.assertFalse(_words_between(0, 29, all_word_starts, max_gap=5))
        self.assertTrue(_words_between(3, 10, all_word_starts, max_gap=1))

    def test_same_position(self):
        all_word_starts = [0, 5, 10, 15]
        self.assertTrue(_words_between(0, 0, all_word_starts, max_gap=0))
        self.assertTrue(_words_between(5, 5, all_word_starts, max_gap=0))
        self.assertTrue(_words_between(10, 10, all_word_starts, max_gap=1))
        self.assertTrue(_words_between(15, 15, all_word_starts, max_gap=0))
        self.assertTrue(_words_between(0, 10, all_word_starts, max_gap=2))

    def test_edge_cases(self):
        all_word_starts = [0, 5, 10, 15, 20, 25, 30]
        self.assertTrue(_words_between(-5, 0, all_word_starts, max_gap=0))
        self.assertTrue(_words_between(0, 15, all_word_starts, max_gap=3))
        self.assertFalse(_words_between(20, 40, all_word_starts, max_gap=1))
        self.assertTrue(_words_between(-1, 12, all_word_starts, max_gap=3))


class TestNormalizeVariable(TestCase):
    def test_simple_camel_case(self):
        self.assertEqual(_normalize_variable("myVariableNameTest"), {"variable", "name", "test"})
        self.assertEqual(_normalize_variable("anotherExampleHere"), {"another", "example", "here"})
        self.assertEqual(_normalize_variable("finalCheckNow"), {"final", "check", "now"})

    def test_preserve_numbers(self):
        self.assertEqual(_normalize_variable("300MhzSpeedTest"), {"300mhz", "speed", "test"})
        self.assertEqual(_normalize_variable("128GBMemoryUnit"), {"128gb", "memory", "unit"})
        self.assertEqual(_normalize_variable("500kvPowerLine"), {"500kv", "power", "line"})

    def test_underscores_and_dashes(self):
        self.assertEqual(_normalize_variable("my_variable-name-test"), {"variable", "name", "test"})
        self.assertEqual(_normalize_variable("another_var-TestCase"), {"another", "var", "test", "case"})
        self.assertEqual(_normalize_variable("final_example-TestOne"), {"final", "example", "test", "one"})

    def test_short_tokens_removed(self):
        self.assertEqual(_normalize_variable("aVariableXTest"), {"variable", "test"})
        self.assertEqual(_normalize_variable("bMyVarYCheck"), {"var", "check"})
        self.assertEqual(_normalize_variable("cSomeVarZ"), {"some", "var"})

    def test_mixed_cases(self):
        self.assertEqual(_normalize_variable("JSONDataParserTest"), {"json", "data", "parser", "test"})
        self.assertEqual(_normalize_variable("HTTPRequestHandler"), {"http", "request", "handler"})
        self.assertEqual(_normalize_variable("XMLHttpRequestObject"), {"xml", "http", "request", "object"})

    def test_enums(self):
        self.assertEqual(_normalize_variable("my_variable_ALL"), {"all", "variable"})
        self.assertEqual(_normalize_variable("my_variable_TEMP"), {"temp", "variable"})
        self.assertEqual(_normalize_variable("another_enum_MAX"), {"max", "another", "enum"})

    def test_empty_after_filter(self):
        """all tokens <= 2 chars -> empty result"""
        result = _normalize_variable("a_b")
        self.assertEqual(result, set())

    def test_preserves_number_letter_token(self):
        """digits followed by 1-2 letters kept as-is"""
        result = _normalize_variable("300M")
        self.assertIn("300m", result)

    def test_preserves_two_letter_suffix(self):
        result = _normalize_variable("128GB")
        self.assertIn("128gb", result)


class TestGenerateCombinations(TestCase):
    def test_simple_combinations(self):
        pos_score_dict = {"var1": [((0, 2), 10)], "var2": [((3, 5), 15)], "var3": [((6, 8), 5)]}
        var_fragments = {"var1", "var2", "var3"}
        max_gap = 3
        threshold = 0
        min_coverage = 0.5
        all_word_starts = [0, 3, 6, 9]

        combos = _generate_combinations(
            pos_score_dict, var_fragments, max_gap, threshold, min_coverage, all_word_starts
        )

        self.assertTrue(len(combos) > 0)
        expected_positions = [[(0, 2), (3, 5), (6, 8)]]
        self.assertEqual(combos[0][1], expected_positions[0])
        expected_avg_score = (10 + 15 + 5) / 3
        self.assertAlmostEqual(combos[0][0], expected_avg_score)

    def test_missing_fragment_punishment(self):
        pos_score_dict = {"var1": [((0, 2), 10)], "var2": [((3, 5), 15)]}
        var_fragments = {"var1", "var2", "var3"}
        max_gap = 3
        threshold = -50
        min_coverage = 0.5
        all_word_starts = [0, 3, 6]

        combos = _generate_combinations(
            pos_score_dict, var_fragments, max_gap, threshold, min_coverage, all_word_starts
        )
        self.assertTrue(len(combos) > 0)

    def test_gap_too_large(self):
        pos_score_dict = {"var1": [((0, 2), 10)], "var2": [((10, 12), 15)]}
        var_fragments = {"var1", "var2"}
        max_gap = 0
        threshold = 0
        min_coverage = 0.5
        all_word_starts = [0, 3, 6, 10]

        combos = _generate_combinations(
            pos_score_dict, var_fragments, max_gap, threshold, min_coverage, all_word_starts
        )
        self.assertEqual(combos, [])

    def test_skips_same_start_position(self):
        """duplicate start position in pos_score_dict -> second entry skipped"""
        pos_score_dict = {
            "foo": [((0, 3), 90.0), ((0, 5), 85.0)],
            "bar": [((10, 13), 90.0)],
        }
        combos = _generate_combinations(
            pos_score_dict, {"foo", "bar"}, max_gap=5, threshold=50, min_coverage=0.5, all_word_starts=[0, 10]
        )
        for _, positions in combos:
            starts = [p[0] for p in positions]
            self.assertEqual(len(starts), len(set(starts)))


class TestFilterCombos(TestCase):
    def test_simple_non_overlapping(self):
        combos = [(10, [(0, 2), (3, 5)]), (15, [(6, 8), (9, 12)])]
        filtered = _filter_combos(combos)
        self.assertIn((10, 0, 5, [(0, 2), (3, 5)]), filtered)
        self.assertIn((15, 6, 12, [(6, 8), (9, 12)]), filtered)

    def test_overlapping_lower_score_removed(self):
        combos = [(10, [(0, 5)]), (15, [(3, 7)])]
        filtered = _filter_combos(combos)
        self.assertIn((15, 3, 7, [(3, 7)]), filtered)
        self.assertNotIn((10, 0, 5, [(0, 5)]), filtered)

    def test_multiple_overlaps(self):
        combos = [(8, [(0, 2)]), (12, [(1, 3)]), (10, [(4, 6)]), (15, [(5, 7)])]
        filtered = _filter_combos(combos)
        self.assertIn((12, 1, 3, [(1, 3)]), filtered)
        self.assertNotIn((8, 0, 2, [(0, 2)]), filtered)
        self.assertIn((15, 5, 7, [(5, 7)]), filtered)
        self.assertNotIn((10, 4, 6, [(4, 6)]), filtered)

    def test_selected_start_end(self):
        combos = [(10, [(2, 4), (5, 8)])]
        filtered = _filter_combos(combos)
        self.assertIn((10, 2, 8, [(2, 4), (5, 8)]), filtered)

    def test_empty(self):
        combos = []
        filtered = _filter_combos(combos)
        self.assertTrue([] == filtered)


class TestHighlightDescVariable(TestCase):
    def test_skips_insufficient_coverage(self):
        """scored_matches / variable_fragments < min_coverage -> empty result"""
        req_data = RequirementHighlightingData(
            req_id="R1",
            description="hello world",
            desc_words=["hello", "world"],
            desc_words_positions={"hello": [(0, 5)], "world": [(6, 11)]},
            desc_words_starting_pos=[0, 6],
        )
        result = _highlight_desc_variable(req_data, [("UNMATCHED_XYZ_VAR", {"xyz", "abc", "def", "ghi", "jkl"})])
        self.assertEqual(result, [])

    def test_skips_insufficient_coverage_with_min_coverage(self):
        """explicit min_coverage threshold respected"""
        req_data = RequirementHighlightingData(
            req_id="R1",
            description="hello world foo bar",
            desc_words=["hello", "world", "foo", "bar"],
            desc_words_positions={
                "hello": [(0, 5)],
                "world": [(6, 11)],
                "foo": [(12, 15)],
                "bar": [(16, 19)],
            },
            desc_words_starting_pos=[0, 6, 12, 16],
        )
        result = _highlight_desc_variable(
            req_data,
            [("NOMATCH_VAR", {"zzz", "qqq", "xxx", "aaa", "bbb", "ccc"})],
            min_coverage=0.55,
        )
        self.assertEqual(result, [])


class TestGenerateMdDescription(TestCase):
    def test_same_score_longer_span_wins(self):
        """equal score but longer span -> longer match replaces shorter"""
        matches = [
            VariableMatch(0, 4, "hell", "VAR_A", 80.0),
            VariableMatch(0, 9, "hello wor", "VAR_B", 80.0),
        ]
        result = _generate_md_description(matches, "hello world")
        self.assertIn("VAR_B", result)
        self.assertNotIn("VAR_A", result)


class TestGenerateAllHighlightedDesc(TestCase):
    def test_empty_variable_string_skipped(self):
        req = Requirement(rid="R1", description="fo ba", type_in_csv="Feature", csv_row={}, pos_in_csv=0)
        generate_all_highlighted_desc(["fo", "ba"], {"R1": req})
        self.assertIn("R1", requirement_highlighting_data_per_req)

    def test_is_stopped_breaks_loop(self):
        """cancelling the task stops processing before all reqs are handled"""
        reqs = {
            f"R{i}": Requirement(
                rid=f"R{i}",
                description="some description with variableName and anotherVar",
                type_in_csv="Feature",
                csv_row={},
                pos_in_csv=0,
            )
            for i in range(500)
        }
        handler = ThreadHandler(SendUpdateThreadingAndAi(), max_threads=5)
        result = handler.submit(
            ThreadTask(
                generate_all_highlighted_desc,
                SchedulingClass.SYSTEM_CALL,
                ThreadGroup("VARIABLE_HIGHLIGHTING"),
                None,
                None,
                (["variableName", "anotherVar"], reqs),
                {},
            )
        )
        time.sleep(0.05)
        self.assertTrue(not handler.is_idle())
        handler.cancel_task(result.task_id())
        time.sleep(0.2)
        self.assertTrue(handler.is_idle())


class TestRequirementHighlightingEndToEnd(TestCase):
    def test_requirement_highlighting(self):
        req = Requirement(
            rid="REQ1",
            description="This is a testDescription with MyVariable and AnotherVar.",
            type_in_csv="Feature",
            csv_row={},
            pos_in_csv=0,
        )

        variables = {"MyVariable", "AnotherVar", "TestDescription"}

        generate_all_highlighted_desc(list(variables), {"REQ1": req})
        self.assertIn("REQ1", requirement_highlighting_data_per_req)
        req_data: RequirementHighlightingData = requirement_highlighting_data_per_req["REQ1"]

        self.assertTrue(req_data.variable_matches)
        self.assertTrue(req_data.highlighted_desc)
        matched_vars = {m.variable for m in req_data.variable_matches}
        self.assertTrue(variables.intersection(matched_vars))

        for m in req_data.variable_matches:
            self.assertLessEqual(m.start, m.end)
            self.assertGreaterEqual(m.end, 0)
        positions = {m.variable: (m.start, m.end) for m in req_data.variable_matches}
        self.assertEqual(positions["TestDescription"], (10, 25))
        self.assertEqual(positions["MyVariable"], (33, 41))
        self.assertEqual(positions["AnotherVar"], (46, 56))

        html = req_data.highlighted_desc
        for var in variables:
            self.assertIn(f'data-main-var="{var}"', html)

        for m in req_data.variable_matches:
            self.assertGreater(m.score, 99.9)

        words = req_data.desc_words
        self.assertNotIn("my", words)
        self.assertIn("variable", words)
        self.assertIn("test", words)
        self.assertIn("description", words)


class TestDeleteVariables(TestCase):
    def setUp(self):
        requirement_highlighting_data_per_req.clear()

    def test_delete_variable_removes_match(self):
        req_data = RequirementHighlightingData(req_id="R1", description="test description variable")
        req_data.variable_matches = [VariableMatch(0, 4, "test", "VAR_A", 90)]
        requirement_highlighting_data_per_req["R1"] = req_data
        delete_variables(["VAR_A"])
        self.assertEqual(len(requirement_highlighting_data_per_req["R1"].variable_matches), 0)

    def test_delete_variable_keeps_other_matches(self):
        req_data = RequirementHighlightingData(req_id="R1", description="test description variable")
        req_data.variable_matches = [
            VariableMatch(0, 4, "test", "VAR_A", 90),
            VariableMatch(5, 10, "descr", "VAR_B", 85),
        ]
        requirement_highlighting_data_per_req["R1"] = req_data
        delete_variables(["VAR_A"])
        matches = requirement_highlighting_data_per_req["R1"].variable_matches
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].variable, "VAR_B")
