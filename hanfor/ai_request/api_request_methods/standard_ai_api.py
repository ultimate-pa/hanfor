import asyncio
import logging
from typing import Optional
import httpx
from ai_request import ai_api_methods_abstract_class
from thread_handling.thread_function_decorator import is_stopped, set_status

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


class OllamaStandard(ai_api_methods_abstract_class.AiApiMethod):

    @staticmethod
    async def do_request(url: str, headers: dict, payload: dict):
        async def _fetch():
            async with httpx.AsyncClient(timeout=120) as client:
                return await client.post(url, headers=headers, json=payload)

        async def _watch():
            while True:
                await asyncio.sleep(0.2)
                if is_stopped():
                    return

        fetch_task = asyncio.create_task(_fetch())
        watch_task = asyncio.create_task(_watch())

        done, _ = await asyncio.wait([fetch_task, watch_task], return_when=asyncio.FIRST_COMPLETED)

        for t in [fetch_task, watch_task]:
            if not t.done():
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass

        if watch_task in done:
            return None, "cancelled"

        try:
            return fetch_task.result(), None
        except Exception as e:
            return None, e

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

        set_status("Wait for a Response")
        response, error = asyncio.run(self.do_request(url, headers, payload))

        if error == "cancelled":
            return None, "cancelled"
        if error:
            logging.error(f"Request failed: {error}")
            return None, f"error_ai_connection_{error}"

        if not response.is_success:
            logging.error(f"HTTP error: {response.status_code} {response.text}")
            return None, f"error_ai_connection_http_{response.status_code}"

        set_status("Parse Response...")

        try:
            data = response.json()
        except Exception as e:
            logging.error(f"Json Response error: {e}")
            return None, f"error_ai_json_parse_{e}"

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
