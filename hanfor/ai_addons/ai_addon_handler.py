from abc import ABC, abstractmethod
import os
import importlib
import logging

from ai_request.ai_core_requests import AiRequest
from thread_handling.threading_core import ThreadHandler


class AiAddonAbstractClass(ABC):
    @property
    @abstractmethod
    def addon_name(self) -> str:
        pass

    @property
    @abstractmethod
    def addon_description(self) -> str:
        pass


class AiAddons:
    def __init__(self, thread_handler: ThreadHandler, ai_request: AiRequest):
        self.__thread_handler = thread_handler
        self.__ai_request = ai_request
        self.__socketio = None
        self.__addons = {}

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

    def get_addons(self):
        return self.__addons

    def __load_all_ai_addons(self):
        """Dynamically loads all AI addons from within addon subfolder."""
        base_directory = os.path.dirname(os.path.abspath(__file__))
        base_package = "ai_addons"

        for directory in os.listdir(base_directory):
            if directory in ["ui", "ai_addon_handler.py", "__pycache__", "threading_ai_socketio.py"]:
                continue

            addon_directory = os.path.join(base_directory, directory)
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
                                print(attr_name)
                                try:
                                    deps = {
                                        k: v for k, v in self.__dependencies.items() if k in attr.required_dependencies
                                    }
                                    instance = attr(**deps)
                                    self.__addons[module_name] = instance
                                except TypeError as e:
                                    logging.warning(f"Cannot instantiate {attr_name}: {e}")
                    except ModuleNotFoundError as e:
                        logging.error(f"Error loading module {module_path}: {e}")
