import time
import requests
import logging
from hanfor.ai.strategies import ai_formalization_methods


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

        self.del_time = time.time()
