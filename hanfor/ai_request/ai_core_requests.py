from threading import Event, Semaphore
from dataclasses import dataclass, field
from typing import Optional, Callable
from ai_request.ai_api_methods_abstract_class import AiApiMethod
from configuration import ai_config

import os
import importlib
import logging
import requests

from thread_handling.threading_core import ThreadHandler, ThreadTask, SchedulingClass, ThreadGroup, TaskResult


@dataclass(slots=True)
class ProviderEntry:
    """Data structure for provider information"""

    maximum_concurrent_api_requests: int
    url: str
    api_key: str
    models: dict[str, str]
    default_model: str
    api_methods: dict[str, AiApiMethod] = field(default_factory=dict)
    semaphore: Semaphore = field(init=False)

    def __post_init__(self):
        self.semaphore = Semaphore(self.maximum_concurrent_api_requests)


class AiCatalogPrinter:
    """Prints AI provider catalog and model check results."""

    def __init__(self, catalog: dict[str, ProviderEntry]):
        self.__catalog = catalog

    def print_catalog(self):
        """Logs all providers with their configuration."""
        lines = ["\n" + "=" * 40]
        for provider, entry in self.__catalog.items():
            lines.append("-" * 40)
            lines.append(f"Provider: {provider}")
            lines.append(f"  max_request    {entry.maximum_concurrent_api_requests}")
            lines.append(f"  Semaphore:     {entry.semaphore}")
            lines.append(f"  URL:           {entry.url}")
            lines.append(f"  API Key:       {entry.api_key[:8]}...")
            lines.append(f"  API Methods:   {', '.join(entry.api_methods.keys()) if entry.api_methods else 'None'}")
            lines.append(f"  Models:")
            for model, description in entry.models.items():
                lines.append(f"    - {model}: {description}")
            lines.append(f"  Default Model: {entry.default_model}")
        lines.append("-" * 40)
        lines.append(f"  Default Provider: {ai_config.DEFAULT_PROVIDER}")
        lines.append("=" * 40)
        logging.info("\n".join(lines))

    @staticmethod
    def print_check_results(results: dict[str, dict[str, dict[str, str]]]):
        """Logs model check results grouped by provider and API method."""
        lines = []
        for provider, methods in results.items():
            lines.append("\n" + "=" * 40)
            lines.append(f"Provider: {provider}")
            for method_name, models in methods.items():
                lines.append(f"  API Method: {method_name}")
                for model, status in models.items():
                    icon = "✓" if status == "ok" else "✗"
                    lines.append(f"    {icon} {model}: {status}")
        lines.append("=" * 40)
        logging.info("\n".join(lines))


class AiCatalogTester:
    """Tests all models of all providers against their registered API methods."""

    def __init__(self, catalog: dict[str, ProviderEntry]):
        self.__catalog = catalog

    def check_all_models(self, stop_event: Event) -> dict[str, dict[str, dict[str, str]]]:
        """Tests every model of every provider with all registered api methods. Returns {provider: {method: {model: status}}}."""
        results = {}
        test_prompt = "Say 'ok'."

        for provider_name, entry in self.__catalog.items():
            if stop_event.is_set():
                break

            results[provider_name] = {}

            if not self.__is_reachable(provider_name, entry, results):
                continue

            if not entry.api_methods:
                results[provider_name]["__no_api_method__"] = {"__no_model__": "error: no api method available"}
                continue

            for method_name, method in entry.api_methods.items():
                if stop_event.is_set():
                    break
                results[provider_name][method_name] = {}
                for model_name in entry.models:
                    if stop_event.is_set():
                        break
                    try:
                        response, status = method.query_api(
                            test_prompt, entry.url, entry.api_key, model_name, None, None
                        )
                        results[provider_name][method_name][model_name] = "ok" if response else f"error: {status}"
                    except Exception as e:
                        results[provider_name][method_name][model_name] = f"error: {e}"

        return results

    @staticmethod
    def __is_reachable(provider_name: str, entry: ProviderEntry, results: dict) -> bool:
        """Returns True if the provider URL is reachable, otherwise writes the error into results."""
        try:
            requests.get(entry.url, timeout=3)
            return True
        except requests.exceptions.ConnectionError:
            results[provider_name]["__unreachable__"] = {
                "__no_model__": f"error: '{provider_name}' is not reachable at {entry.url}"
            }
        except requests.exceptions.Timeout:
            results[provider_name]["__unreachable__"] = {
                "__no_model__": f"error: '{provider_name}' timed out at {entry.url}"
            }
        return False


class AiRequest:
    """Loads and organizes AI providers and routes incoming requests to the correct API method."""

    def __init__(self, thread_handler: ThreadHandler):
        self.__thread_handler = thread_handler
        self.__ai_model_catalog = self.__build_catalog()
        self.__register_api_methods()
        self.__validate_catalog()
        self.__catalog_printer = AiCatalogPrinter(self.__ai_model_catalog)
        self.__catalog_tester = AiCatalogTester(self.__ai_model_catalog)

        self.print_catalog()
        self.__thread_handler.submit(
            ThreadTask(
                self.check_all_models,
                SchedulingClass.SYSTEM_CALL,
                ThreadGroup.AI,
                None,
                self.print_check_results,
                (),
                {},
            )
        )

    def ask_ai(
        self,
        prompt: str,
        callback: Callable,
        scheduling_class: SchedulingClass = SchedulingClass.SYSTEM_CALL,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_method_name: Optional[str] = None,
        other_params: Optional[dict] = None,
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
        )
        return self.__thread_handler.submit(ai_task)

    def get_all_models(self) -> dict[str, ProviderEntry]:
        return dict(self.__ai_model_catalog)

    def check_all_models(self, stop_event: Event) -> dict[str, dict[str, dict[str, str]]]:
        return self.__catalog_tester.check_all_models(stop_event)

    def print_catalog(self) -> None:
        self.__catalog_printer.print_catalog()

    def print_check_results(self, tested_catalog: dict[str, dict[str, dict[str, str]]]):
        self.__catalog_printer.print_check_results(tested_catalog)

    def _resolve_provider(self, provider: Optional[str]) -> str:
        if not provider or provider not in self.__ai_model_catalog:
            if provider:
                logging.warning(f"Provider: {provider} not found, will use: {ai_config.DEFAULT_PROVIDER}")
            provider = ai_config.DEFAULT_PROVIDER
            if provider not in self.__ai_model_catalog:
                raise ValueError(f"Default provider '{ai_config.DEFAULT_PROVIDER}' not found in catalog.")
        return provider

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
        return {provider: ProviderEntry(**data) for provider, data in ai_config.AI_PROVIDERS.items()}

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
