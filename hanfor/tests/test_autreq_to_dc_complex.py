from collections import defaultdict
from unittest import TestCase

from lib_core.data import *
from lib_core.pattern.patterns_automata import AAutomatonPattern


class TestComplexAutomaton(TestCase):

    def __get_complex_automaton(self):
        """
        Automaton 1 : {f1, f2, f3, f6}
                                       ?anEventVar
                                       aGuardingVar < 44.0
                                       <= 42.0
            +--------------------+                        +----------------------+
            |                    |                        |                      |
            |       A (1)        +------------------------>        B (2)         |
            |                    |                        |                      |
            |                    |                        |                      |
            +--------------------+                        +--------------+-------+
                   ^                                        ^            |
                   |                                        |            |
                   |  aGuardingVar > 22.0                   |            |   <= 42.0
                   |                                        |            |   anOtherEventVar
                   |                                        |            |
                   |                                        |            |
                   |                   aGuardingVar < 5.0   |            |
                   |                                        |            |
                   |                                        |            |
                   |                                        |            |
                   |           +------------------------------+          |
                   |           |                              |<---------+
                   +-----------+           C  (3)             |
                               |                              |
                               |                              |
                               +------------------------------+
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
            mapping={"R": "states == states.B && piffel", "S": "states == states.C && determinisation"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        # the follwoing two are reachable sinks, to test traversal works right
        i, f5b = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "Transition",
            mapping={"R": "states == states.C && determinisation", "S": "states == states.C && !determinisation"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f6a = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "TransitionG",
            mapping={"R": "states == states.C", "S": "states == states.A", "V": "aGuardingVar > 22.0"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f6b = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "TransitionG",
            mapping={"R": "states == states.C", "S": "states == states.B", "V": "aGuardingVar < 5.0"},
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
                "R": "states == states.C && !determinisation",
                "S": "states == states.C && !piffel",
                "T": "42.0",
                "U": "anEventVar",
                "V": "aGuardingVar < 44.0",
            },
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        i, f8 = r.add_empty_formalization()
        r.update_formalization(
            i,
            "GLOBALLY",
            "InitialLoc",
            mapping={"R": "states == states.B && piffel"},
            variable_collection=variable_collection,
            standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
        )
        return variable_collection, r, f1, f2, f3, f5a, f5b, f6a, f6b, f7, f8

    def test_assembly(self):
        variable_collection, r, f1, f2, f3, f5a, f5b, f6a, f6b, f7, f8 = self.__get_complex_automaton()
        # First automaton
        req_belonging_to_r = AAutomatonPattern.get_hull(f1, [f for f in r.formalizations.values()], variable_collection)
        self.assertSetEqual({f1, f2, f3, f6a, f6b}, set(req_belonging_to_r))
        # Second Automaton
        req_belonging_to_r = AAutomatonPattern.get_hull(
            f5a, [f for f in r.formalizations.values()], variable_collection
        )
        self.assertSetEqual({f5a, f5b, f7, f8}, set(req_belonging_to_r))

    def test_edge_G(self):
        variable_collection, r, f1, f2, f3, f5a, f5b, f6a, f6b, f7, f8 = self.__get_complex_automaton()
        # test general automaton layout
        aut = {f1, f2, f3, f6a, f6b}

        formal_f6a = f6a.scoped_pattern.pattern.get_patternish().get_instanciated_countertraces(
            f6a.scoped_pattern.scope, f6a, aut, variable_collection
        )
        self.assertIsNotNone(formal_f6a)
        self.assertIn(r"(states = 3)", repr(formal_f6a[0].dc_phases[1].invariant))
        self.assertIn(r"(states = 1)", repr(formal_f6a[0].dc_phases[2].invariant))
        self.assertIn(r"(22.0 < aGuardingVar)", repr(formal_f6a[0].dc_phases[2].invariant))
        self.assertIn(r"(states = 3)", repr(formal_f6a[0].dc_phases[2].invariant))
        self.assertIn(r"(aGuardingVar < 5.0)", repr(formal_f6a[0].dc_phases[2].invariant))

    def test_edge_GE(self):
        pass

    def test_edge_GEL(self):
        pass
