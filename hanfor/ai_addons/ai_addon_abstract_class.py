from abc import ABC, abstractmethod
from functools import wraps
import os
import inspect
from http import HTTPStatus


class AiAddonAbstractClass(ABC):

    class AddonDisabledError(Exception):
        pass

    # -------------------------------------------------------------------------
    # Decorator
    # -------------------------------------------------------------------------

    @staticmethod
    def requires_enabled(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.enabled:
                raise AiAddonAbstractClass.AddonDisabledError()
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def handle_disabled(namespace):
        """Factory that returns a decorator bound to the given namespace."""

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except AiAddonAbstractClass.AddonDisabledError:
                    namespace.abort(HTTPStatus.FORBIDDEN, "Addon is disabled")

            return wrapper

        return decorator

    # -------------------------------------------------------------------------
    # Autodetect properties
    # -------------------------------------------------------------------------

    _addon_static_folder: str = None
    _addon_template_folder: str = None

    def normalize_addon_name(self) -> str:
        return self.addon_name.lower().replace(" ", "_")

    @property
    def addon_html(self) -> str:
        return f"ai_addons/{self.normalize_addon_name()}.html"

    @property
    def addon_js(self) -> str:
        # Convention: dist/<addon_name>-bundle.js
        return f"dist/{self.normalize_addon_name()}-bundle.js"

    @classmethod
    def get_template_folder(cls) -> str | None:
        """Returns the addon template folder."""
        addon_dir = os.path.dirname(inspect.getfile(cls))
        template_path = os.path.join(addon_dir, "templates")
        return template_path if os.path.isdir(template_path) else None

    @classmethod
    def get_static_folder(cls) -> str | None:
        """Returns the addon static folder."""
        addon_dir = os.path.dirname(inspect.getfile(cls))
        static_path = os.path.join(addon_dir, "static")
        return static_path if os.path.isdir(static_path) else None

    # -------------------------------------------------------------------------
    # Abstract properties
    # -------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    @abstractmethod
    def addon_name(self) -> str:
        pass

    @property
    @abstractmethod
    def addon_description(self) -> str:
        pass

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    # Subclasses declare their required dependency names here.
    required_dependencies: list[str] = []

    # Lifecycle
    def __init__(self, enabled: bool, **kwargs):
        self._enabled = enabled
        self._initialized: bool = False
        self._resolve_dependencies(kwargs)
        self.initialize()

    def toggle_addon(self):
        """Toggles the addon on/off and triggers initialization when enabled."""
        self._enabled = not self._enabled
        self.initialize()

    def initialize(self):
        """Calls _do_initialize() once while the addon is enabled."""
        if not self.enabled or self._initialized:
            return
        self._do_initialize()
        self._initialized = True

    @abstractmethod
    def _do_initialize(self):
        """Subclass-specific initialization logic."""
        pass

    # Internal helpers
    def _resolve_dependencies(self, kwargs: dict):
        """Validates and injects all declared dependencies as instance attributes."""
        for dep in self.required_dependencies:
            if dep not in kwargs:
                raise ValueError(f"Missing required dependency: '{dep}'")
            setattr(self, dep, kwargs[dep])
