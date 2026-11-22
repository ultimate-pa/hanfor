"""Test scenarios: example traces that have to hold or are forbidden to hold.

A scenario either belongs to one requirement (requirement_id) or is global (checked against all requirements).
In the .req file: NAME: TestScenario for <RID | ALL>, trace has to hold: (duration, formula), ...
"""

import re
from typing import Any, Dict

from json_db_connector.json_db import DatabaseField, DatabaseFieldType, DatabaseID, DatabaseTable, TableType
from lib_core import boogie_parsing

# Target of a global test scenario in the .req file
GLOBAL_TEST_TARGET = "ALL"

_SIMPLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
_REQ_LINE = re.compile(
    r"^\s*(?P<name>\w+)\s*:\s*TestScenario for (?P<target>[^,]+),\s*"
    r"trace (?P<mode>has to hold|is forbidden to hold)\s*:\s*(?P<steps>.*)$"
)


def _identifier(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", text)


def _split_top_level(text: str, sep: str) -> list[str]:
    """Split on sep, but only outside of parentheses."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        depth += (ch == "(") - (ch == ")")
        if depth == 0 and text.startswith(sep, i) and i >= start:
            parts.append(text[start:i])
            start = i + len(sep)
    return parts + [text[start:]]


def _strip_outer_parens(text: str) -> str:
    """(a || b) -> a || b, but (a) || (b) stays as it is."""
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        for i, ch in enumerate(text[:-1]):
            depth += (ch == "(") - (ch == ")")
            if depth == 0:
                return text
        text = text[1:-1].strip()
    return text


@DatabaseFieldType()
@DatabaseField("duration", float)
@DatabaseField("states", dict)
class TestScenarioStep:
    """One interval. states maps a lane to high (True) or low (False), a missing lane is "don't care"."""

    __test__ = False  # keeps pytest from collecting the class

    def __init__(self, duration: float, states: dict[str, bool] | None = None):
        self.duration = duration
        self.states: dict[str, bool] = states or {}

    @property
    def formula(self) -> str:
        """a && !(x > 5), or true if every lane is "don't care"."""
        parts = []
        for lane, value in self.states.items():
            bare = _SIMPLE_NAME.match(lane) or (value and len(self.states) == 1)
            expr = lane if bare else f"({lane})"
            parts.append(expr if value else f"!{expr}")
        return " && ".join(parts) or "true"

    @staticmethod
    def from_dict(d: dict) -> "TestScenarioStep":
        duration = float(d["duration"])
        if duration <= 0:
            raise ValueError(f"Duration must be positive: {duration}")
        states = {}
        for lane, value in d.get("states", {}).items():
            if value is None:
                continue
            if not isinstance(value, bool):
                raise ValueError(f"State of `{lane}` must be true or false, got {value!r}")
            states[str(lane).strip()] = value
        return TestScenarioStep(duration, states)

    @staticmethod
    def from_formula(formula: str) -> dict[str, bool]:
        """The states of a formula as to_req_line writes it: a && !b && (c > 1) -> {a: True, b: False, c > 1: True}."""
        states: dict[str, bool] = {}
        if formula.strip().lower() == "true":
            return states
        for term in _split_top_level(formula, "&&"):
            term, value = _strip_outer_parens(term), True
            if term.startswith("!") and not term.startswith("!="):
                term, value = _strip_outer_parens(term[1:]), False
            if not term:
                raise ValueError(f"Empty term in `{formula}`")
            if states.setdefault(term, value) != value:
                raise ValueError(f"`{term}` has to be true and false at once")
        return states


@DatabaseTable(TableType.File)
@DatabaseID("id", int)
@DatabaseField("name", str)
@DatabaseField("description", str, "")
@DatabaseField("requirement_id", str, "")
@DatabaseField("desired_behavior", bool)
@DatabaseField("steps", list[TestScenarioStep])
@DatabaseField("lanes", list[str])
@DatabaseField("ultimate_result", dict, {})
class TestScenario:
    """A trace that has to hold (desired_behavior True, POS) or is forbidden to hold (False, NEG).

    requirement_id is the requirement it tests, or "" for a global scenario. Steps are consecutive: a step starts
    where the previous one ends. Lanes are boolean expressions, e.g. var1 or speed > 5.
    ultimate_result is the outcome of the latest Ultimate job that checked the scenario, {} if there is none.
    """

    __test__ = False  # keeps pytest from collecting the class

    def __init__(
        self,
        sid: int,
        name: str,
        desired_behavior: bool,
        steps: list[TestScenarioStep] | None = None,
        lanes: list[str] | None = None,
        requirement_id: str = "",
        description: str = "",
    ):
        self.id = sid
        self.name = name
        self.description = description
        self.requirement_id = requirement_id
        self.desired_behavior = desired_behavior
        self.steps: list[TestScenarioStep] = steps or []
        self.lanes: list[str] = lanes if lanes is not None else self.lanes_of_steps(self.steps)
        self.ultimate_result: dict = {}

    @property
    def is_global(self) -> bool:
        return not self.requirement_id

    @staticmethod
    def lanes_of_steps(steps: list[TestScenarioStep]) -> list[str]:
        """All lanes the steps use, in order of first appearance."""
        lanes: list[str] = []
        for step in steps:
            lanes += [lane for lane in step.states if lane not in lanes]
        return lanes

    @staticmethod
    def default_name(requirement_id: str, positive: bool, taken: set[str]) -> str:
        """TS_<rid>_<POS|NEG>_<n> (TS_GLOBAL_... without requirement) with the smallest free n."""
        owner = _identifier(requirement_id) if requirement_id else "GLOBAL"
        prefix = f"TS_{owner}_{'POS' if positive else 'NEG'}_"
        n = 1
        while f"{prefix}{n}" in taken:
            n += 1
        return f"{prefix}{n}"

    @staticmethod
    def clean_name(name: str) -> str:
        """Ultimate reads the name as an identifier."""
        return _identifier(name.strip()).strip("_")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requirement_id": self.requirement_id,
            "desired_behavior": self.desired_behavior,
            "lanes": self.lanes,
            "steps": [{"duration": s.duration, "states": s.states} for s in self.steps],
            "ultimate_result": self.ultimate_result or {},
        }

    def used_lane_tokens(self) -> set[str]:
        """Every name that appears in a lane, a superset of the variables the scenario uses."""
        return {token for lane in self.lanes for token in re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", lane)}

    def rename_used_variable(self, old_name: str, new_name: str) -> None:
        def rename(lane: str) -> str:
            if old_name not in lane:
                return lane
            return boogie_parsing.replace_var_in_expression(expression=lane, old_var=old_name, new_var=new_name)

        renamed = {lane: rename(lane) for lane in self.lanes}
        self.lanes = list(dict.fromkeys(renamed.values()))
        for step in self.steps:
            step.states = {renamed.get(lane, lane): value for lane, value in step.states.items()}

    @staticmethod
    def parse_req_line(line: str) -> dict | None:
        """A line NAME: TestScenario for TARGET, trace has to hold: (duration, formula), ... as dict
        {name, target, desired_behavior, steps} (steps as the API takes them), None for any other line."""
        m = _REQ_LINE.match(line)
        if not m:
            return None
        steps = []
        for group in _split_top_level(m["steps"].strip(), ","):
            group = _strip_outer_parens(group)
            duration, _, formula = group.partition(",")
            if not formula:
                raise ValueError(f"Interval `({group})` is not `(duration, formula)`")
            steps.append({"duration": float(duration), "states": TestScenarioStep.from_formula(formula)})
        return {
            "name": m["name"],
            "target": m["target"].strip(),
            "desired_behavior": m["mode"] == "has to hold",
            "steps": steps,
        }

    def to_req_line(self) -> str:
        """TS_ELS_3_POS_4: TestScenario for ELS_3, trace has to hold: (0.4, formula), (1.0, formula),
        ... TestScenario for ALL, ... for a global scenario."""
        target = GLOBAL_TEST_TARGET if self.is_global else _identifier(self.requirement_id)
        mode = "has to hold" if self.desired_behavior else "is forbidden to hold"
        steps = ", ".join(f"({float(s.duration)}, {s.formula})" for s in self.steps)
        return f"{self.name}: TestScenario for {target}, trace {mode}: {steps}"
