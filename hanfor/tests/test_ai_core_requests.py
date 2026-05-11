from unittest import TestCase
from unittest.mock import MagicMock

from ai_addons.threading_ai_socketio import SendUpdateThreadingAndAi
from thread_handling.threading_core import ThreadHandler
from ai_request.ai_core_requests import AiRequest, AiCatalogTester, TestedActivity, catalog_to_frontend
from configuration import ai_config


class TestAiCoreRequests(TestCase):
    def setUp(self):
        ai_config.AI_PROVIDERS = {
            "TEST_PROVIDER": {
                "maximum_concurrent_api_requests": 4,
                "url": "http://TEST_URL",
                "api_key": "PROVIDER_API_KEY",
                "api_methods_names": ["API_METHOD_NAME"],
                "default_model": "TEST_DEFAULT_MODEL",
                "models": {
                    "TEST_DEFAULT_MODEL": "TEST_DEFAULT_MODEL_DESC",
                    "TEST_MODEL_1": "TEST_MODEL_1_DESC",
                    "TEST_MODEL_2": "TEST_MODEL_2_DESC",
                },
            },
        }
        ai_config.DEFAULT_PROVIDER = "TEST_PROVIDER"
        self.thread_handler = ThreadHandler(SendUpdateThreadingAndAi())
        self.ai_request = AiRequest(self.thread_handler, SendUpdateThreadingAndAi())

    def test_catalog(self):
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].maximum_concurrent_api_requests, 4)
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].url, "http://TEST_URL")
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].api_key, "PROVIDER_API_KEY")
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].default_model, "TEST_DEFAULT_MODEL")
        self.assertEqual(
            self.ai_request.ai_model_catalog()["TEST_PROVIDER"].models,
            {
                "TEST_DEFAULT_MODEL": ("TEST_DEFAULT_MODEL_DESC", TestedActivity.NOT_TESTED),
                "TEST_MODEL_1": ("TEST_MODEL_1_DESC", TestedActivity.NOT_TESTED),
                "TEST_MODEL_2": ("TEST_MODEL_2_DESC", TestedActivity.NOT_TESTED),
            },
        )

    def test_resolve_functions(self):
        self.assertEqual(self.ai_request._resolve_provider("ollama"), "TEST_PROVIDER")
        self.assertEqual(self.ai_request._resolve_provider("TEST_PROVIDER"), "TEST_PROVIDER")
        self.assertEqual(
            self.ai_request._resolve_model(self.ai_request.ai_model_catalog()["TEST_PROVIDER"], "TEST_MODEL_1"),
            "TEST_MODEL_1",
        )
        self.assertEqual(
            self.ai_request._resolve_model(self.ai_request.ai_model_catalog()["TEST_PROVIDER"], "NOT_EXISTING"),
            "TEST_DEFAULT_MODEL",
        )

    def test_resolve_provider_no_default_raises(self):
        ai_config.DEFAULT_PROVIDER = "NONEXISTENT"
        ai_request = AiRequest(self.thread_handler, SendUpdateThreadingAndAi())
        with self.assertRaises(ValueError):
            ai_request._resolve_provider("also_nonexistent")

    def test_resolve_model_missing_default_raises(self):
        catalog = self.ai_request.ai_model_catalog()
        catalog["TEST_PROVIDER"].default_model = "NONEXISTENT"
        with self.assertRaises(ValueError):
            self.ai_request._resolve_model(catalog["TEST_PROVIDER"], "also_nonexistent")

    def test_resolve_method_no_methods_raises(self):
        catalog = self.ai_request.ai_model_catalog()
        catalog["TEST_PROVIDER"].api_methods = {}
        with self.assertRaises(ValueError):
            self.ai_request._resolve_method(catalog["TEST_PROVIDER"], None)

    def test_set_default_provider(self):
        ai_config.AI_PROVIDERS["SECOND_PROVIDER"] = {
            "maximum_concurrent_api_requests": 2,
            "url": "http://OTHER_URL",
            "api_key": "OTHER_KEY",
            "api_methods_names": ["API_METHOD_NAME"],
            "default_model": "OTHER_MODEL",
            "models": {"OTHER_MODEL": "OTHER_MODEL_DESC"},
        }
        ai_request = AiRequest(self.thread_handler, SendUpdateThreadingAndAi())
        ai_request.set_default_provider("SECOND_PROVIDER")
        catalog = ai_request.ai_model_catalog()
        self.assertFalse(catalog["TEST_PROVIDER"].default_provider)
        self.assertTrue(catalog["SECOND_PROVIDER"].default_provider)

    def test_set_default_provider_unknown_ignored(self):
        self.ai_request.set_default_provider("NONEXISTENT")
        self.assertTrue(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].default_provider)

    def test_set_default_model(self):
        self.ai_request.set_default_model("TEST_PROVIDER", "TEST_MODEL_1")
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].default_model, "TEST_MODEL_1")

    def test_set_default_model_unknown_provider_ignored(self):
        self.ai_request.set_default_model("NONEXISTENT", "TEST_MODEL_1")
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].default_model, "TEST_DEFAULT_MODEL")

    def test_set_default_model_unknown_model_ignored(self):
        self.ai_request.set_default_model("TEST_PROVIDER", "NONEXISTENT")
        self.assertEqual(self.ai_request.ai_model_catalog()["TEST_PROVIDER"].default_model, "TEST_DEFAULT_MODEL")

    def test_activity_test_provider_unknown_ignored(self):
        """no task submitted for unknown provider"""
        self.ai_request._AiRequest__thread_handler = MagicMock()
        self.ai_request.activity_test_provider("NONEXISTENT")
        self.ai_request._AiRequest__thread_handler.submit.assert_not_called()

    def test_activity_test_provider_submits_task(self):
        self.ai_request._AiRequest__thread_handler = MagicMock()
        self.ai_request.activity_test_provider("TEST_PROVIDER")
        self.ai_request._AiRequest__thread_handler.submit.assert_called_once()

    def test_activity_test_model_submits_task(self):
        self.ai_request._AiRequest__thread_handler = MagicMock()
        self.ai_request.activity_test_model("TEST_PROVIDER", "TEST_MODEL_1")
        self.ai_request._AiRequest__thread_handler.submit.assert_called_once()

    def test_activity_test_model_unknown_provider_ignored(self):
        self.ai_request._AiRequest__thread_handler = MagicMock()
        self.ai_request.activity_test_model("NONEXISTENT", "TEST_MODEL_1")
        self.ai_request._AiRequest__thread_handler.submit.assert_not_called()

    def test_activity_test_model_unknown_model_ignored(self):
        self.ai_request._AiRequest__thread_handler = MagicMock()
        self.ai_request.activity_test_model("TEST_PROVIDER", "NONEXISTENT")
        self.ai_request._AiRequest__thread_handler.submit.assert_not_called()

    def test_test_all_provider_models_resets_activities(self):
        catalog = self.ai_request.ai_model_catalog()
        catalog["TEST_PROVIDER"].activity = TestedActivity.ACTIVE
        catalog["TEST_PROVIDER"].models["TEST_MODEL_1"] = ("TEST_MODEL_1_DESC", TestedActivity.ACTIVE)
        self.ai_request._AiRequest__thread_handler = MagicMock()

        self.ai_request.test_all_provider_models()

        self.assertEqual(catalog["TEST_PROVIDER"].activity, TestedActivity.NOT_TESTED)
        for _, activity in catalog["TEST_PROVIDER"].models.values():
            self.assertEqual(activity, TestedActivity.NOT_TESTED)

    def test_test_all_provider_models_submits_task(self):
        self.ai_request._AiRequest__thread_handler = MagicMock()
        self.ai_request.test_all_provider_models()
        self.ai_request._AiRequest__thread_handler.submit.assert_called_once()

    def test_ask_ai_submits_task_with_correct_params(self):
        method_mock = MagicMock()
        catalog = self.ai_request.ai_model_catalog()
        catalog["TEST_PROVIDER"].api_methods = {"test_method": method_mock}
        self.ai_request._AiRequest__thread_handler = MagicMock()

        self.ai_request.ask_ai(
            prompt="hello",
            provider="TEST_PROVIDER",
            model_name="TEST_MODEL_1",
            api_method_name="test_method",
        )

        self.ai_request._AiRequest__thread_handler.submit.assert_called_once()
        task = self.ai_request._AiRequest__thread_handler.submit.call_args[0][0]
        self.assertEqual(task.args[0], "hello")
        self.assertEqual(task.args[1], "http://TEST_URL")
        self.assertEqual(task.args[2], "PROVIDER_API_KEY")
        self.assertEqual(task.args[3], "TEST_MODEL_1")


