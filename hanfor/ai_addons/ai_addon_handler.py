import os
import importlib
import logging
from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.threading_ai_socketio import send_ai_update
from ai_request.ai_core_requests import AiRequest
from configuration import ai_config
from thread_handling.threading_core import ThreadHandler
from typing import TypeVar, Type

T = TypeVar("T", bound=AiAddonAbstractClass)


class AiAddons:
    def __init__(self, thread_handler: ThreadHandler, ai_request: AiRequest):
        self.__thread_handler = thread_handler
        self.__ai_request = ai_request
        self.__socketio = None
        self.__addons: dict[str, AiAddonAbstractClass] = {}

    @property
    def __dependencies(self):
        return {
            "thread_handler": self.__thread_handler,
            "ai_request": self.__ai_request,
            "socketio": self.__socketio,
        }

    def set_socketio(self, socketio):
        self.__socketio = socketio
        self.__load_all_ai_addons()

    def get_addon(self, addon_id: str, addon_type: Type[T]) -> T:
        return self.__addons[addon_id]

    def get_all_addons(self) -> dict[str, AiAddonAbstractClass]:
        return self.__addons

    def toggle_addon(self, id: str):
        if id in self.__addons.keys():
            self.__addons[id].toggle_addon()
            send_ai_update({}, "reload", self.__socketio)

    def __load_all_ai_addons(self):
        """Dynamically loads all AI addons from within addon subfolder."""
        base_directory = os.path.dirname(os.path.abspath(__file__))
        base_package = "ai_addons"

        for directory in os.listdir(base_directory):

            addon_directory = os.path.join(str(base_directory), str(directory))
            if not os.path.isdir(addon_directory) or directory in ["ui", "__pycache__"]:
                continue

            for filename in os.listdir(addon_directory):
                if filename.endswith(".py") and filename != "__init__.py":
                    module_name = filename[:-3]
                    module_path = f"{base_package}.{directory}.{module_name}"

                    try:
                        module = importlib.import_module(module_path)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)

                            if (
                                isinstance(attr, type)
                                and attr.__name__ != "AiAddonAbstractClass"
                                and any(base.__name__ == "AiAddonAbstractClass" for base in attr.__mro__)
                            ):
                                try:
                                    deps = {
                                        k: v for k, v in self.__dependencies.items() if k in attr.required_dependencies
                                    }
                                    deps["enabled"] = getattr(ai_config, f"ADDON_{module_name.upper()}", False)
                                    instance = attr(**deps)
                                    self.__addons[module_name] = instance
                                except TypeError as e:
                                    logging.warning(f"Cannot instantiate {attr_name}: {e}")
                    except ModuleNotFoundError as e:
                        logging.error(f"Error loading module {module_path}: {e}")
