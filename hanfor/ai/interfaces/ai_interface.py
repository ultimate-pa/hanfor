import os
import importlib
import time
from typing import Optional
import logging
import reqtransformer
from ai.ai_enum import AiDataEnum
from ai.strategies.ai_api_methods_abstract_class import AiApiMethod
from ai.strategies.ai_prompt_parse_abstract_class import AiPromptParse, get_scope, get_pattern
import ai.ai_config as ai_config
from lib_core import boogie_parsing

pattern = get_pattern().keys()
scope = get_scope().keys()


def load_ai_prompt_parse_methods() -> dict[str, AiPromptParse]:
    """Dynamically loads all AI algorithms from the specified directory."""

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../strategies/ai_prompt_parse_methods/")
    methods = {}
    base_package = "ai.strategies.ai_prompt_parse_methods"

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


def load_ai_api_methods() -> list[AiApiMethod]:
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../strategies/ai_api_methods/")
    methods = []
    base_package = "ai.strategies.ai_api_methods"

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            # Import Modul
            module_name = filename[:-3]
            module_path = f"{base_package}.{module_name}"

            try:
                module = importlib.import_module(module_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, AiApiMethod) and attr is not AiApiMethod:
                        try:
                            instance = attr()
                            methods.append(instance)
                        except TypeError as e:
                            logging.warning(f"Class {attr_name} in module {module_path} could not be instantiated: {e}")
            except ModuleNotFoundError as e:
                logging.error(f"Error loading module {module_path}: {e}")
    return methods


def query_ai(query: str, model_info: dict, enable_api_ai_request: bool) -> (str, str):
    """Sends a query to the AI API. enable_api_ai_request should be the AI flag in AiData."""

    if not enable_api_ai_request:
        return None, "error_AI_API_requests_off"

    return model_info[1]["api_method_object"].query_api(query, model_info[0])


class AIFormalization:
    """Class to handle AI-based formalization of requirements, including prompt generation, AI querying, response parsing, and validation."""

    def __init__(
        self,
        requirement_to_formalize: reqtransformer.Requirement,
        requirement_with_formalization: list[reqtransformer.Requirement],
        stop_event_ai,
        ai_processing_queue,
        prompt_generator: callable,
        response_parser: callable,
        used_variables: list[dict],
        ai_model: tuple[str, dict],
        enable_api_ai_request: bool,
        req_logger: callable,
        update_status_function,
    ):
        self.requirement_to_formalize = requirement_to_formalize
        self.requirement_with_formalization = requirement_with_formalization

        self.status = "initialized"
        self.del_time = None
        self.try_count = 1
        self.stop_event = stop_event_ai

        self.prompt = None
        self.ai_response = None
        self.formalized_output = None

        self.req_id = self.requirement_to_formalize.to_dict()["id"]
        self.ai_processing_queue = ai_processing_queue
        self.prompt_generator = prompt_generator
        self.response_parser = response_parser
        self.variables = used_variables
        self.ai_model = ai_model
        self.enable_api_ai_request = enable_api_ai_request

        self.req_logger = req_logger
        self.update_status_function = update_status_function

    def __update_status(self, status: str):
        self.status = status
        self.update_status_function(AiDataEnum.FORMALIZATION, None, None)

    def run_formalization_process(
        self,
        ai_statistic,
        prompt_generator_name: str,
    ) -> None:

        # Initial status log
        requirement_with_formalization = [x.to_dict()["id"] for x in self.requirement_with_formalization]
        data_dict = {
            "message": "Initiating AI formalization",
            "description": f"{self.requirement_to_formalize.to_dict().get("desc", "")}",
            "formalized_requirements": f"{requirement_with_formalization}",
            "ai_model": f"{self.ai_model[0]}",
            "prompt_or_parser": f"{prompt_generator_name}",
        }
        self.req_logger(self.req_id, data_dict)

        # All steps in separate methods
        steps = [
            self.__step_generate_prompt,
            self.__step_ai_processing_queue,
            self.__step_query_ai,
            self.__step_response_parser,
            self.__step_test_formalization_complete,
        ]

        while self.try_count < ai_config.MAX_AI_FORMALIZATION_TRYS:
            for step_function in steps:

                # Terminated Ai Threads
                if self.stop_event.is_set():
                    self.__update_status(f"terminated_{self.status}")
                    self.del_time = time.time()
                    self.__req_logger_ai_process()
                    ai_statistic.add_status(self.ai_model[0], prompt_generator_name, self.status)
                    return

                output = step_function()

                # Error occurs
                if output is None:
                    self.__update_status(f"error_{self.status}")
                    break

            # Logging Progress
            self.__req_logger_ai_process()
            ai_statistic.add_status(self.ai_model[0], prompt_generator_name, self.status)

            # Again or finished
            if self.status == "complete":
                break
            else:
                self.try_count += 1

        # Finish up
        self.del_time = time.time()
        ai_statistic.add_try_count(self.ai_model[0], prompt_generator_name, self.try_count)
        self.__update_status(self.status)

    def __test_formalization_complete(self) -> bool:
        """
        Checks if the formalization is complete by validating the scope, pattern, and expression mappings.
        + trying to parse before inserting in Hanfor
        """

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
        logging.debug("true" + str(self.requirement_to_formalize.to_dict()))
        return True

    def __req_logger_ai_process(self) -> None:
        """Helper method to log a request to the AI API."""

        requirement_with_formalization = [x.to_dict()["id"] for x in self.requirement_with_formalization]
        data_dict = {
            "try_count": f"{self.try_count}",
            "requirement_with_formalization": f"{requirement_with_formalization}",
            "ai_response": f"{self.ai_response}",
            "formalized_output": f"{self.formalized_output}",
            "status": f"{self.status}",
        }

        self.req_logger(self.req_id, data_dict)

    def __step_generate_prompt(self) -> Optional[str]:
        self.__update_status("generating_prompt")
        self.__req_logger_ai_process()

        self.prompt = self.prompt_generator(
            self.requirement_to_formalize, self.requirement_with_formalization, self.variables
        )

        self.req_logger(self.req_id, {"message": "created prompt", "prompt": self.prompt})

        self.__update_status("prompt_generated")
        return self.prompt

    def __step_ai_processing_queue(self) -> True:
        self.__update_status("waiting_for_ai_slot")
        self.__req_logger_ai_process()

        while not self.ai_processing_queue.add_request(self.req_id):
            time.sleep(1)
            if self.stop_event.is_set():
                self.ai_processing_queue.terminated(self.req_id)
                return True

        self.__update_status("acquired_slot_in_ai")
        return True

    def __step_query_ai(self) -> Optional[str]:
        self.__update_status("waiting_ai_response")
        self.__req_logger_ai_process()

        self.ai_response, self.status = query_ai(self.prompt, self.ai_model, self.enable_api_ai_request)
        self.__update_status("ai_response_received")

        self.ai_processing_queue.complete_request(self.req_id)
        return self.ai_response

    def __step_response_parser(self) -> Optional[dict[str, str | dict[str, str]]]:
        self.__update_status("parsing_ai_response")
        self.__req_logger_ai_process()

        self.formalized_output = self.response_parser(self.ai_response, self.variables)

        self.__update_status("ai_response_parsed")
        return self.formalized_output

    def __step_test_formalization_complete(self) -> Optional[bool]:
        self.__update_status("test_formalization_complete")
        if self.__test_formalization_complete():
            self.__update_status("complete")
            return True
        return None
