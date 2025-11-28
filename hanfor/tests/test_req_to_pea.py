from collections import defaultdict
from unittest import TestCase

from lib_core.data import Requirement, VariableCollection, Tag
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
        sem = get_semantics_from_requirement(r, [r], variable_collection)
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[0].__str__())
        self.assertEqual("⌈((anIntegerVar = 42) & (! aBooleanVar))⌉", list(sem.items())[0][1].dc_phases[1].__str__())
        self.assertEqual("True", list(sem.items())[0][1].dc_phases[2].__str__())
