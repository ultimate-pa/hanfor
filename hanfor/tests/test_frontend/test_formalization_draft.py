from urllib.parse import quote

from playwright.sync_api import Page, expect

RID = "SysRS FooXY_42"
FORMALIZATIONS_URL = f"/api/v1/req/{quote(RID)}/formalizations"


def test_save_default_formalization_draft(page: Page):
    existing_ids = {f["id"] for f in page.request.get(FORMALIZATIONS_URL).json()}

    page.goto("/")
    page.get_by_role("link", name=RID, exact=True).click()
    modal = page.locator("#requirement_modal")
    expect(modal).to_be_visible()

    formalizations = modal.locator("#formalization_accordion > .accordion-item")
    expect(formalizations).to_have_count(len(existing_ids))
    modal.locator("#add_formalization").click()
    expect(formalizations).to_have_count(len(existing_ids) + 1)

    # For saving always use `with req as save` to avoid the race condition of proceeding
    # with the test before doing the api testing
    with page.expect_response(lambda r: r.request.method == "PATCH" and quote(RID) in r.url) as save:
        modal.locator("#save_requirement_modal").click()
    assert save.value.ok
    expect(modal).to_be_hidden()

    response = page.request.get(FORMALIZATIONS_URL)
    expect(response).to_be_ok()
    new = [f for f in response.json() if f["id"] not in existing_ids]
    assert len(new) == 1
    assert new[0]["formalization_type"] == "formalization"
    assert new[0]["scope"] == "NONE"
    assert new[0]["pattern"] == "NotFormalizable"
    assert not any(key.startswith("expr_") for key in new[0])


def test_fill_draft_and_save(page: Page) -> None:
    rid = "SysRS FooXY_91"
    page.goto("/")
    page.get_by_role("link", name=rid, exact=True).click()
    modal = page.locator("#requirement_modal")
    modal.locator("#add_formalization").click()

    draft = modal.locator("#formalization_accordion > .accordion-item.draft")
    draft.locator(".accordion-button").click()
    draft.locator(".scope_selector").select_option("GLOBALLY")
    draft.locator(".pattern_selector").select_option("TransitionG")
    draft.get_by_role("textbox", name="R", exact=True).fill("foo")
    draft.get_by_role("textbox", name="S", exact=True).fill("bar")
    draft.get_by_role("textbox", name="V", exact=True).fill("baz")

    with page.expect_response(lambda r: r.request.method == "PATCH" and quote(rid) in r.url) as save:
        modal.locator("#save_requirement_modal").click()
    assert save.value.ok
    expect(modal).to_be_hidden()

    response = page.request.get(f"/api/v1/req/{quote(rid)}")
    expect(response).to_be_ok()
    assert sorted(response.json()["vars"]) == sorted(["bar", "baz", "foo"])
