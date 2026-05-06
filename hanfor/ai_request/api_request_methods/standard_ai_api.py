import json
import logging
import threading
from typing import Optional

import requests

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
            "stream": True,
            **(other_params or {}),
        }

        response_container = [None]
        exception_container = [None]
        ready_event = threading.Event()

        def do_request():
            try:
                response_container[0] = requests.post(
                    url,
                    headers=headers,
                    json=payload,
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
            if is_stopped():
                return None, "cancelled"

        if is_stopped():
            return None, "cancelled"

        if exception_container[0]:
            e = exception_container[0]
            logging.error(f"Request failed: {e}")
            return None, f"error_ai_connection_{e}"

        response = response_container[0]

        if not response.ok:
            logging.error(f"HTTP error: {response.status_code} {response.text}")
            return None, f"error_ai_connection_http_{response.status_code}"

        set_status("streaming response...")

        try:
            full_response = []
            for line in response.iter_lines(chunk_size=1):
                if is_stopped():
                    response.close()
                    return None, "cancelled"

                if not line:
                    continue

                text = line.decode("utf-8") if isinstance(line, bytes) else line

                payload_str = text[len("data:") :].strip() if text.startswith("data:") else text

                if payload_str == "[DONE]":
                    break

                try:
                    data = json.loads(payload_str)
                except ValueError as e:
                    logging.error(f"Invalid JSON in response: {e}")
                    return None, f"error_ai_response_format_{e}"

                if "error" in data:
                    logging.error(f"API error: {data['error']}")
                    return None, f"error_ai_response_format_{data['error']}"

                chunk = data.get("choices", [{}])[0].get("delta", {}).get("content") or data.get("message", {}).get(
                    "content"
                )
                if chunk:
                    full_response.append(chunk)

                if data.get("message", {}).get("done"):
                    break

            if not full_response:
                logging.error("Empty response from API")
                return None, "error_ai_response_empty"

            print("".join(full_response))
            set_status(f"done ({len(''.join(full_response))} chars)")
            return "".join(full_response), "ai_response_received"

        except requests.exceptions.RequestException as e:
            if is_stopped():
                return None, "cancelled"
            logging.error(f"Request failed: {e}")
            return None, f"error_ai_connection_{e}"

    @property
    def provider_names_which_work_with_api_method(self) -> list[str]:
        return ["ollama", "openai", "uni", "ollama-laptop"]
