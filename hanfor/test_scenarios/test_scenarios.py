"""Logic for test scenarios: create, change, import. The routes are in test_scenarios_api.py."""

import logging

from lark import LarkError

from json_db_connector.json_db import JsonDatabase
from lib_core import boogie_parsing
from lib_core.boogie_parsing import BoogieType, run_typecheck_fixpoint
from lib_core.data import Requirement, Variable, VariableCollection
from lib_core.test_scenario import GLOBAL_TEST_TARGET, TestScenario, TestScenarioStep, _identifier
from requirements.subtypes import InvalidPayload, SubtypeNotFound


def check_boolean(collection: VariableCollection, lane: str) -> None:
    """A lane has to be a boolean expression, e.g. speed > 5 instead of speed."""
    try:
        tree = boogie_parsing.get_parser_instance().parse(lane)
    except LarkError as e:
        raise InvalidPayload(f"Lane `{lane}` is not a valid expression: {e}") from e
    try:
        result = run_typecheck_fixpoint(tree, collection.get_boogie_type_env(), expected_types=[BoogieType.bool])
    except Exception:
        # a failing type checker must not block saving, only a reported type error does
        logging.exception(f"Could not type check lane `{lane}`")
        return
    if result.type_errors:
        raise InvalidPayload(f"Lane `{lane}` is not boolean: {'; '.join(map(str, result.type_errors))}")


def next_id(db: JsonDatabase) -> int:
    new_id = max(db.get_objects(TestScenario).keys(), default=0) + 1
    while db.key_in_table(TestScenario, new_id):  # ids of deleted scenarios stay taken
        new_id += 1
    return new_id


def apply(db: JsonDatabase, scenario: TestScenario | None, data) -> TestScenario:
    """Validate data and write it into scenario, or into a new one if None.

    Fields of data: requirement_id (only when creating, "" or missing = global), name (empty = automatic),
    description, desired_behavior, lanes, steps.
    """
    if not isinstance(data, dict):
        raise InvalidPayload("Body has to be a JSON object")
    if scenario is None:
        requirement_id = str(data.get("requirement_id") or "")
        if requirement_id and not db.key_in_table(Requirement, requirement_id):
            raise SubtypeNotFound(f"Requirement '{requirement_id}' not found.")
        scenario = TestScenario(next_id(db), "", True, requirement_id=requirement_id)

    try:
        steps = [TestScenarioStep.from_dict(s) for s in data.get("steps") or []]
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise InvalidPayload(f"Invalid step: `{e}`") from e
    lanes = list(dict.fromkeys(str(lane).strip() for lane in data.get("lanes") or []))
    lanes += [lane for lane in TestScenario.lanes_of_steps(steps) if lane not in lanes]
    collection = VariableCollection(db.get_objects(Variable).values(), db.get_objects(Requirement).values())
    for lane in lanes:
        check_boolean(collection, lane)

    # names are unique over all scenarios, Ultimate uses them as identifiers
    desired = bool(data.get("desired_behavior", True))
    others = {s.name for s in db.get_objects(TestScenario).values() if s.id != scenario.id}
    name = TestScenario.clean_name(str(data.get("name") or ""))
    name = name or TestScenario.default_name(scenario.requirement_id, desired, others)
    if name in others:
        raise InvalidPayload(f"A test scenario named `{name}` exists already")

    scenario.name = name
    scenario.description = str(data.get("description") or "")
    scenario.desired_behavior = desired
    scenario.steps = steps
    scenario.lanes = lanes
    return scenario


def import_text(db: JsonDatabase, text: str, replace: bool = False) -> dict:
    """Import every test scenario line of text (e.g. an exported .req file), other lines are ignored.

    TARGET ALL makes a global scenario, otherwise the requirement with that id (or that id as the .req file writes
    it, SysRS FooXY_42 -> SysRS_FooXY_42). A scenario whose name exists already is skipped, or overwritten if
    replace is true. Returns {"imported": [names], "skipped": [names], "errors": ["line n: ..."]}.
    """
    by_identifier: dict[str, list[str]] = {}
    for rid in db.get_objects(Requirement).keys():
        by_identifier.setdefault(_identifier(rid), []).append(rid)
    report = {"imported": [], "skipped": [], "errors": []}
    for line_no, line in enumerate(text.splitlines(), start=1):
        try:
            data = TestScenario.parse_req_line(line)
            if data is None:
                continue
            target = data.pop("target")
            if target == GLOBAL_TEST_TARGET and not db.key_in_table(Requirement, target):
                data["requirement_id"] = ""
            elif db.key_in_table(Requirement, target):
                data["requirement_id"] = target
            elif len(by_identifier.get(target, [])) == 1:
                data["requirement_id"] = by_identifier[target][0]
            else:
                raise InvalidPayload(f"Requirement `{target}` not found or ambiguous")

            existing = next((s for s in db.get_objects(TestScenario).values() if s.name == data["name"]), None)
            if existing is not None and not replace:
                report["skipped"].append(data["name"])
                continue
            if existing is not None:
                existing.requirement_id = data["requirement_id"]
            scenario = apply(db, existing, data)
            if existing is None:
                db.add_object(scenario)
            else:
                db.update()
            report["imported"].append(scenario.name)
        except (InvalidPayload, SubtypeNotFound, ValueError) as e:
            report["errors"].append(f"line {line_no}: {e}")
    return report
