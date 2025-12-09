from collections import defaultdict
from unittest import TestCase

from configuration.patterns import AAutomatonPattern
from lib_core.data import Requirement, VariableCollection, Tag, Variable


class TestSimpleAutomaton(TestCase):

    def test_invariant(self):
        r = Requirement(
            "req1",
            "System has two opstates 'A' (initial) and 'B'. ",
            "requirement",
            {"a": "blabla", "b": "blablubb"},
            1,
        )
        variable_collection = VariableCollection(
            [
                Variable("states", "ENUM_INT"),
                Variable("states.A", "ENUMERATOR_INT", "1"),
                Variable("states.B", "ENUMERATOR_INT", "2"),
                Variable("other_states", "ENUM_INT"),
                Variable("other_states.A", "ENUMERATOR_INT", "1"),
                Variable("other_states.B", "ENUMERATOR_INT", "2"),
            ],
            [r],
        )
        i, f1 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            # Semantically equivalent, syntactically different S
            mapping={"R": "states == states.A", "S": "states == 2"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f2 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "states == states.B", "S": "states == states.A"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f3 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "InitialLoc",
            mapping={"R": "states == states.A"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f4 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "InitialLoc",
            mapping={"R": "states == states.B"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        # This one is something completely different while the above build one automaton
        i, f5 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "other_states == other_states.B", "S": "other_states == other_states.A"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )

        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        self.assertSetEqual({f1, f2, f3, f4}, set(req_belonging_to_r))

        """
        self.assertIn("aBooleanVar", [var.name for var in variable_collection.new_vars])
        self.assertIn("anIntegerVar", [var.name for var in variable_collection.new_vars])
        sem = get_semantics_from_requirement(r, [r], variable_collection)
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[0].__str__())
        self.assertEqual("⌈((anIntegerVar = 42) & (! aBooleanVar))⌉", list(sem.items())[0][1].dc_phases[1].__str__())
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[2].__str__())
        """
