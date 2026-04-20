from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass


class ExampleAiAddon(AiAddonAbstractClass):
    @property
    def enabled(self) -> bool:
        return self._enabled

    def toggle_addon(self):
        self._enabled = not self._enabled

    @property
    def addon_name(self) -> str:
        return "Example AI addon"

    @property
    def addon_description(self) -> str:
        return "This is an example AI addon"

    @property
    def addon_html(self) -> str:
        return "ai_addons/example_ai_addon.html"

    @property
    def addon_js(self) -> str:
        return "dist/example_ai_addon.js"

    def __init__(self, enabled: bool):
        self._enabled = enabled
