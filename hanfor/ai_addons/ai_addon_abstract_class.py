from abc import abstractmethod, ABC
from functools import wraps


class AiAddonAbstractClass(ABC):

    @staticmethod
    def requires_enabled(func):
        """Decorator, returns None if the addon is disabled"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.enabled:
                return None
            return func(self, *args, **kwargs)

        return wrapper

    @property
    @abstractmethod
    def enabled(self) -> bool:
        pass

    @abstractmethod
    def toggle_addon(self):
        pass

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
