import logging
import threading
from typing import Optional

import requests
from configuration import ai_config
from ai_request import ai_api_methods_abstract_class


class OllamaStandard(ai_api_methods_abstract_class.AiApiMethod):
    def query_api(
        self,
        query: str,
        url: str,
        api_key: str,
        model_name: str,
        other_params: Optional[dict],
        stop_event: Optional[threading.Event],
    ) -> tuple[str | None, str]:
        try:
            response = requests.post(
                url,
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
    def provider_names_which_work_with_api_method(self) -> list[str]:
        return ["ollama"]
