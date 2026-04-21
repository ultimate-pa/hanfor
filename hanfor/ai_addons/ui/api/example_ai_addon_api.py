from flask import Blueprint, request
from ai_addons.example_ai_addon.example_ai_addon import ExampleAiAddon
from hanfor_flask import current_app

example_ai_addon_blueprint = Blueprint(
    "ai_addons_example_ai_addon",
    __name__,
    url_prefix="/ai_addons/example_ai_addon",
)


def _get_addon():
    return current_app.ai_addons.get_addon("example_ai_addon", ExampleAiAddon)


@example_ai_addon_blueprint.route("/set_sid", methods=["POST"])
def set_sid():
    payload = request.json
    _get_addon().set_sid(payload.get("sid"))
    return "", 204


@example_ai_addon_blueprint.route("/clear_sid", methods=["POST"])
def clear_sid():
    payload = request.json
    _get_addon().clear_sid(payload.get("sid"))
    return "", 204


@example_ai_addon_blueprint.route("/increment_for_client", methods=["POST"])
def increment_for_client():
    payload = request.json
    _get_addon().increment_for_client(payload.get("sid"))
    return "", 204


@example_ai_addon_blueprint.route("/increment_for_all", methods=["POST"])
def increment_for_all():
    _get_addon().increment_for_all()
    return "", 204
