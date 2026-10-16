from playwright.sync_api import Page, expect

from tests.test_frontend.helpers import open_requirement, req_url, save_requirement

RID = "SysRS FooXY_91"


def test_set_status_and_add_tag_with_comment(page: Page) -> None:
    modal = open_requirement(page, RID)
    modal.get_by_role("radio", name="Review").check()
    tag_input = modal.locator("#requirement_tag_field-tokenfield")
    tag_input.fill("timing")
    tag_input.press("Enter")

    # The save reads tags from the comment table, so the row must exist before the comment is set.
    row = modal.locator("#tags_comments_table tr").filter(has_text="timing")
    expect(row).to_have_count(1)
    row.locator("textarea").fill("check the 5ms bound")
    save_requirement(page, modal, RID)

    response = page.request.get(req_url(RID))
    expect(response).to_be_ok()
    saved = response.json()
    assert saved["status"] == "Review"
    assert "timing" in saved["tags"]
    assert saved["tags_comments"]["timing"] == "check the 5ms bound"
