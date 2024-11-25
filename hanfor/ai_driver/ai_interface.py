import requests
from reqtransformer import Requirement

url = "http://127.0.0.1:5000/api/req/"

formal_dict = {
    "REQ1": '{"0":{"id":"0","scope":"GLOBALLY","pattern":"Universality","expression_mapping":{"P":"","Q":"","R":"var1 > 5", "S": "", "T": "", "U": "", "V": ""}}}',
    "REQ2": '{"0":{"id":"0","scope":"GLOBALLY","pattern":"Universality","expression_mapping":{"P":"","Q":"","R":"var2 < 10", "S": "", "T": "", "U": "", "V": ""}}}',
    "REQ3": '{"0":{"id":"0","scope":"GLOBALLY","pattern":"Universality","expression_mapping":{"P":"","Q":"","R":"constraint1", "S": "", "T": "", "U": "", "V": ""}}}',
    "REQ4": '{"0":{"id":"0","scope":"GLOBALLY","pattern":"Absence","expression_mapping":{"P":"","Q":"","R":"constraint2", "S": "", "T": "", "U": "", "V": ""}}}',
    "REQ7": '{"0":{"id":"0","scope":"GLOBALLY","pattern":"Invariant","expression_mapping":{"P":"","Q":"","R":"var3", "S": "var4 == 0", "T": "", "U": "", "V": ""}}}',
    "REQ8": '{"0":{"id":"0","scope":"GLOBALLY","pattern":"Invariant","expression_mapping":{"P":"","Q":"","R":"var3", "S": "var4 == 1", "T": "", "U": "", "V": ""}}}',
}


def post_create_new_formalization(req_id: str):
    headers = {
        "accept": "*/*",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "x-requested-with": "XMLHttpRequest",
    }
    data = {"id": req_id}
    requests.post(url + "new_formalization", headers=headers, data=data)


def post_update_formalization(req_id: str, formalization: str):
    data = {
        "id": req_id,
        "row_idx": "2",
        "update_formalization": "true",
        "tags": "{}",
        "status": "Todo",
        "formalizations": formalization,
    }
    requests.post(url + "update", data=data)


def ai_formalization(req_formal: Requirement, req_list: [Requirement]):
    for req in req_list:
        # do stuff
        req_id = req["id"]
        post_create_new_formalization(req_id)
        post_update_formalization(req_id, formal_dict[req_id])
