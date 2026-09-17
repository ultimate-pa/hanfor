from playwright.sync_api import Page, expect

from tests.test_frontend.helpers import get_formalizations, open_requirement, req_url, save_requirement


def test_save_default_formalization_draft(page: Page):
    rid = "SysRS FooXY_42"
    existing_ids = {f["id"] for f in get_formalizations(page, rid)}
    assert existing_ids == {0}

    modal = open_requirement(page, rid)
    formalizations = modal.locator("#formalization_accordion > .accordion-item")
    expect(formalizations).to_have_count(len(existing_ids))
    modal.locator("#add_formalization").click()
    expect(formalizations).to_have_count(len(existing_ids) + 1)
    save_requirement(page, modal, rid)

    new = [f for f in get_formalizations(page, rid) if f["id"] not in existing_ids]
    assert len(new) == 1
    assert new[0]["formalization_type"] == "formalization"
    assert new[0]["scope"] == "NONE"
    assert new[0]["pattern"] == "NotFormalizable"
    assert not any(key.startswith("expr_") for key in new[0])


def test_fill_draft_and_save(page: Page) -> None:
    rid = "SysRS FooXY_91"
    modal = open_requirement(page, rid)
    modal.locator("#add_formalization").click()

    draft = modal.locator("#formalization_accordion > .accordion-item.draft")
    draft.locator(".accordion-button").click()
    draft.locator(".scope_selector").select_option("GLOBALLY")
    draft.locator(".pattern_selector").select_option("TransitionG")
    draft.get_by_role("textbox", name="R", exact=True).fill("foo")
    draft.get_by_role("textbox", name="S", exact=True).fill("bar")
    draft.get_by_role("textbox", name="V", exact=True).fill("baz")
    save_requirement(page, modal, rid)

    response = page.request.get(req_url(rid))
    expect(response).to_be_ok()
    assert sorted(response.json()["vars"]) == sorted(["bar", "baz", "foo"])


def test_add_several_drafts_save_then_edit_the_first(page: Page) -> None:
    rid = "SysRS FooXY_91"
    assert get_formalizations(page, rid) == []

    modal = open_requirement(page, rid)
    items = modal.locator("#formalization_accordion > .accordion-item")
    expect(items).to_have_count(0)
    for _ in range(4):
        modal.locator("#add_formalization").click()
    expect(items).to_have_count(4)
    save_requirement(page, modal, rid)

    saved = get_formalizations(page, rid)
    assert {f["id"] for f in saved} == {0, 1, 2, 3}
    assert all(f["scope"] == "NONE" and f["pattern"] == "NotFormalizable" for f in saved)

    modal = open_requirement(page, rid)
    items = modal.locator("#formalization_accordion > .accordion-item")
    expect(items).to_have_count(4)
    expect(items.nth(0)).to_have_attribute("data-id", "0")

    first = items.nth(0)
    first.locator(".accordion-button").click()
    first.locator(".scope_selector").select_option("GLOBALLY")
    first.locator(".pattern_selector").select_option("Absence")
    first.get_by_role("textbox", name="R", exact=True).fill("bright_side")
    save_requirement(page, modal, rid)

    edited = {f["id"]: f for f in get_formalizations(page, rid)}
    assert set(edited) == {0, 1, 2, 3}
    assert edited[0]["scope"] == "GLOBALLY"
    assert edited[0]["pattern"] == "Absence"
    assert edited[0]["expr_R"] == "bright_side"
    assert all(edited[fid]["pattern"] == "NotFormalizable" for fid in (1, 2, 3))

    modal = open_requirement(page, rid)
    modal.locator("#add_formalization").click()
    save_requirement(page, modal, rid)

    final = {f["id"]: f for f in get_formalizations(page, rid)}
    assert set(final) == {0, 1, 2, 3, 4}
    assert final[0]["expr_R"] == "bright_side"
