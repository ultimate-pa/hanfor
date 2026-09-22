import json
from urllib.parse import quote

from playwright.sync_api import Locator, Page, expect

VARIABLE_CARD = '#formalization_accordion > .accordion-item[data-type="variable"]'


def req_url(rid: str) -> str:
    return f"/api/v1/req/{quote(rid)}"


def open_requirement(page: Page, rid: str) -> Locator:
    page.goto("/")
    page.get_by_role("link", name=rid, exact=True).click()
    modal = page.locator("#requirement_modal")
    expect(modal).to_be_visible()
    return modal


def save_requirement(page: Page, modal: Locator, rid: str) -> None:
    # For saving always use `with req as save` to avoid the race condition of proceeding
    # with the test before doing the api testing
    with page.expect_response(lambda r: r.request.method == "PATCH" and quote(rid) in r.url) as save:
        modal.locator("#save_requirement_modal").click()
    assert save.value.ok
    expect(modal).to_be_hidden()


def get_formalizations(page: Page, rid: str, subtype: str | None = None) -> list[dict]:
    params = {"subtype": subtype} if subtype else None
    response = page.request.get(f"{req_url(rid)}/formalizations", params=params)
    expect(response).to_be_ok()
    return response.json()


def create_formalization(page: Page, rid: str, scope: str, pattern: str, mapping: dict, temp_id: str = "tmp-1") -> int:
    data = {"scope": scope, "pattern": pattern, "expression_mapping": mapping}
    response = page.request.post(
        f"{req_url(rid)}/formalizations/formalization/{temp_id}", form={"data": json.dumps(data)}
    )
    expect(response).to_be_ok()
    return response.json()["id"]


def create_variable(page: Page, rid: str, name: str, var_type: str, temp_id: str = "tmp-1") -> int:
    data = {"name": name, "type": var_type}
    response = page.request.post(f"{req_url(rid)}/formalizations/variable/{temp_id}", form={"data": json.dumps(data)})
    expect(response).to_be_ok()
    return response.json()["id"]


def confirm_delete(button: Locator) -> None:
    # The delete buttons use a two-click confirm, the first click only arms the button.
    button.click()
    expect(button).to_have_text("Do it!")
    button.click()
