import logging

import requests

from ai import ai_config
from ai.strategies import ai_api_methods_abstract_class


class OllamaStandard(ai_api_methods_abstract_class.AiApiMethod):
    def query_api(self, query: str, model_name: str) -> (str, str):
        try:
            response = requests.post(
                ai_config.AI_API_URL,
                json={"model": model_name, "prompt": query, "stream": False},
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

    @property
    def model_names_which_work_with_api_method(self) -> list[str]:
        return ["llama3.1:70b"]
