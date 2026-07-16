from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.threading_ai_socketio import SendGuiUpdate


class ExampleAiAddon(AiAddonAbstractClass):
    # Optional: declare dependencies you need (injected automatically)
    required_dependencies = ["send_update_threading_and_ai"]

    # Optional: type hints for IDE support (no runtime effect)
    send_update_threading_and_ai: SendGuiUpdate

    @property
    def addon_name(self) -> str:
        return "Example AI addon"

    @property
    def addon_description(self) -> str:
        return "This is an example AI addon"

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

        self.send_update_threading_and_ai.send_ai_update(
            {"counter": self.global_counter, "scope": "global"},
            "socket_example_counter",
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

        current = self._sid_map.get(sid, 0) + 1
        self._sid_map[sid] = current

        self.send_update_threading_and_ai.send_ai_update(
            {"counter": current, "scope": "private"},
            "socket_example_counter",
            sid=sid,
        )

    @AiAddonAbstractClass.requires_enabled
    def increment_global_counter(self):
        """Increment the global counter and broadcast the update to all clients."""
        self.global_counter += 1

        self.send_update_threading_and_ai.send_ai_update(
            {"counter": self.global_counter, "scope": "global"},
            "socket_example_counter",
        )
