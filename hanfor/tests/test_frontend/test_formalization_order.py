from playwright.sync_api import Page, expect

from tests.test_frontend.helpers import create_formalization, get_formalizations, open_requirement, save_requirement


def test_reorder_formalizations(page: Page):
    rid = "SysRS FooXY_42"
    create_formalization(page, rid, 1, "GLOBALLY", "Absence", {"R": "foo == bar"})

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
