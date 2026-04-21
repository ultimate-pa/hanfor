from flask_socketio import SocketIO

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.threading_ai_socketio import send_ai_update


class ExampleAiAddon(AiAddonAbstractClass):
    # Optional: declare dependencies you need (injected automatically)
    required_dependencies = ["socketio"]

    # Optional: type hints for IDE support (no runtime effect)
    socketio: SocketIO

    @property
    def addon_name(self) -> str:
        return "Example AI addon"

    @property
    def addon_description(self) -> str:
        return "This is an example AI addon"

    @property
    def addon_html(self) -> str:
        # Must match the template path under ui/api/templates/
        return "ai_addons/example_ai_addon.html"

    @property
    def addon_js(self) -> str:
        # Must match the bundle name defined in webpack.config.js
        return "dist/example_ai_addon-bundle.js"

    def _do_initialize(self):
        # Called once automatically when the addon is enabled.
        # Use this to set up state, load data, or connect to services.
        self.global_counter = 0
        self._sid_map = {}  # { sid: count }

    # -------------------------------------------------------------------------
    # sid tracking — needed to send updates to a specific client only
    # -------------------------------------------------------------------------

    @AiAddonAbstractClass.requires_enabled
    def set_sid(self, sid: str):
        self._sid_map[sid] = 0

        send_ai_update(
            {"counter": self.global_counter, "scope": "global"},
            "socket_example_counter",
            self.socketio,
        )

    @AiAddonAbstractClass.requires_enabled
    def clear_sid(self, sid: str):
        self._sid_map.pop(sid, None)

    # -------------------------------------------------------------------------
    # Counter logic
    # -------------------------------------------------------------------------

    @AiAddonAbstractClass.requires_enabled
    def increment_for_client(self, sid: str):
        """Increment a per-client counter and send the update only to that client."""

        current = self._sid_map.get(f"{sid}_counter", 0) + 1
        self._sid_map[f"{sid}_counter"] = current

        send_ai_update(
            {"counter": current, "scope": "private"},
            "socket_example_counter",
            self.socketio,
            sid=sid,
        )

    @AiAddonAbstractClass.requires_enabled
    def increment_for_all(self):
        """Increment the global counter and broadcast the update to all clients."""
        self.global_counter += 1

        send_ai_update(
            {"counter": self.global_counter, "scope": "global"},
            "socket_example_counter",
            self.socketio,
        )
