from collections import defaultdict
from unittest import TestCase

from lib_core.data import *
from lib_core.pattern.patterns_automata import AAutomatonPattern


class TestSimpleAutomaton(TestCase):

    def __get_aut_easy(self):
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
        i, f3a = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "InitialLoc",
            mapping={"R": "states == states.A"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f3b = r.add_empty_formalization()
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
            mapping={"R": "states_other == states.B", "S": "states_other == states.A"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        return variable_collection, r, f1, f2, f3a, f3b, f5

    def test_simple_transitions(self):
        variable_collection, r, f1, f2, f3a, f3b, f5 = self.__get_aut_easy()
        # test general automaton layout
        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        aut = {f1, f2, f3a, f3b}
        self.assertSetEqual(aut, set(req_belonging_to_r))

    def test_initial_edge(self):
        variable_collection, r, f1, f2, f3a, f3b, f5 = self.__get_aut_easy()
        # test general automaton layout
        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        aut = {f1, f2, f3a, f3b}
        # test formula generation
        formal_f3a = f3a.scoped_pattern.pattern.get_patternish().get_instanciated_countertraces(
            f3a.scoped_pattern.scope, f3a, aut, variable_collection
        )
        self.assertIsNotNone(formal_f3a)
        # States A and B (1 and 2) are initial.
        self.assertIn(r"(states = 1)", repr(formal_f3a[0].dc_phases[0].invariant))
        self.assertIn(r"(states = 2)", repr(formal_f3a[0].dc_phases[0].invariant))

    def test_edge_simple(self):
        variable_collection, r, f1, f2, f3a, f3b, f5 = self.__get_aut_easy()
        # test general automaton layout
        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        aut = {f1, f2, f3a, f3b}

        formal_f1 = f1.scoped_pattern.pattern.get_patternish().get_instanciated_countertraces(
            f1.scoped_pattern.scope, f1, aut, variable_collection
        )
        self.assertIsNotNone(formal_f1)
        self.assertIn(r"(states = 1)", repr(formal_f1[0].dc_phases[1].invariant))
        self.assertNotIn(r"(states = 2)", repr(formal_f1[0].dc_phases[1].invariant))
        self.assertIn(r"(states = 1)", repr(formal_f1[0].dc_phases[2].invariant))
        self.assertIn(r"(states = 2)", repr(formal_f1[0].dc_phases[2].invariant))
