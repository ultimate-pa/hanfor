import threading
from abc import ABC, abstractmethod
from typing import Optional

from thread_handling.thread_function_decorator import thread_function


class AiApiMethod(ABC):
    @property
    @abstractmethod
    def provider_names_which_work_with_api_method(self) -> list[str]:
        """All names of the AI models that work with this API method must be entered in a list here"""
        pass

    @thread_function
    @abstractmethod
    def query_api(
        self,
        query: str,
        url: str,
        api_key: str,
        model_name: str,
        other_params: Optional[dict],
    ) -> tuple[str | None, str]:
        """Sends a query to the AI API, returns (response, status)."""
        pass
