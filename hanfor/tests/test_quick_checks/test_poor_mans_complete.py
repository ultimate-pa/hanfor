from unittest import TestCase

from quickchecks.check_poormanscomplete import PoorMansComplete, CompletenessCheckOutcome
from reqtransformer import Variable, Requirement, ScopedPattern, Scope, Pattern, Formalization


class Mock_Expression:
    """Mock Expression without parsing and typechecking"""

    def __init__(self, raw_expression: str):
        self.raw_expression = raw_expression


class TestPoorMansComplete(TestCase):

    @staticmethod
    def __instantiate_bound_response(name: str, expr1: str, expr2: str, bound: str) -> Requirement:
        req = Requirement("test_1", "I am a requirement.", "req", dict(), 3)
        f = Formalization(0)
        f.scoped_pattern = ScopedPattern(Scope.GLOBALLY, Pattern(name="BoundedResponse"))
        f.expressions_mapping = {"R": Mock_Expression(expr1), "S": Mock_Expression(expr2), "T": Mock_Expression(bound)}
        req.formalizations[0] = f
        return req

    def __instantiate_universality(name: str, expr1: str) -> Requirement:
        req = Requirement("test_1", "I am a requirement.", "req", dict(), 3)
        req.formalizations[0] = TestPoorMansComplete.__formalisation_universality(expr1)
        return req

    def __formalisation_universality(expr1: str) -> Formalization:
        f = Formalization(0)
        f.scoped_pattern = ScopedPattern(Scope.GLOBALLY, Pattern(name="Universality"))
        f.expressions_mapping = {"R": Mock_Expression(expr1)}
        return f

    def test_incomplete_without_env(self):
        vars = {
            "a": Variable("a", "bool", None),
            "b": Variable("b", "int", None),
            "c": Variable("c", "int", None),
        }
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && b < 5", "b > 6", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && b < 5", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_INCOMPLETE_UNCONSTRAINT}
        self.assertIn(vars["b"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_incomplete_with_env_bool(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 7")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_INCOMPLETE_UNCONSTRAINT}
        self.assertIn(vars["d"], b_result)
        self.assertNotIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_incomplete_with_env(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 7")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c >= 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 10", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE}
        self.assertNotIn(vars["d"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_incomplete_with_env_cmplx(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
            "x": Variable("x", "int", None),
        }
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 7")
        vars["c"].constraints[1] = TestPoorMansComplete.__formalisation_universality("c > 9")
        vars["c"].constraints[2] = TestPoorMansComplete.__formalisation_universality("x < 42")
        vars["c"].constraints[3] = TestPoorMansComplete.__formalisation_universality("x < 5 && d && c > 10")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c >= 22 && x == 0 ", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 11", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE}
        self.assertNotIn(vars["d"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)
        self.assertIn(vars["x"], b_result)

    def test_incomplete_with_env_int(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["d"].constraints[0] = TestPoorMansComplete.__formalisation_universality("d")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_INCOMPLETE_UNCONSTRAINT}
        self.assertNotIn(vars["d"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_incomplete_with_env_ok(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["d"].constraints[0] = TestPoorMansComplete.__formalisation_universality("d")
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 7")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE}
        self.assertNotIn(vars["d"], b_result)
        self.assertNotIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_env_violation_int(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c < 0")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_VIOLATED}
        self.assertNotIn(vars["d"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_env_violation_bool(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["d"].constraints[0] = TestPoorMansComplete.__formalisation_universality("!d")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_VIOLATED}
        self.assertIn(vars["d"], b_result)
        self.assertNotIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_env_violation_all(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["d"].constraints[0] = TestPoorMansComplete.__formalisation_universality("!d")
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c < 0")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_VIOLATED}
        self.assertIn(vars["d"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)

    def test_env_violation_none(self):
        vars = {
            "a": Variable("a", "bool", None),
            "d": Variable("d", "bool", None),
            "c": Variable("c", "int", None),
        }
        vars["d"].constraints[0] = TestPoorMansComplete.__formalisation_universality("d")
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 0")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "a && d", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req2", "!a && d", "c > 7", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.ENV_VIOLATED}
        self.assertIn(vars["d"], b_result)
        self.assertIn(vars["c"], b_result)
        self.assertNotIn(vars["a"], b_result)
