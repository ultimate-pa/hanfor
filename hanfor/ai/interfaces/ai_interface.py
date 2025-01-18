import time
import requests
import logging
from hanfor import boogie_parsing
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


def query_ai(query: str) -> (str, str):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1:8b", "prompt": query, "stream": False},
        )
        response_json = response.json()
        if "response" in response_json:
            return response_json["response"], "ai_response_received"
        else:
            logging.error(f"Key 'response' not found in AI response: {response_json}")
            return None, "error_ai_response_format"
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None, "error_ai_connection"
    except ValueError as e:
        logging.error(f"Invalid JSON in response: {e}")
        return None, "error_ai_response_format"


class AIFormalization:
    def __init__(self, req_ai, req_formal, stop_event_ai):
        self.try_count = 1
        self.req_ai = req_ai
        self.req_formal = req_formal
        self.prompt = None
        self.ai_response = None
        self.formalized_output = None
        self.status = "initialized"
        self.del_time = None
        self.stop_event = stop_event_ai

    def test_formalization_complete(self) -> bool:
        if (
            self.formalized_output["scope"] in scope
            and self.formalized_output["pattern"] in pattern
            and self.formalized_output["expression_mapping"].keys() == {"P", "Q", "R", "S", "T", "U", "V"}
        ):
            parser = boogie_parsing.get_parser_instance()
            # Test all non-empty strings in "expression_mapping" values
            for key, value in self.formalized_output["expression_mapping"].items():
                if value.strip():
                    try:
                        parser.parse(value)
                    except Exception as e:
                        logging.error(f"Error while parsing expression_mapping[{key}]: {e}")
                        return False

            logging.debug("true" + str(self.req_ai.to_dict()))
            return True
        logging.debug("false" + str(self.req_ai.to_dict()))
        return False

    def run_process(self, ai_processing_queue):
        while self.try_count < 5:
            self.status = "generating_prompt"
            self.status, self.prompt = ai_formalization_methods.create_prompt(self.req_formal, self.req_ai)

            if self.stop_event.is_set():
                self.status = "terminated_" + self.status
                self.del_time = time.time()
                return

            # Checking if the AI can process a Prompt
            self.status = "waiting_in_ai_queue"
            req_id = self.req_ai.to_dict()["id"]
            while not ai_processing_queue.add_request(req_id):
                time.sleep(1)
                if self.stop_event.is_set():
                    self.status = "terminated_" + self.status
                    self.del_time = time.time()
                    ai_processing_queue.terminated(req_id)
                    return
            self.status = "waiting_ai_response"
            self.ai_response, self.status = query_ai(self.prompt)
            ai_processing_queue.complete_request(req_id)

            if self.stop_event.is_set():
                self.status = "terminated_" + self.status
                self.del_time = time.time()
                return

            if self.status.startswith("error"):
                self.try_count += 1
                continue

            self.status = "parsing_ai_response"
            self.status, self.formalized_output = ai_formalization_methods.parse_ai_response(self.ai_response)

            if self.stop_event.is_set():
                self.status = "terminated_" + self.status
                self.del_time = time.time()
                return

            if self.status.startswith("error"):
                self.try_count += 1
                continue

            logging.info(self.formalized_output)

            if self.test_formalization_complete():
                self.status = "complete"
                break

            self.status = "error"
            self.try_count += 1

        self.del_time = time.time()
