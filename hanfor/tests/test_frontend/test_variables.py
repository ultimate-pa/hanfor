import pytest
from playwright.sync_api import Page, expect

from tests.test_frontend.helpers import (
    VARIABLE_CARD,
    confirm_delete,
    create_formalization,
    create_variable,
    get_formalizations,
    open_requirement,
    save_requirement,
)

RID = "SysRS FooXY_91"


@pytest.mark.parametrize(
    ("name", "var_type", "value", "enumerators", "expected"),
    [
        ("speed", "int", "", [], {"type": "int"}),
        ("limit", "CONST", "10", [], {"type": "CONST", "const_val": "10"}),
        ("mode", "ENUM_INT", "", [("on", "1")], {"type": "ENUM_INT", "enumerators": [{"name": "on", "value": "1"}]}),
    ],
)
def test_create_variable(page: Page, name, var_type, value, enumerators, expected):
    modal = open_requirement(page, RID)
    modal.locator("#add_variable").click()
    card = modal.locator(f"{VARIABLE_CARD}.draft")
    card.locator(".accordion-button").click()
    card.locator('input[aria-describedby="variable-name-feedback"]').fill(name)
    card.locator("input.variable-type").fill(var_type)
    card.locator("input.variable-type").press("Tab")
    if value:
        card.locator("input.variable-value").fill(value)
    for enum_name, enum_value in enumerators:
        card.locator(".add-enumerator-btn").click()
        card.locator(".enum_name_input").last.fill(enum_name)
        card.locator(".enum_value_input").last.fill(enum_value)
    save_requirement(page, modal, RID)

    variables = {v["name"]: v for v in get_formalizations(page, RID, "variable")}
    assert expected.items() <= variables[name].items()


def test_change_variable_type(page: Page):
    create_variable(page, RID, "speed", "int")

    modal = open_requirement(page, RID)
    card = modal.locator(VARIABLE_CARD)
    card.locator(".accordion-button").click()
    card.locator("input.variable-type").fill("CONST")
    card.locator("input.variable-type").press("Tab")
    value_input = card.locator("input.variable-value")
    expect(value_input).to_be_visible()
    value_input.fill("5")
    save_requirement(page, modal, RID)

    [variable] = get_formalizations(page, RID, "variable")
    assert (variable["name"], variable["type"], variable["const_val"]) == ("speed", "CONST", "5")


def test_rename_variable(page: Page):
    create_variable(page, RID, "speed", "int")
    create_formalization(page, RID, "GLOBALLY", "Absence", {"R": "speed > 5"})

    modal = open_requirement(page, RID)
    card = modal.locator(VARIABLE_CARD)
    card.locator(".accordion-button").click()
    card.locator('input[aria-describedby="variable-name-feedback"]').fill("velocity")
    expect(card.locator(".accordion-button")).to_have_text("velocity")
    save_requirement(page, modal, RID)

    [variable] = get_formalizations(page, RID, "variable")
    assert variable["name"] == "velocity"
    [formalization] = get_formalizations(page, RID, "formalization")
    assert formalization["expr_R"].replace(" ", "") == "velocity>5"


def test_cancelled_close_keeps_new_variable(page: Page):
    modal = open_requirement(page, RID)
    modal.locator("#add_variable").click()
    card = modal.locator(f"{VARIABLE_CARD}.draft")
    card.locator(".accordion-button").click()
    card.locator('input[aria-describedby="variable-name-feedback"]').fill("speed")
    card.locator("input.variable-type").fill("int")
    card.locator("input.variable-type").press("Tab")
    page.once("dialog", lambda dialog: dialog.dismiss())
    modal.locator(".modal-footer").get_by_role("button", name="Close").click()
    expect(modal).to_be_visible()
    save_requirement(page, modal, RID)

    assert "speed" in {v["name"] for v in get_formalizations(page, RID, "variable")}


def test_delete_enumerator_of_saved_variable(page: Page):
    modal = open_requirement(page, RID)
    modal.locator("#add_variable").click()
    card = modal.locator(f"{VARIABLE_CARD}.draft")
    card.locator(".accordion-button").click()
    card.locator('input[aria-describedby="variable-name-feedback"]').fill("mode")
    card.locator("input.variable-type").fill("ENUM_INT")
    card.locator("input.variable-type").press("Tab")
    for enum_name, enum_value in [("on", "1"), ("off", "2")]:
        card.locator(".add-enumerator-btn").click()
        card.locator(".enum_name_input").last.fill(enum_name)
        card.locator(".enum_value_input").last.fill(enum_value)
    save_requirement(page, modal, RID)

    # Reopen so the delete goes through the update path of a saved variable, not the create path.
    modal = open_requirement(page, RID)
    card = modal.locator(VARIABLE_CARD)
    card.locator(".accordion-button").click()
    card.locator(".enumerator-input").filter(has=page.locator('.enum_name_input[value="off"]')).locator(".del_enum").click()
    save_requirement(page, modal, RID)

    [variable] = get_formalizations(page, RID, "variable")
    assert variable["enumerators"] == [{"name": "on", "value": "1"}]


def test_delete_variable_card(page: Page):
    create_variable(page, RID, "speed", "int")

    modal = open_requirement(page, RID)
    card = modal.locator(VARIABLE_CARD)
    card.locator(".accordion-button").click()
    confirm_delete(card.locator(".delete_variable"))
    expect(card).to_have_count(0)
    save_requirement(page, modal, RID)

    assert get_formalizations(page, RID, "variable") == []
