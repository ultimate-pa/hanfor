import json
import logging
import threading
from typing import Optional

import requests

from ai_request import ai_api_methods_abstract_class


class OllamaStandard(ai_api_methods_abstract_class.AiApiMethod):

    def query_api(
        self,
        query: str,
        url: str,
        api_key: str,
        model_name: str,
        other_params: Optional[dict],
        stop_events: Optional[list[threading.Event]],
    ) -> tuple[str | None, str]:
        if stop_events and any(e.is_set() for e in stop_events):
            return None, "cancelled"

        response_container = [None]
        exception_container = [None]
        ready_event = threading.Event()

        def do_request():
            try:
                response_container[0] = requests.post(
                    url,
                    json={"model": model_name, "prompt": query, "stream": True},
                    timeout=120,
                    stream=True,
                )
            except Exception as e:
                exception_container[0] = e
            finally:
                ready_event.set()

        request_thread = threading.Thread(target=do_request, daemon=True)
        request_thread.start()

        while not ready_event.wait(timeout=0.2):
            if stop_events and any(e.is_set() for e in stop_events):
                return None, "cancelled"

        # Extra check: stop_event could have been set right as ready_event fired
        if stop_events and any(e.is_set() for e in stop_events):
            return None, "cancelled"

        if exception_container[0]:
            e = exception_container[0]
            logging.error(f"Request failed: {e}")
            return None, f"error_ai_connection_{e}"

        response = response_container[0]

        try:
            full_response = []
            for line in response.iter_lines(chunk_size=1):
                if stop_events and any(e.is_set() for e in stop_events):
                    response.close()
                    return None, "cancelled"

                if line:
                    try:
                        data = json.loads(line)
                    except ValueError as e:
                        logging.error(f"Invalid JSON in response: {e}")
                        return None, f"error_ai_response_format_{e}"

                    if "error" in data:
                        logging.error(f"Ollama error: {data['error']}")
                        return None, f"error_ai_response_format_{data['error']}"
                    if "response" in data:
                        full_response.append(data["response"])
                    if data.get("done"):
                        break

            if not full_response:
                logging.error("Empty response from Ollama")
                return None, "error_ai_response_empty"

            return "".join(full_response), "ai_response_received"

        except requests.exceptions.RequestException as e:
            if stop_events and any(e.is_set() for e in stop_events):
                return None, "cancelled"
            logging.error(f"Request failed: {e}")
            return None, f"error_ai_connection_{e}"

    @property
    def provider_names_which_work_with_api_method(self) -> list[str]:
        return ["ollama", "gemma"]
