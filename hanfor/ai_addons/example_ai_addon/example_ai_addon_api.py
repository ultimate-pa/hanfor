from flask import Blueprint
from flask_restx import Namespace, Resource

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.example_ai_addon.example_ai_addon import ExampleAiAddon
from hanfor_flask import current_app


# Blueprint: required for serving addon-specific static files (CSS)
blueprint = Blueprint(
    "example_ai_addon", __name__, static_folder="static", static_url_path="/ai_addons/example_ai_addon/static"
)

# Namespace: REST endpoints with Swagger documentation
example_ai_addon_api_namespace = Namespace(
    "Example AI ADDON", "Example AI ADDON Description", path="/example-ai-addon", ordered=True
)

_handle_disabled = AiAddonAbstractClass.handle_disabled(example_ai_addon_api_namespace)


def _get_addon() -> ExampleAiAddon:
    return current_app.ai_addons.get_addon("example_ai_addon", ExampleAiAddon)


@example_ai_addon_api_namespace.route("/<string:socket_io_sid>")
class ApiExampleAiAddonSocket(Resource):
    @example_ai_addon_api_namespace.response(204, "Success")
    @example_ai_addon_api_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def post(self, socket_io_sid: str):
        _get_addon().set_sid(socket_io_sid)
        return None, 204

    @example_ai_addon_api_namespace.response(204, "Success")
    @example_ai_addon_api_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def delete(self, socket_io_sid: str):
        _get_addon().clear_sid(socket_io_sid)
        return None, 204


@example_ai_addon_api_namespace.route("/increment-client-counter/<string:socket_io_sid>")
class ApiExampleAiAddonCounterClient(Resource):
    @example_ai_addon_api_namespace.response(204, "Success")
    @example_ai_addon_api_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def post(self, socket_io_sid: str):
        _get_addon().increment_for_client(socket_io_sid)
        return None, 204


@example_ai_addon_api_namespace.route("/increment-global-counter")
class ApiExampleAiAddonGlobalCounter(Resource):
    @example_ai_addon_api_namespace.response(204, "Success")
    @example_ai_addon_api_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def post(self):
        _get_addon().increment_global_counter()
        return None, 204
