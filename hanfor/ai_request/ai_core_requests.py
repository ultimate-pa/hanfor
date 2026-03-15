from threading import Event
from dataclasses import dataclass, field
from typing import Optional
from ai_request.ai_api_methods_abstract_class import AiApiMethod
from configuration import ai_config

import os
import importlib
import logging
import requests


@dataclass(slots=True)
class ProviderEntry:
    url: str
    api_key: str
    models: dict[str, str]
    default_model: str
    api_methods: dict[str, AiApiMethod] = field(default_factory=dict)


class AiCatalogPrinter:
    def __init__(self, catalog: dict[str, ProviderEntry]):
        self.__catalog = catalog

    def print_catalog(self):
        print(f"{'='*40}")
        for provider, entry in self.__catalog.items():
            print(f"{'-'*40}")
            print(f"Provider: {provider}")
            print(f"  URL:           {entry.url}")
            print(f"  API Key:       {entry.api_key[:8]}...")
            print(f"  API Methods:   {', '.join(entry.api_methods.keys()) if entry.api_methods else 'None'}")
            print(f"  Models:")
            for model, description in entry.models.items():
                print(f"    - {model}: {description}")
            print(f"  Default Model: {entry.default_model}")
        print(f"{'-'*40}")
        print(f"  Default Provider: {ai_config.DEFAULT_PROVIDER}")
        print(f"{'='*40}")

    @staticmethod
    def print_check_results(results: dict[str, dict[str, dict[str, str]]]):
        for provider, methods in results.items():
            print(f"\n{'='*40}")
            print(f"Provider: {provider}")
            for method_name, models in methods.items():
                print(f"  API Method: {method_name}")
                for model, status in models.items():
                    icon = "✓" if status == "ok" else "✗"
                    print(f"    {icon} {model}: {status}")
        print(f"{'='*40}")


class AiCatalogTester:

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

    def __init__(self):
        self.__ai_model_catalog = self.__build_catalog()
        self.__register_api_methods()
        self.__validate_catalog()
        self.__catalog_printer = AiCatalogPrinter(self.__ai_model_catalog)
        self.__catalog_tester = AiCatalogTester(self.__ai_model_catalog)

    def ask_ai(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_method_name: Optional[str] = None,
        other_params: Optional[dict] = None,
        stop_event: Optional[Event] = None,
    ) -> tuple[str | None, str]:
        """returns the ai_response and the status"""

        if not provider or provider not in self.__ai_model_catalog:
            if provider:
                logging.warning(f"Provider: {provider} not found, will use: {ai_config.DEFAULT_PROVIDER}")
            provider = ai_config.DEFAULT_PROVIDER
            if provider not in self.__ai_model_catalog:
                raise ValueError(
                    f"Default provider '{ai_config.DEFAULT_PROVIDER}' not found in catalog. Check your configuration."
                )

        provider_entry = self.__ai_model_catalog[provider]

        if not model_name or model_name not in provider_entry.models:
            if model_name:
                logging.warning(f"Model: {model_name} not found, will use: {provider_entry.default_model}")
            model_name = provider_entry.default_model
            if model_name not in provider_entry.models:
                raise ValueError(
                    f"Default model '{provider_entry.default_model}' of provider '{provider}' not found in catalog. Check your configuration."
                )

        if not api_method_name or api_method_name not in provider_entry.api_methods:
            if api_method_name:
                logging.warning(f"API method: {api_method_name} not found, will use first available.")
            method = next(iter(provider_entry.api_methods.values()), None)
            if not method:
                raise ValueError(f"No api method available for provider '{provider}'. Check your configuration.")
        else:
            method = provider_entry.api_methods[api_method_name]

        return method.query_api(
            prompt, provider_entry.url, provider_entry.api_key, model_name, other_params, stop_event
        )

    def get_all_models(self) -> dict[str, ProviderEntry]:
        return dict(self.__ai_model_catalog)

    def check_all_models(self, stop_event: Event) -> dict[str, dict[str, dict[str, str]]]:
        return self.__catalog_tester.check_all_models(stop_event)

    def print_catalog(self):
        self.__catalog_printer.print_catalog()

    def print_check_results(self, tested_catalog: dict[str, dict[str, dict[str, str]]]):
        self.__catalog_printer.print_check_results(tested_catalog)

    @staticmethod
    def __build_catalog() -> dict[str, ProviderEntry]:
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
        for name, method in self.__load_ai_api_methods():
            for provider in method.provider_names_which_work_with_api_method:
                if provider not in self.__ai_model_catalog:
                    logging.warning(f"Provider '{provider}' from method '{name}' not found in catalog, skipping.")
                    continue
                self.__ai_model_catalog[provider].api_methods[name] = method

    def __validate_catalog(self):
        for provider, entry in self.__ai_model_catalog.items():
            if not entry.api_methods:
                logging.warning(f"{provider} has no api method to use.")
