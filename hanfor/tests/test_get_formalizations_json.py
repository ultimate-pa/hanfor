import json
from collections import defaultdict
from unittest import TestCase

from lib_core.data import Requirement, Tag, Variable, VariableCollection


def formalized_requirement() -> tuple[Requirement, int]:
    req = Requirement("req1", "the Requirement is always A", "requirement", {"a": "blabla"}, 0)
    fid, _ = req.add_empty_formalization()
    req.update_formalization(
        fid,
        "GLOBALLY",
        "Invariant",
        mapping={"R": "anIntegerVar == 42", "S": "aBooleanVar"},
        variable_collection=VariableCollection([], [req]),
        standard_tags=defaultdict(lambda: Tag("test", "color", False, "")),
    )
    return req, fid


class TestGetFormalizationsJson(TestCase):
    def test_formalizations_are_exported(self):
        req, fid = formalized_requirement()

        result = json.loads(req.get_formalizations_json())

        self.assertEqual([str(fid)], list(result.keys()))

    def test_variables_are_skipped(self):
        """A `Variable` has no `scoped_pattern`; before the fix this raised `AttributeError`."""
        req, fid = formalized_requirement()
        req.add_formalization_with_id(Variable("aBooleanVar", "bool"), fid + 1)

        result = json.loads(req.get_formalizations_json())

        self.assertEqual([str(fid)], list(result.keys()))
