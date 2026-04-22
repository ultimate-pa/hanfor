import os
import importlib
import logging
from socket import SocketIO

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.threading_ai_socketio import send_ai_update
from ai_request.ai_core_requests import AiRequest
from configuration import ai_config
from thread_handling.threading_core import ThreadHandler
from typing import TypeVar, Type

T = TypeVar("T", bound=AiAddonAbstractClass)


class AiAddons:
    """Registry for all AI addons. Handles loading, access, and toggling"""

    def __init__(self, thread_handler: ThreadHandler, ai_request: AiRequest):
        self.__thread_handler = thread_handler
        self.__ai_request = ai_request
        self.__socket_io = None
        self.__addons: dict[str, AiAddonAbstractClass] = {}

    @property
    def __dependencies(self) -> dict[str, object]:
        """Shared dependencies injected into each addon on instantiation"""
        return {
            "thread_handler": self.__thread_handler,
            "ai_request": self.__ai_request,
            "socketio": self.__socket_io,
        }

    def set_socketio(self, socket_io: SocketIO):
        """Set the SocketIO instance and trigger addon loading"""
        self.__socket_io = socket_io
        self.__load_all_ai_addons()

    def get_addon(self, addon_id: str, addon_type: Type[T]) -> T:
        """Return a specific addon by ID"""
        return self.__addons[addon_id]

    def get_all_addons(self) -> dict[str, AiAddonAbstractClass]:
        """Return all loaded addons"""
        return self.__addons

    def toggle_addon(self, addon_id: str):
        """Toggle an addon on/off and notify the frontend to reload."""
        if addon_id in self.__addons.keys():
            self.__addons[addon_id].toggle_addon()
            send_ai_update({}, "reload", self.__socket_io)

    def __load_all_ai_addons(self):
        """Dynamically discover and instantiate all addons in subdirectories."""
        base_directory = os.path.dirname(os.path.abspath(__file__))
        base_package = "ai_addons"
        non_ai_addon_folders = ["ui", "__pycache__"]

        for directory in os.listdir(base_directory):

            addon_directory = os.path.join(str(base_directory), str(directory))
            if not os.path.isdir(addon_directory) or directory in non_ai_addon_folders:
                continue

            # looks through every subfolder
            for filename in os.listdir(addon_directory):
                if filename.endswith(".py") and filename != "__init__.py":
                    module_name = filename[:-3]
                    module_path = f"{base_package}.{directory}.{module_name}"

                    try:
                        module = importlib.import_module(module_path)

                        # Find concrete AiAddonAbstractClass subclasses in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)

                            if (
                                isinstance(attr, type)
                                and attr.__name__ != "AiAddonAbstractClass"
                                and any(base.__name__ == "AiAddonAbstractClass" for base in attr.__mro__)
                            ):
                                try:
                                    # Inject only dependencies the addon declares
                                    deps = {
                                        k: v for k, v in self.__dependencies.items() if k in attr.required_dependencies
                                    }

                                    # Read enabled state from config, warn if missing
                                    enabled = getattr(ai_config, f"ADDON_{module_name.upper()}", None)
                                    if enabled is None:
                                        logging.warning(
                                            f"No config entry for ADDON_{module_name.upper()}, defaulting to disabled."
                                        )
                                        enabled = False
                                    deps["enabled"] = enabled

                                    # instantiates addon
                                    instance = attr(**deps)
                                    self.__addons[module_name] = instance

                                except TypeError as e:
                                    logging.warning(f"Cannot instantiate {attr_name}: {e}")
                    except ModuleNotFoundError as e:
                        logging.error(f"Error loading module {module_path}: {e}")

    def activate_all_addons(self):
        for addon_id, instance in self.__addons.items():
            if not instance.enabled:
                self.toggle_addon(addon_id)

    def deactivate_all_addons(self):
        for addon_id, instance in self.__addons.items():
            if instance.enabled:
                self.toggle_addon(addon_id)
