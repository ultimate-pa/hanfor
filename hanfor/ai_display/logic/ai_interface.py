import logging
import time
from reqtransformer import Requirement

# URL of the service endpoint
SERVICE_URL = "http://127.0.0.1:5000/api/req/"

# Dictionary for predefined formalization templates
FORMALIZATION_TEMPLATES = {
    "REQ001": {
        "scope": "GLOBALLY",
        "pattern": "Universality",
        "expression_mapping": {"P": "", "Q": "", "R": "var1 > 5", "S": "", "T": "", "U": "", "V": ""},
    },
    "REQ002": {
        "scope": "GLOBALLY",
        "pattern": "Universality",
        "expression_mapping": {"P": "", "Q": "", "R": "var2 < 10", "S": "", "T": "", "U": "", "V": ""},
    },
    "REQ003": {
        "scope": "GLOBALLY",
        "pattern": "Universality",
        "expression_mapping": {"P": "", "Q": "", "R": "constraint1", "S": "", "T": "", "U": "", "V": ""},
    },
    "REQ004": {
        "scope": "GLOBALLY",
        "pattern": "Absence",
        "expression_mapping": {"P": "", "Q": "", "R": "constraint2", "S": "", "T": "", "U": "", "V": ""},
    },
    "REQ007": {
        "scope": "GLOBALLY",
        "pattern": "Invariant",
        "expression_mapping": {"P": "", "Q": "", "R": "var3", "S": "var4 == 0", "T": "", "U": "", "V": ""},
    },
    "REQ008": {
        "scope": "GLOBALLY",
        "pattern": "Invariant",
        "expression_mapping": {"P": "", "Q": "", "R": "var3", "S": "var4 == 1", "T": "", "U": "", "V": ""},
    },
}


# AI-based formalization function
def generate_formalization(req_ai: Requirement, req_formal: Requirement) -> dict:
    # Simulate processing time
    time.sleep(5)
    req_id = req_ai.to_dict(include_used_vars=True)["id"]

    # Check if the requirement ID exists in the predefined templates
    if req_id in FORMALIZATION_TEMPLATES:
        return FORMALIZATION_TEMPLATES[req_id]
    else:
        logging.warning(f"Requirement ID {req_id} not found in predefined templates.")
        return {
            "scope": "GLOBALLY",
            "pattern": "Universality",
            "expression_mapping": {"P": "", "Q": "", "R": "True", "S": "", "T": "", "U": "", "V": ""},
        }
