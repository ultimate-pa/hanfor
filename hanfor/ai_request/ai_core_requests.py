import sys
from socket import SocketIO
from threading import Semaphore
from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple

from ai_addons.threading_ai_socketio import send_ai_update
from ai_request.ai_api_methods_abstract_class import AiApiMethod
from configuration import ai_config

import os
import importlib
import logging
import requests

from thread_handling.thread_function_decorator import thread_function, is_stopped, set_status
from thread_handling.threading_core import ThreadHandler, ThreadTask, SchedulingClass, ThreadGroup, TaskResult
from enum import Enum


class TestedActivity(Enum):
    ACTIVE = 0
    NOT_TESTED = 1
    INACTIVE = 2


@dataclass(slots=True)
class ProviderEntry:
    """Data structure for provider information"""

    maximum_concurrent_api_requests: int
    url: str
    api_key: str
    models: dict[str, Tuple[str, TestedActivity]]
    default_model: str
    api_methods: dict[str, AiApiMethod] = field(default_factory=dict)
    activity: TestedActivity = TestedActivity.NOT_TESTED
    semaphore: Semaphore = field(init=False)
    default_provider: bool = False

    def __post_init__(self):
        self.semaphore = Semaphore(self.maximum_concurrent_api_requests)


class AiCatalogTester:
    """Tests all models of all providers against their registered API methods."""

    def check_all_models_activity(self, catalog: dict[str, ProviderEntry]):
        """Tests every model of every provider with all registered api methods."""
        for provider_name, provider_entry in catalog.items():
            if is_stopped():
                print("STOP")
                return
            set_status(f"checking provider: {provider_name}")
            self.activity_test_provider(provider_name, provider_entry)

    def activity_test_provider(self, provider_name: str, provider_entry: ProviderEntry):
        if not self.__is_reachable(provider_entry.url):
            set_status(f"{provider_name}: unreachable")
            provider_entry.activity = TestedActivity.INACTIVE
            for model_name, (desc, activity) in provider_entry.models.items():
                if activity == TestedActivity.ACTIVE:
                    provider_entry.models[model_name] = (desc, TestedActivity.NOT_TESTED)
            return

        provider_entry.activity = TestedActivity.ACTIVE

        if not provider_entry.api_methods:
            provider_entry.activity = TestedActivity.NOT_TESTED
            for model_name, (desc, activity) in provider_entry.models.items():
                provider_entry.models[model_name] = (desc, TestedActivity.NOT_TESTED)
            return

        total = len(provider_entry.models)
        for i, (model_name, (desc, activity)) in enumerate(provider_entry.models.items(), 1):
            if is_stopped():
                print("STOP")
                return
            set_status(f"{provider_name}: testing {model_name} ({i}/{total})")
            self.activity_test_model(model_name, desc, provider_entry)

    @staticmethod
    def activity_test_model(model_name: str, desc: str, provider_entry: ProviderEntry):
        test_prompt = "Say 'ok'."
        if len(provider_entry.api_methods) <= 0:
            provider_entry.models[model_name] = (desc, TestedActivity.INACTIVE)
            return
        for _, method in provider_entry.api_methods.items():
            if is_stopped():
                print("STOP")
                return
            try:
                response, status = method.query_api(
                    test_prompt, provider_entry.url, provider_entry.api_key, model_name, None
                )
                if response:
                    provider_entry.models[model_name] = (desc, TestedActivity.ACTIVE)
                    return
            except Exception:
                pass
        provider_entry.models[model_name] = (desc, TestedActivity.INACTIVE)

    @staticmethod
    def __is_reachable(url: str) -> bool:
        """Returns True if the provider URL is reachable."""
        try:
            requests.get(url, timeout=3)
            return True
        except Exception:
            return False


