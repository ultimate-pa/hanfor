from abc import ABC, abstractmethod


class AiApiMethod(ABC):
    @property
    @abstractmethod
    def model_names_which_work_with_api_method(self) -> list[str]:
        """All names of the AI models that work with this API method must be entered in a list here"""
        pass

    @abstractmethod
    def query_api(self, query: str, model_name: str) -> (str, str):
        """
        The API request method.
        It receives the name of the selected model and the question.
        Returns the AI's response together with a status message (response, status).
        """
        pass
