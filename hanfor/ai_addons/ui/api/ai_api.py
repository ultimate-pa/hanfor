from flask import Blueprint, jsonify, request
from hanfor_flask import current_app

ai_blueprint = Blueprint(
    "ai",
    __name__,
    url_prefix="/ai",
)


@ai_blueprint.route("/ai_addon_data", methods=["GET"])
def get_ai_addon_data():
    send_data = {}
    addons = current_app.ai_addons.get_all_addons()

    send_data["addons"] = [
        {
            "id": addon_id,
            "name": addon.addon_name,
            "desc": addon.addon_description,
            "enabled": addon.enabled,
        }
        for addon_id, addon in addons.items()
    ]
    return jsonify(send_data)


@ai_blueprint.route("/toggle_addon", methods=["POST"])
def toggle_addon():
    current_app.ai_addons.toggle_addon(request.json.get("addon"))
    return "", 204


@ai_blueprint.route("/set_default_provider", methods=["POST"])
def set_default_provider():
    current_app.ai_request.set_default_provider(request.json.get("provider"))
    return "", 204


@ai_blueprint.route("/set_default_model", methods=["POST"])
def set_default_model():
    payload = request.json
    current_app.ai_request.set_default_model(payload.get("provider"), payload.get("model"))
    return "", 204


@ai_blueprint.route("/test_provider", methods=["POST"])
def activity_test_provider():
    current_app.ai_request.activity_test_provider(request.json.get("provider"))
    return "", 204


@ai_blueprint.route("/test_model", methods=["POST"])
def activity_test_model():
    payload = request.json
    current_app.ai_request.activity_test_model(payload.get("provider"), payload.get("model"))
    return "", 204


@ai_blueprint.route("/rescan_provider", methods=["POST"])
def rescan_provider():
    current_app.ai_request.scan_provider()
    return "", 204


@ai_blueprint.route("/test_all_provider", methods=["POST"])
def test_all_provider():
    current_app.ai_request.test_all_provider_models()
    return "", 204


@ai_blueprint.route("/activate_all_addons", methods=["POST"])
def activate_all_addons():
    current_app.ai_addons.activate_all_addons()
    return "", 204


@ai_blueprint.route("/deactivate_all_addons", methods=["POST"])
def deactivate_all_addons():
    current_app.ai_addons.deactivate_all_addons()
    return "", 204
