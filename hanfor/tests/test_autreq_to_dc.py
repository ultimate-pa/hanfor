from collections import defaultdict
from unittest import TestCase

from configuration.patterns import AAutomatonPattern
from lib_core.data import Requirement, VariableCollection, Tag, Variable


class TestAutomatonAssembly(TestCase):

    def test_simple_transitions(self):
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
        # This one is slightly diffent, but should also not be part of the automaton
        #  (the locations are a little bit stricter so this might be a nested-automaton)
        i, f5 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "states == states.B && piffel", "S": "states == states.A && !piffel"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )

        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        self.assertSetEqual({f1, f2, f3, f4}, set(req_belonging_to_r))

    def test_complex_pattern_transitions(self):
        """
        This Test describes a donut A -> B -> C -> A   , with two sinks B -> C & det   and B -> C & !det
        to test if all successors are found correctly
        """
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
                Variable("states.C", "ENUMERATOR_INT", "3"),
                Variable("other_states", "ENUM_INT"),
                Variable("other_states.A", "ENUMERATOR_INT", "1"),
                Variable("other_states.B", "ENUMERATOR_INT", "2"),
            ],
            [r],
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
        i, f1 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "TransitionLGE",
            # Semantically equivalent, syntactically different S
            mapping={
                "R": "states == states.A",
                "S": "states == states.B",
                "T": "42.0",
                "U": "anEventVar",
                "V": "aGuardingVar < 44.0",
            },
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f2 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "TransitionUE",
            mapping={
                "R": "states == states.B",
                "S": "states == states.C",
                "T": "42.0",
                "U": "anOtherEventVar",
            },
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        # This one is something completely different while the above build one automaton
        i, f5a = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "states == states.B", "S": "states == states.C && determinisation"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        # the follwoing two are reachable sinks, to test traversal works right
        i, f5b = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "states == states.B", "S": "states == states.C && !determinisation"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f6 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "states == states.C", "S": "states == states.A"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        # This one is slightly diffent, but should also not be part of the automaton
        #  (the locations are a little bit stricter so this might be a nested-automaton)
        i, f7 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "TransitionLGE",
            mapping={
                "R": "states == states.B && piffel",
                "S": "states == states.C && !piffel",
                "T": "42.0",
                "U": "anEventVar",
                "V": "aGuardingVar < 44.0",
            },
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )

        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        self.assertSetEqual({f1, f2, f3, f5a, f5b, f6}, set(req_belonging_to_r))
