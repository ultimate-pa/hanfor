from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from ai_addons.example_ai_addon.example_ai_addon import ExampleAiAddon
from hanfor_flask import current_app

example_ai_addon_blueprint = Blueprint(
    "ai_addons_example_ai_addon",
    __name__,
    url_prefix="/ai_addons/example_ai_addon",
)

example_ai_addon_api_namespace = Namespace(
    "Example AI ADDON", "Example AI ADDON Description", path="/example-ai-addon", ordered=True
)


def _get_addon():
    return current_app.ai_addons.get_addon("example_ai_addon", ExampleAiAddon)


@example_ai_addon_api_namespace.route("/<string:socket_io_sid>")
class ApiExampleAiAddonSocket(Resource):
    @example_ai_addon_api_namespace.response(204, "Success")
    def post(self, socket_io_sid: str):
        _get_addon().set_sid(socket_io_sid)
        return None, 204

    @example_ai_addon_api_namespace.response(204, "Success")
    def delete(self, socket_io_sid: str):
        _get_addon().clear_sid(socket_io_sid)
        return None, 204


@example_ai_addon_api_namespace.route("/increment-client-counter/<string:socket_io_sid>")
class ApiExampleAiAddonCounterClient(Resource):
    @example_ai_addon_api_namespace.response(204, "Success")
    def post(self, socket_io_sid: str):
        _get_addon().increment_for_client(socket_io_sid)
        return None, 204


@example_ai_addon_api_namespace.route("/increment-global-counter")
class ApiExampleAiAddonGlobalCounter(Resource):
    @example_ai_addon_api_namespace.response(204, "Success")
    def post(self):
        _get_addon().increment_global_counter()
        return None, 204
