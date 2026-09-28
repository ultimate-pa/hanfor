from playwright.sync_api import Page, expect

from tests.test_frontend.helpers import (
    VARIABLE_CARD,
    create_formalization,
    get_formalizations,
    open_requirement,
    save_requirement,
)


def test_reorder_formalizations(page: Page):
    rid = "SysRS FooXY_42"
    create_formalization(page, rid, "GLOBALLY", "Absence", {"R": "foo == bar"})

    modal = open_requirement(page, rid)
    items = modal.locator("#formalization_accordion > .accordion-item")
    expect(items).to_have_count(2)
    expect(items.nth(0)).to_have_attribute("data-id", "0")
    items.nth(1).locator(".accordion-header").drag_to(
        items.nth(0).locator(".accordion-header"), target_position={"x": 10, "y": 2}
    )
    expect(items.nth(0)).to_have_attribute("data-id", "1")
    save_requirement(page, modal, rid)

    order = {f["id"]: f["order"] for f in get_formalizations(page, rid, "formalization")}
    assert order[1] < order[0]

    modal = open_requirement(page, rid)
    expect(modal.locator("#formalization_accordion > .accordion-item").nth(0)).to_have_attribute("data-id", "1")


def test_reorder_new_variable_and_new_formalization(page: Page):
    rid = "SysRS FooXY_91"
    modal = open_requirement(page, rid)
    modal.locator("#add_variable").click()
    variable = modal.locator(f"{VARIABLE_CARD}.draft")
    variable.locator(".accordion-button").click()
    variable.locator('input[aria-describedby="variable-name-feedback"]').fill("speed")
    variable.locator("input.variable-type").fill("int")
    variable.locator("input.variable-type").press("Tab")
    variable.locator(".accordion-button").click()
    modal.locator("#add_formalization").click()

    # both cards carry temp ids here, so the saved order only holds if the save maps each temp id to its real id.
    items = modal.locator("#formalization_accordion > .accordion-item")
    expect(items.nth(1)).to_have_attribute("data-type", "formalization")
    items.nth(1).locator(".accordion-header").drag_to(
        items.nth(0).locator(".accordion-header"), target_position={"x": 10, "y": 2}, force=True
    )
    expect(items.nth(0)).to_have_attribute("data-type", "formalization")
    save_requirement(page, modal, rid)

    saved = get_formalizations(page, rid)
    order = {f["formalization_type"]: f["order"] for f in saved}
    assert order["formalization"] < order["variable"]

    modal = open_requirement(page, rid)
    expect(modal.locator("#formalization_accordion > .accordion-item").nth(0)).to_have_attribute(
        "data-type", "formalization"
    )