class TestCatalogToFrontend(TestCase):
    def setUp(self):
        ai_config.AI_PROVIDERS = {
            "TEST_PROVIDER": {
                "maximum_concurrent_api_requests": 4,
                "url": "http://TEST_URL",
                "api_key": "PROVIDER_API_KEY",
                "api_methods_names": ["API_METHOD_NAME"],
                "default_model": "TEST_DEFAULT_MODEL",
                "models": {
                    "TEST_DEFAULT_MODEL": "TEST_DEFAULT_MODEL_DESC",
                    "TEST_MODEL_1": "TEST_MODEL_1_DESC",
                },
            },
        }
        ai_config.DEFAULT_PROVIDER = "TEST_PROVIDER"
        self.ai_request = AiRequest(ThreadHandler(SendUpdateThreadingAndAi()), SendUpdateThreadingAndAi())

    def test_frontend_structure(self):
        result = self.ai_request.catalog_to_frontend()
        self.assertIn("providers", result)
        self.assertEqual(len(result["providers"]), 1)
        prov = result["providers"][0]
        self.assertEqual(prov["name"], "TEST_PROVIDER")
        self.assertEqual(prov["url"], "http://TEST_URL")
        self.assertTrue(prov["default"])
        self.assertEqual(prov["reachable"], TestedActivity.NOT_TESTED.name)

    def test_frontend_models(self):
        result = self.ai_request.catalog_to_frontend()
        models = {m["name"]: m for m in result["providers"][0]["models"]}
        self.assertIn("TEST_DEFAULT_MODEL", models)
        self.assertIn("TEST_MODEL_1", models)
        self.assertTrue(models["TEST_DEFAULT_MODEL"]["default"])
        self.assertFalse(models["TEST_MODEL_1"]["default"])
        self.assertEqual(models["TEST_DEFAULT_MODEL"]["active"], TestedActivity.NOT_TESTED.name)

    def test_frontend_empty_catalog(self):
        result = catalog_to_frontend({})
        self.assertEqual(result["providers"], [])


