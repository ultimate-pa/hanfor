from unittest import TestCase

from thread_handling.threading_core import ThreadHandler
from ai_request.ai_core_requests import AiRequest, ProviderEntry
from configuration import ai_config


class TestAiCoreRequests(TestCase):
    def setUp(self):
        ai_config.AI_PROVIDERS = {
            "TEST_PROVIDER": {
                "maximum_concurrent_api_requests": 4,
                "url": "http://TEST_URL",
                "api_key": "PROVIDER_API_KEY",
                "default_model": "TEST_DEFAULT_MODEL",
                "models": {
                    "TEST_DEFAULT_MODEL": "TEST_DEFAULT_MODEL_DESC",
                    "TEST_MODEL_1": "TEST_MODEL_1_DESC",
                    "TEST_MODEL_2": "TEST_MODEL_2_DESC",
                },
            },
        }
        ai_config.DEFAULT_PROVIDER = "TEST_PROVIDER"
        self.thread_handler = ThreadHandler()
        self.ai_request = AiRequest(self.thread_handler)

    def test_catalog(self):
        self.assertEqual(self.ai_request.get_all_models()["TEST_PROVIDER"].maximum_concurrent_api_requests, 4)
        self.assertEqual(self.ai_request.get_all_models()["TEST_PROVIDER"].url, "http://TEST_URL")
        self.assertEqual(self.ai_request.get_all_models()["TEST_PROVIDER"].api_key, "PROVIDER_API_KEY")
        self.assertEqual(self.ai_request.get_all_models()["TEST_PROVIDER"].default_model, "TEST_DEFAULT_MODEL")

        self.assertEqual(
            self.ai_request.get_all_models()["TEST_PROVIDER"].models,
            {
                "TEST_DEFAULT_MODEL": "TEST_DEFAULT_MODEL_DESC",
                "TEST_MODEL_1": "TEST_MODEL_1_DESC",
                "TEST_MODEL_2": "TEST_MODEL_2_DESC",
            },
        )

    def test_resolve_functions(self):
        self.assertEqual(self.ai_request._resolve_provider("ollama"), "TEST_PROVIDER")
        self.assertEqual(self.ai_request._resolve_provider("TEST_PROVIDER"), "TEST_PROVIDER")
        self.assertEqual(
            self.ai_request._resolve_model(self.ai_request.get_all_models()["TEST_PROVIDER"], "TEST_MODEL_1"),
            "TEST_MODEL_1",
        )
        self.assertEqual(
            self.ai_request._resolve_model(self.ai_request.get_all_models()["TEST_PROVIDER"], "NOT_EXISTING"),
            "TEST_DEFAULT_MODEL",
        )
