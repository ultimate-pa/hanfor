import json
import logging
import threading
from typing import Optional

import requests
from requests import Response

from ai_request import ai_api_methods_abstract_class
from thread_handling.thread_function_decorator import is_stopped, set_status


class OllamaStandard(ai_api_methods_abstract_class.AiApiMethod):

    def query_api(
        self,
        query: str,
        url: str,
        api_key: str,
        model_name: str,
        other_params: Optional[dict],
    ) -> tuple[str | None, str]:
        if is_stopped():
            return None, "cancelled"

        set_status("connecting...")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "system", "content": ""}, {"role": "user", "content": query}],
            **(other_params or {}),
            "stream": False,
        }

        result: dict[str, None | Exception | Response] = {"response": None, "exception": None}

        def do_request():
            try:
                result["response"] = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
            except Exception as exept:
                result["exception"] = exept

        request_thread = threading.Thread(target=do_request, daemon=True)
        request_thread.start()

        while request_thread.is_alive():
            request_thread.join(timeout=0.2)
            if is_stopped():
                return None, "cancelled"

        if result["exception"]:
            e = result["exception"]
            logging.error(f"Request failed: {e}")
            return None, f"error_ai_connection_{e}"

        response: Response = result["response"]

        if not response.ok:
            logging.error(f"HTTP error: {response.status_code} {response.text}")
            return None, f"error_ai_connection_http_{response.status_code}"

        data = response.json()

        # OpenAI format
        if "choices" in data:
            text = data["choices"][0]["message"]["content"]
        # Ollama format
        elif "message" in data:
            text = data["message"]["content"]
        else:
            logging.error(f"Unknown response format: {data}")
            return None, "error_ai_unknown_format"

        return text, "ai_response_received"