class TestAiCatalogTester(TestCase):
    def _make_tester(self, reachable: bool, task_response=("ok", "200")):
        task_mock = MagicMock()
        task_mock.done.return_value = True
        task_mock.result.return_value = task_response
        ask_ai = MagicMock(return_value=task_mock)

        tester = AiCatalogTester(ask_ai, MagicMock(), MagicMock())
        tester.send_update = MagicMock()
        tester._AiCatalogTester__is_reachable = MagicMock(return_value=reachable)
        return tester, ask_ai

    def _make_catalog(self, api_methods=None, models=None):
        ai_config.AI_PROVIDERS = {
            "TEST_PROVIDER": {
                "maximum_concurrent_api_requests": 4,
                "url": "http://TEST_URL",
                "api_key": "PROVIDER_API_KEY",
                "api_methods_names": ["API_METHOD_NAME"],
                "default_model": "TEST_DEFAULT_MODEL",
                "models": models or {"TEST_DEFAULT_MODEL": "TEST_DEFAULT_MODEL_DESC"},
            }
        }
        ai_config.DEFAULT_PROVIDER = "TEST_PROVIDER"
        ai_request = AiRequest(ThreadHandler(SendUpdateThreadingAndAi()), SendUpdateThreadingAndAi())
        catalog = ai_request.ai_model_catalog()
        if api_methods is not None:
            catalog["TEST_PROVIDER"].api_methods = api_methods
        return catalog

    def test_check_one_model_active_on_success(self):
        tester, _ = self._make_tester(reachable=True, task_response=("ok", "200"))
        catalog = self._make_catalog(api_methods={"method": MagicMock()})
        tester.check_one_model(catalog, "TEST_PROVIDER", "TEST_DEFAULT_MODEL")
        _, activity = catalog["TEST_PROVIDER"].models["TEST_DEFAULT_MODEL"]
        self.assertEqual(activity, TestedActivity.ACTIVE)

    def test_check_one_model_inactive_on_empty_response(self):
        tester, _ = self._make_tester(reachable=True, task_response=(None, "500"))
        catalog = self._make_catalog(api_methods={"method": MagicMock()})
        tester.check_one_model(catalog, "TEST_PROVIDER", "TEST_DEFAULT_MODEL")
        _, activity = catalog["TEST_PROVIDER"].models["TEST_DEFAULT_MODEL"]
        self.assertEqual(activity, TestedActivity.INACTIVE)

    def test_check_one_model_inactive_if_no_api_methods(self):
        tester, ask_ai = self._make_tester(reachable=True)
        catalog = self._make_catalog(api_methods={})
        tester.check_one_model(catalog, "TEST_PROVIDER", "TEST_DEFAULT_MODEL")
        _, activity = catalog["TEST_PROVIDER"].models["TEST_DEFAULT_MODEL"]
        self.assertEqual(activity, TestedActivity.INACTIVE)
        ask_ai.assert_not_called()

    def test_check_one_provider_inactive_if_unreachable(self):
        tester, _ = self._make_tester(reachable=False)
        catalog = self._make_catalog()
        tester.check_one_provider_with_models(catalog, "TEST_PROVIDER")
        self.assertEqual(catalog["TEST_PROVIDER"].activity, TestedActivity.INACTIVE)

    def test_check_one_provider_active_if_reachable(self):
        tester, _ = self._make_tester(reachable=True)
        catalog = self._make_catalog(api_methods={"method": MagicMock()})
        tester.check_one_provider_with_models(catalog, "TEST_PROVIDER")
        self.assertEqual(catalog["TEST_PROVIDER"].activity, TestedActivity.ACTIVE)

    def test_check_one_provider_no_api_methods_skips_model_tests(self):
        tester, ask_ai = self._make_tester(reachable=True)
        catalog = self._make_catalog(api_methods={})
        tester.check_one_provider_with_models(catalog, "TEST_PROVIDER")
        ask_ai.assert_not_called()

    def test_check_one_provider_tests_all_models(self):
        tester, ask_ai = self._make_tester(reachable=True)
        catalog = self._make_catalog(
            api_methods={"method": MagicMock()},
            models={
                "TEST_DEFAULT_MODEL": "DESC",
                "TEST_MODEL_1": "DESC",
                "TEST_MODEL_2": "DESC",
            },
        )
        tester.check_one_provider_with_models(catalog, "TEST_PROVIDER")
        self.assertEqual(ask_ai.call_count, 3)

    def test_unreachable_resets_active_models_to_not_tested(self):
        """ACTIVE models are reset to NOT_TESTED when provider becomes unreachable"""
        tester, _ = self._make_tester(reachable=False)
        catalog = self._make_catalog(
            models={
                "TEST_DEFAULT_MODEL": "DESC",
                "TEST_MODEL_1": "DESC",
            }
        )
        catalog["TEST_PROVIDER"].models["TEST_DEFAULT_MODEL"] = ("DESC", TestedActivity.ACTIVE)
        catalog["TEST_PROVIDER"].models["TEST_MODEL_1"] = ("DESC", TestedActivity.INACTIVE)
        tester.check_one_provider_with_models(catalog, "TEST_PROVIDER")
        _, activity_active = catalog["TEST_PROVIDER"].models["TEST_DEFAULT_MODEL"]
        _, activity_inactive = catalog["TEST_PROVIDER"].models["TEST_MODEL_1"]
        self.assertEqual(activity_active, TestedActivity.NOT_TESTED)
        self.assertEqual(activity_inactive, TestedActivity.INACTIVE)

    def test_send_update_calls_send_ai_update(self):
        send_update_mock = MagicMock()
        tester = AiCatalogTester(MagicMock(), send_update_mock, MagicMock())
        catalog = self._make_catalog()
        tester.send_update(catalog)
        send_update_mock.send_ai_update.assert_called_once()
        args = send_update_mock.send_ai_update.call_args[0]
        self.assertEqual(args[1], "socket_provider_info")
