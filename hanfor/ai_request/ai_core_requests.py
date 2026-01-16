import threading
from typing import Dict, Optional
import config
import os
import importlib
import logging
from ai_request.ai_api_methods_abstract_class import AiApiMethod


def load_ai_api_methods() -> list[AiApiMethod]:
    """Dynamically loads all AI API method classes from strategies folder."""
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_request_methods/")
    methods = []
    base_package = "ai_request.api_request_methods"

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
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
                            logging.warning(f"Cannot instantiate {attr_name} in {module_path}: {e}")
            except ModuleNotFoundError as e:
                logging.error(f"Error loading module {module_path}: {e}")
    return methods


class AiRequest:
    """
    Holds data for AI requests: model name, selected API method, etc.
    Automatically maps AI models to their API methods.
    """

    def __init__(self):
        ai_api_methods = load_ai_api_methods()
        model_to_api_method: Dict[str, AiApiMethod] = {
            m: method for method in ai_api_methods for m in method.model_names_which_work_with_api_method
        }
        self.__ai_models: Dict[str, dict] = {
            key: {
                "description": value,
                "selected": key == config.STANDARD_AI_MODEL,
                "api_method_object": model_to_api_method.get(key),
            }
            for key, value in config.AI_MODEL_NAMES.items()
        }
        for name, value in self.__ai_models.items():
            if not value["api_method_object"]:
                logging.warning(f"AI model [{name}] has no API method! Please select one or create a new one.")
        self.model_name: str = config.STANDARD_AI_MODEL
        self.ai_api_method = self.__ai_models[self.model_name]["api_method_object"]

    def set_model(self, model_name: str):
        """Setzt das AI Modell und lädt die passende API-Methode."""
        if model_name not in self.__ai_models:
            raise ValueError(f"Unknown AI model: {model_name}")
        self.model_name = model_name
        self.ai_api_method = self.__ai_models[model_name]["api_method_object"]
        if not self.ai_api_method:
            logging.warning(f"Selected AI model [{model_name}] has no API method!")

    def get_all_models(self):
        return self.__ai_models

    def ask_ai(self, prompt: str, stop_event: Optional[threading.Event]) -> (str, str):
        """returns the ai_response and the status"""
        return self.ai_api_method.query_api(prompt, self.model_name)
