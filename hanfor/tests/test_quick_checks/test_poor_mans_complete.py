from unittest import TestCase

from lib_core.data import Variable, Requirement, ScopedPattern, Pattern, Formalization
from lib_core.scopes import Scope
from quickchecks.check_poormanscomplete import PoorMansComplete, CompletenessCheckOutcome


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
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE_UNCONSTRAINT}
        self.assertIn("b", b_result)
        self.assertIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE_UNCONSTRAINT}
        self.assertIn("d", b_result)
        self.assertNotIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        self.assertNotIn("d", b_result)
        self.assertIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        self.assertNotIn("d", b_result)
        self.assertIn("c", b_result)
        self.assertNotIn("a", b_result)
        self.assertIn("x", b_result)

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
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE_UNCONSTRAINT}
        self.assertNotIn("d", b_result)
        self.assertIn("c", b_result)
        self.assertNotIn("a", b_result)

    def test_incomplete_with_env_neg(self):
        vars = {
            "c": Variable("c", "int", None),
        }
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 0 && c < 100")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "c == 3", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req1", "c == 4", "c > 22", "5.0"),
            # TestPoorMansComplete.__instantiate_bound_response("req2", "c < 1000", "c > -33", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE}
        self.assertIn("c", b_result)

    def test_incomplete_with_env_univ(self):
        vars = {
            "c": Variable("c", "int", None),
        }
        vars["c"].constraints[0] = TestPoorMansComplete.__formalisation_universality("c > 0 && c < 100")
        reqs = [
            TestPoorMansComplete.__instantiate_bound_response("req1", "c != -4", "c > 22", "5.0"),
            TestPoorMansComplete.__instantiate_bound_response("req1", "c != -5", "c > 22", "5.0"),
            # TestPoorMansComplete.__instantiate_bound_response("req2", "c < 1000", "c > -33", "5.0"),
        ]
        results = PoorMansComplete().run(reqs, set(vars.values()))
        b_result = {r.var: r for r in results if r.outcome == CompletenessCheckOutcome.INCOMPLETE}
        self.assertNotIn("c", b_result)

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
        self.assertNotIn("d", b_result)
        self.assertNotIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        self.assertNotIn("d", b_result)
        self.assertIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        self.assertIn("d", b_result)
        self.assertNotIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        self.assertIn("d", b_result)
        self.assertIn("c", b_result)
        self.assertNotIn("a", b_result)

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
        self.assertNotIn("d", b_result)
        self.assertNotIn("c", b_result)
        self.assertNotIn("a", b_result)
