from playwright.sync_api import Page, expect


def test_requirements_table_lists_requirements(page: Page):
    page.goto("/")
    expect(page.get_by_text("SysRS FooXY_42")).to_be_visible()
