import time
import requests
import logging
from hanfor.ai.strategies import ai_formalization_methods

pattern = [
    "Response",
    "ResponseChain1-2",
    "ConstrainedChain",
    "Precedence",
    "PrecedenceChain2-1",
    "PrecedenceChain1-2",
    "Universality",
    "UniversalityDelay",
    "BoundedExistence",
    "Invariant",
    "Absence",
    "BoundedResponse",
    "BoundedRecurrence",
    "MaxDuration",
    "TimeConstrainedMinDuration",
    "BoundedInvariance",
    "TimeConstrainedInvariant",
    "MinDuration",
    "ConstrainedTimedExistence",
    "BndTriggeredEntryConditionPattern",
    "BndTriggeredEntryConditionPatternDelayed",
    "EdgeResponsePatternDelayed",
    "BndEdgeResponsePattern",
    "BndEdgeResponsePatternDelayed",
    "BndEdgeResponsePatternTU",
    "Initialization",
    "Persistence",
    "Toggle1",
    "Toggle2",
    "BndEntryConditionPattern",
    "ResponseChain2-1",
    "Existence",
]
scope = ["GLOBALLY", "BEFORE", "AFTER", "BETWEEN", "AFTER_UNTIL"]


class AIFormalization:
    def __init__(self, req_ai, req_formal, stop_event_ai):
        self.req_ai = req_ai
        self.req_formal = req_formal
        self.prompt = None
        self.ai_response = None
        self.formalized_output = None
        self.status = "initialized"
        self.del_time = None
        self.stop_event = stop_event_ai

    def query_ai(self):
        self.status = "waiting_ai_response"
        try:
            self.ai_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.1:8b", "prompt": self.prompt, "stream": False},
            ).json()["response"]
        except requests.exceptions.RequestException as e:
            logging.error(e)
            self.status = "error_ai_connection"
            return
        self.status = "ai_response_received"

    def test_formalization_complete(self) -> bool:
        if (
            self.formalized_output["scope"] in scope
            and self.formalized_output["pattern"] in pattern
            and self.formalized_output["expression_mapping"].keys() == {"P", "Q", "R", "S", "T", "U", "V"}
        ):
            logging.debug("true" + str(self.req_ai.to_dict()))
            return True
        logging.debug("false" + str(self.req_ai.to_dict()))
        return False

    def run_process(self):
        self.status = "generating_prompt"
        (self.status, self.prompt) = ai_formalization_methods.create_prompt(self.req_formal, self.req_ai)

        if self.stop_event.is_set():
            self.status = "terminated_" + self.status
            self.del_time = time.time()
            return

        self.query_ai()

        if self.stop_event.is_set() or self.status.startswith("error"):
            self.status = "terminated_" + self.status
            self.del_time = time.time()
            return

        self.status = "parsing_ai_response"
        (self.status, self.formalized_output) = ai_formalization_methods.parse_ai_response(self.ai_response)
        if self.stop_event.is_set() or self.status.startswith("error"):
            self.status = "terminated_" + self.status
            self.del_time = time.time()
            return

        logging.info(self.formalized_output)
        if self.test_formalization_complete():
            self.status = "complete"
        else:
            self.status = "error"

        self.del_time = time.time()
