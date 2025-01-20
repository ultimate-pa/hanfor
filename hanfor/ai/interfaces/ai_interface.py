import os
import importlib
import time
import requests
import logging
from hanfor import boogie_parsing
from hanfor.ai.strategies.ai_prompt_parse_abstract_class import AiPromptParse, get_scope, get_pattern
import hanfor.ai.ai_config as ai_config

pattern = get_pattern().keys()
scope = get_scope().keys()


def load_ai_prompt_parse_methods() -> dict[str, AiPromptParse]:
    """Dynamically loads all AI algorithms from the specified directory."""

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../strategies/ai_prompt_parse_methods/")
    methods = {}
    base_package = "hanfor.ai.strategies.ai_prompt_parse_methods"

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            # Import Modul
            module_name = filename[:-3]
            module_path = f"{base_package}.{module_name}"

            try:
                module = importlib.import_module(module_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, AiPromptParse) and attr is not AiPromptParse:
                        try:
                            instance = attr()
                            methods[instance.name] = instance
                        except TypeError as e:
                            logging.warning(f"Class {attr_name} in module {module_path} could not be instantiated: {e}")
            except ModuleNotFoundError as e:
                logging.error(f"Error loading module {module_path}: {e}")
    return methods


def query_ai(query: str, model: str, enable_api_ai_request: bool) -> (str, str):

    if not enable_api_ai_request:
        return None, "error_AI_API_requests_off"

    try:
        response = requests.post(
            ai_config.AI_API_URL,
            json={"model": model, "prompt": query, "stream": False},
        )
        response_json = response.json()
        if "response" in response_json:
            return response_json["response"], "ai_response_received"
        else:
            logging.error(f"Key 'response' not found in AI response: {response_json}")
            return None, f"error_ai_response_format_{response_json}"
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None, f"error_ai_connection_{e}"
    except ValueError as e:
        logging.error(f"Invalid JSON in response: {e}")
        return None, f"error_ai_response_format_{e}"


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
        if self.formalized_output["scope"] not in scope:
            logging.error(f"Scope {self.formalized_output["scope"]} not found in {scope}, skipping")
            return False
        if self.formalized_output["pattern"] not in pattern:
            logging.error(f"Pattern {self.formalized_output["pattern"]} not found in {pattern}, skipping")
            return False
        if self.formalized_output["expression_mapping"].keys() != {"P", "Q", "R", "S", "T", "U", "V"}:
            logging.error(f"expression_mapping {self.formalized_output["expression_mapping"]} not okay, skipping")
            return False

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

    def run_process(
        self,
        ai_processing_queue,
        prompt_generator: callable,
        response_parser: callable,
        used_variables: list[dict],
        ai_model: str,
        enable_api_ai_request: bool,
        ai_statistic,
        prompt_generator_name: str,
    ):
        while self.try_count < ai_config.MAX_AI_FORMALIZATION_TRYS:
            self.status = "generating_prompt"
            self.prompt = prompt_generator(self.req_formal, self.req_ai, used_variables)

            if self.prompt is None:
                self.status = "error_generating_prompt"
                self.try_count += 1
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                continue
            else:
                self.status = "prompt_created"

            if self.stop_event.is_set():
                self.status = "terminated_" + self.status
                self.del_time = time.time()
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
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
                    ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                    return
            self.status = "waiting_ai_response"
            self.ai_response, self.status = query_ai(self.prompt, ai_model, enable_api_ai_request)
            ai_processing_queue.complete_request(req_id)

            if self.stop_event.is_set():
                self.status = "terminated_" + self.status
                self.del_time = time.time()
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                return

            if self.status.startswith("error"):
                self.try_count += 1
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                continue

            self.status = "parsing_ai_response"
            self.formalized_output = response_parser(self.ai_response, used_variables)

            if self.formalized_output is None:
                self.status = "error_parsing"
                self.try_count += 1
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                continue
            else:
                self.status = "response_parsed"

            if self.stop_event.is_set():
                self.status = "terminated_" + self.status
                self.del_time = time.time()
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                return

            if self.status.startswith("error"):
                self.try_count += 1
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                continue

            logging.info(self.formalized_output)

            if self.test_formalization_complete():
                self.status = "complete"
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)
                break
            else:
                self.status = "error_failed_test_formalization_complete"
                self.try_count += 1
                ai_statistic.update_status(ai_model, prompt_generator_name, self.status)

        ai_statistic.add_try_count(ai_model, prompt_generator_name, self.try_count)
        self.del_time = time.time()
