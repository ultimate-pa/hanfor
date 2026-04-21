from abc import ABC, abstractmethod
from functools import wraps


class AiAddonAbstractClass(ABC):

    # -------------------------------------------------------------------------
    # Decorator
    # -------------------------------------------------------------------------

    @staticmethod
    def requires_enabled(func):
        """Returns None if the addon is disabled."""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.enabled:
                return None
            return func(self, *args, **kwargs)

        return wrapper

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

    @property
    @abstractmethod
    def addon_html(self) -> str:
        pass

    @property
    @abstractmethod
    def addon_js(self) -> str:
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
