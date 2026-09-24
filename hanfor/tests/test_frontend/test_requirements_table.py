import json
from urllib.parse import parse_qs

from playwright.sync_api import Page, expect

from tests.test_frontend.helpers import req_url

ROWS = "#requirements_table tbody tr"


def search(page: Page, query: str) -> None:
    page.locator("#search_bar").fill(query)
    page.locator("#search_bar").press("Enter")


def test_requirements_table_lists_requirements(page: Page):
    page.goto("/")
    expect(page.get_by_text("SysRS FooXY_42")).to_be_visible()


def test_search_filters_rows(page: Page):
    page.goto("/")
    expect(page.locator(ROWS)).to_have_count(2)
    search(page, "FooXY_91")
    expect(page.locator(ROWS)).to_have_count(1)
    expect(page.locator(ROWS)).to_contain_text("SysRS FooXY_91")


def test_multi_edit_adds_tag_and_sets_status(page: Page):
    page.goto("/")
    page.locator(".select-all-button").first.click()
    page.locator("#selected-tab").click()
    page.locator("#multi-add-tag-input").fill("reviewed")
    page.locator("#multi-set-status-input").fill("Done")
    # mult-edit ends with a page reload so gotta wait for it before reading the result
    with page.expect_navigation():
        page.locator(".apply-multi-edit").click()

    for rid in ("SysRS FooXY_42", "SysRS FooXY_91"):
        saved = page.request.get(req_url(rid)).json()
        assert "reviewed" in saved["tags"]
        assert saved["status"] == "Done"


def test_csv_export_uses_only_the_filtered_rows(page: Page):
    page.goto("/")
    search(page, "FooXY_91")
    expect(page.locator(ROWS)).to_have_count(1)
    page.locator("#tools-tab").click()
    # assert on the posted id list, the file itself opens in a download popup that starts the download too early to catch
    with page.context.expect_event("request", lambda r: r.url.endswith("/api/tools/csv_file")) as request:
        page.locator("#gen-csv-from-selection").click()

    form = parse_qs(request.value.post_data)
    assert json.loads(form["selected_requirement_ids"][0]) == ["SysRS FooXY_91"]
