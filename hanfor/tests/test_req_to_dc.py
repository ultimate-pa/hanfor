from collections import defaultdict
from unittest import TestCase

from lib_core.data import Requirement, VariableCollection, Tag, Variable
from lib_pea.req_to_pea import get_semantics_from_requirement


class TestAbsFunction(TestCase):

    def test_invariant(self):
        r = Requirement("req1", "the Requirement is always A", "requirement", {"a": "blabla", "b": "blablubb"}, 244)
        i, f = r.add_empty_formalization()
        variable_collection = VariableCollection([], [r])
        r.update_formalization(
            i,
            "GLOBALLY",
            "Invariant",
            mapping={"R": "anIntegerVar == 42", "S": "aBooleanVar"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        self.assertIn("aBooleanVar", [var.name for var in variable_collection.new_vars])
        self.assertIn("anIntegerVar", [var.name for var in variable_collection.new_vars])
        sem = get_semantics_from_requirement(r, [r], variable_collection)
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[0].__str__())
        self.assertEqual("⌈((anIntegerVar = 42) & (! aBooleanVar))⌉", list(sem.items())[0][1].dc_phases[1].__str__())
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[2].__str__())

    def test_ResponseDelayBoundL2(self):
        "Just to test a more complex pattern with more placeholders and several formulas"
        r = Requirement(
            "req1",
            "This is a most complicated text for an unbelievably complex requirement",
            "requirement",
            {"a": "blabla", "b": "blablubb"},
            2,
        )
        i, f = r.add_empty_formalization()
        variable_collection = VariableCollection([Variable("MAX_TIME", "CONST", "42.24")], [r])
        r.update_formalization(
            i,
            "AFTER_UNTIL",
            "ResponseDelayBoundL2",
            mapping={
                "R": "anIntegerVar == 42",
                "S": "anotherIntVar >= 42",
                "T": "47.74",
                "U": "MAX_TIME",
                "P": "before",
                "Q": "after",
            },
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        self.assertIn("anotherIntVar", [var.name for var in variable_collection.new_vars])
        self.assertIn("anIntegerVar", [var.name for var in variable_collection.new_vars])
        self.assertIn("before", [var.name for var in variable_collection.new_vars])
        self.assertIn("after", [var.name for var in variable_collection.new_vars])
        sem = get_semantics_from_requirement(r, [r], variable_collection)
        # "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[0].__str__())
        self.assertEqual("⌈before⌉", list(sem.items())[0][1].dc_phases[1].__str__())
        self.assertAlmostEqual(47.74, float(list(sem.items())[0][1].dc_phases[4].bound.constant_value()))
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[5].__str__())
        # "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true"
        self.assertAlmostEqual(42.24, float(list(sem.items())[1][1].dc_phases[5].bound.constant_value()))
        self.assertEqual(
            "⌈((! after) & (42 <= anotherIntVar))⌉ ∧ ℓ < 5944751508129055/140737488355328",
            list(sem.items())[1][1].dc_phases[5].__str__(),
        )