class AiRequest:
    """Loads and organizes AI providers and routes incoming requests to the correct API method."""

    def __init__(self, thread_handler: ThreadHandler):
        self.__thread_handler = thread_handler
        self.__catalog_tester = AiCatalogTester()
        self.__socketio = None
        self.__ai_model_catalog: dict[str, ProviderEntry] = {}
        self.scan_provider()
        self.test_all_provider_models()

    def scan_provider(self, reload_config: bool = False):
        if reload_config and "configuration.ai_config" in sys.modules:
            importlib.reload(sys.modules["configuration.ai_config"])

        self.__ai_model_catalog = self.__build_catalog()
        self.__register_api_methods()
        self.__validate_catalog()

        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

    def test_all_provider_models(self):
        for _, provider_entry in self.__ai_model_catalog.items():
            provider_entry.activity = TestedActivity.NOT_TESTED
            for model_name, (model_desc, activity) in provider_entry.models.items():
                provider_entry.models[model_name] = (model_desc, TestedActivity.NOT_TESTED)

        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

        self.__thread_handler.submit(
            ThreadTask(
                self.__check_all_models,
                SchedulingClass.SYSTEM_CALL,
                ThreadGroup.AI,
                None,
                None,
                (),
                {},
                info_text="provider/model status check",
            )
        )

    def set_socketio(self, socketio: SocketIO):
        self.__socketio = socketio

    def ask_ai(
        self,
        prompt: str,
        callback: Optional[Callable] = None,
        scheduling_class: SchedulingClass = SchedulingClass.SYSTEM_CALL,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_method_name: Optional[str] = None,
        other_params: Optional[dict] = None,
        info_text: str = "Not Specified",
    ) -> TaskResult:
        """
        Submits an AI query asynchronously. Returns a TaskResult to poll via .done() or block via .result().
        Result is also delivered to the callback.
        """

        provider = self._resolve_provider(provider)
        provider_entry = self.__ai_model_catalog[provider]
        model_name = self._resolve_model(provider_entry, model_name)
        method = self._resolve_method(provider_entry, api_method_name)
        semaphore = provider_entry.semaphore

        ai_task = ThreadTask(
            method.query_api,
            scheduling_class,
            ThreadGroup.AI,
            semaphore,
            callback,
            (
                prompt,
                provider_entry.url,
                provider_entry.api_key,
                model_name,
                other_params,
            ),
            {},
            info_text=f"{info_text} - {provider} | {model_name}",
        )
        return self.__thread_handler.submit(ai_task)

    def ai_model_catalog(self):
        return dict(self.__ai_model_catalog)

    def catalog_to_frontend(self):
        data = {"providers": []}

        for provider_name, entry in self.__ai_model_catalog.items():
            provider_dict = {
                "name": provider_name,
                "default": entry.default_provider,
                "url": entry.url,
                "max_request": entry.maximum_concurrent_api_requests,
                "api_method": ", ".join(entry.api_methods.keys()),
                "reachable": entry.activity.name,
                "models": [],
            }

            for model_name, (desc, activity) in entry.models.items():
                model_dict = {
                    "name": model_name,
                    "desc": desc,
                    "default": model_name == entry.default_model,
                    "active": activity.name,
                }
                provider_dict["models"].append(model_dict)

            data["providers"].append(provider_dict)

        return data

    @thread_function
    def __check_all_models(self):
        self.__catalog_tester.check_all_models_activity(self.__ai_model_catalog)
        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

    def set_default_provider(self, set_provider_name_to_default: str):
        if set_provider_name_to_default in self.__ai_model_catalog:
            for provider_name, entry in self.__ai_model_catalog.items():
                entry.default_provider = provider_name == set_provider_name_to_default
        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

    def set_default_model(self, provider: str, set_model_name_to_default: str):
        if provider in self.__ai_model_catalog:
            if set_model_name_to_default in self.__ai_model_catalog[provider].models:
                self.__ai_model_catalog[provider].default_model = set_model_name_to_default
        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

    def activity_test_provider(self, provider: str):
        if provider in self.__ai_model_catalog:
            self.__catalog_tester.activity_test_provider(provider, self.__ai_model_catalog[provider])

        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

    def activity_test_model(self, provider: str, model_name: str):
        if provider in self.__ai_model_catalog:
            if model_name in self.__ai_model_catalog[provider].models:
                model = self.__ai_model_catalog[provider].models[model_name]
                self.__catalog_tester.activity_test_model(model_name, model[0], self.__ai_model_catalog[provider])
        if self.__socketio:
            send_ai_update(self.catalog_to_frontend(), "socket_provider_info", self.__socketio)

    def _resolve_provider(self, provider: Optional[str]) -> str:
        if provider and provider in self.__ai_model_catalog:
            return provider
        if provider:
            logging.warning(f"Provider '{provider}' not found, using default provider from catalog.")
        for name, entry in self.__ai_model_catalog.items():
            if entry.default_provider:
                return name
        raise ValueError("No default provider defined in AI model catalog.")

    @staticmethod
    def _resolve_model(provider_entry: ProviderEntry, model_name: Optional[str]) -> str:
        if not model_name or model_name not in provider_entry.models:
            if model_name:
                logging.warning(f"Model: {model_name} not found, will use: {provider_entry.default_model}")
            model_name = provider_entry.default_model
            if model_name not in provider_entry.models:
                raise ValueError(f"Default model '{provider_entry.default_model}' not found in catalog.")
        return model_name

    @staticmethod
    def _resolve_method(provider_entry: ProviderEntry, api_method_name: Optional[str]) -> AiApiMethod:
        if not api_method_name or api_method_name not in provider_entry.api_methods:
            if api_method_name:
                logging.warning(f"API method: {api_method_name} not found, will use first available.")
            method = next(iter(provider_entry.api_methods.values()), None)
            if not method:
                raise ValueError(f"No api method available. Check your configuration.")
        else:
            method = provider_entry.api_methods[api_method_name]
        return method

    @staticmethod
    def __build_catalog() -> dict[str, ProviderEntry]:
        """Builds the provider catalog from ai_config."""
        catalog = {}

        for provider, data in ai_config.AI_PROVIDERS.items():
            models = {name: (desc, TestedActivity.NOT_TESTED) for name, desc in data["models"].items()}
            catalog[provider] = ProviderEntry(**{**data, "models": models})
            if ai_config.DEFAULT_PROVIDER == provider:
                catalog[provider].default_provider = True
        return catalog

    @staticmethod
    def __load_ai_api_methods() -> list[tuple[str, AiApiMethod]]:
        """Dynamically loads all AI API method classes from strategies folder."""
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_request_methods/")
        methods = []
        base_package = "ai_request.api_request_methods"

        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module_path = f"{base_package}.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, AiApiMethod) and attr is not AiApiMethod:
                            try:
                                instance = attr()
                                methods.append((module_name, instance))
                            except TypeError as e:
                                logging.warning(f"Cannot instantiate {attr_name} in {module_path}: {e}")
                except ModuleNotFoundError as e:
                    logging.error(f"Error loading module {module_path}: {e}")
        return methods

    def __register_api_methods(self):
        """Assigns loaded API methods to matching providers in the catalog."""
        for name, method in self.__load_ai_api_methods():
            for provider in method.provider_names_which_work_with_api_method:
                if provider not in self.__ai_model_catalog:
                    logging.warning(f"Provider '{provider}' from method '{name}' not found in catalog, skipping.")
                    continue
                self.__ai_model_catalog[provider].api_methods[name] = method

    def __validate_catalog(self):
        """Warns if any provider has no registered API method."""
        for provider, entry in self.__ai_model_catalog.items():
            if not entry.api_methods:
                logging.warning(f"{provider} has no api method to use.")
