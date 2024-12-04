import logging
import time
import random
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
    t = random.randint(5, 15)
    time.sleep(t)
    logging.info(f"Time: {t}s")
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


class AIFormalization:
    """
    A class to handle the AI-based formalization process with clear statuses.
    """

    def __init__(self, req_ai, req_formal):
        self.req_ai = req_ai
        self.req_formal = req_formal
        self.prompt = None
        self.ai_response = None
        self.formalized_output = None
        self.status = "initialized"
        self.time = None

    def create_prompt(self):
        """
        Generate the prompt for the AI based on the input requirement.
        """
        try:
            self.status = "generating_prompt"
            # Simulate processing time
            t = random.randint(2, 5)
            time.sleep(t)
            self.prompt = f"Please formalize the following requirement: {self.req_ai.to_dict()}"
            self.status = "prompt_created"
            logging.info("Prompt created successfully.")
        except Exception as e:
            self.status = "error_in_prompt_creation"
            logging.error(f"Error while creating prompt: {e}")

    def query_ai(self):
        """
        Simulate querying the AI and fetching a response.
        """
        try:
            self.status = "waiting_ai_response"
            # Simulate processing time
            t = random.randint(5, 10)
            time.sleep(t)
            self.ai_response = {
                "formalized_pattern": "Universality",
                "scope": "GLOBALLY",
                "mapping": {"P": "", "Q": "", "R": "True"},
            }
            self.status = "ai_response_received"
            logging.info(f"AI response received in {t}s.")
        except Exception as e:
            self.status = "error_in_ai_query"
            logging.error(f"Error while querying AI: {e}")

    def parse_ai_response(self):
        """
        Parse the AI response into the required formalization structure.
        """
        try:
            self.status = "parsing_ai_response"
            # Simulate processing time
            t = random.randint(2, 5)
            time.sleep(t)
            if not self.ai_response:
                raise ValueError("AI response is empty.")

            self.formalized_output = {
                "scope": self.ai_response.get("scope", "GLOBALLY"),
                "pattern": self.ai_response.get("formalized_pattern", "Universality"),
                "expression_mapping": self.ai_response.get("mapping", {}),
            }
            self.status = "response_parsed"
            logging.info("AI response parsed successfully.")
        except Exception as e:
            self.status = "error_in_response_parsing"
            logging.error(f"Error while parsing AI response: {e}")

    def finalize_output(self):
        """
        Check predefined templates and finalize the formalized output.
        """
        try:
            req_id = self.req_ai.to_dict(include_used_vars=True).get("id")

            if req_id in FORMALIZATION_TEMPLATES:
                self.formalized_output = FORMALIZATION_TEMPLATES[req_id]
                self.status = "finalized_from_template"
                logging.info("Formalized output finalized using predefined template.")
            else:
                self.status = "finalized_with_default"
                logging.warning("Requirement ID not found in predefined templates. Default formalization used.")
        except Exception as e:
            self.status = "error_in_finalization"
            logging.error(f"Error during finalization: {e}")

    def run_process(self):
        """
        Run the entire process step by step.
        """
        self.create_prompt()
        if self.status.startswith("error"):
            self.time = time.time()
            return

        self.query_ai()
        if self.status.startswith("error"):
            self.time = time.time()
            return

        self.parse_ai_response()
        if self.status.startswith("error"):
            self.time = time.time()
            return

        self.finalize_output()
        self.time = time.time()
