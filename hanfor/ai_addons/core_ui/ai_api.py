from flask_restx import Namespace, Resource, fields
from hanfor_flask import current_app

ai_api_namespace = Namespace("AI", "Dashboard data for AI", path="/ai", ordered=True)

# --- Models ---

AI_ADDON_ITEM = ai_api_namespace.model(
    "AI Addon Item",
    {
        "id": fields.String(description="Addon identifier"),
        "name": fields.String(description="Addon name"),
        "desc": fields.String(description="Addon description"),
        "enabled": fields.Boolean(description="Whether the addon is active"),
    },
)
AI_ADDON_DATA = ai_api_namespace.model("AI Addon Data", {"addons": fields.List(fields.Nested(AI_ADDON_ITEM))})
ADDON_INPUT = ai_api_namespace.model(
    "AddonInput", {"addon_id": fields.String(required=True, description="Addon identifier if action toggle")}
)
ADDON_ACTIONS = ["toggle", "activate_all", "deactivate_all"]

PROVIDER_INPUT = ai_api_namespace.model(
    "ProviderInput", {"provider": fields.String(required=True, description="Provider identifier")}
)
PROVIDER_ACTIONS = ["set_default", "test", "rescan", "test_all"]

PROVIDER_MODEL_INPUT = ai_api_namespace.model(
    "ProviderModelInput",
    {
        "provider": fields.String(required=True, description="Provider identifier"),
        "model": fields.String(required=True, description="Model identifier"),
    },
)
MODEL_ACTIONS = ["set_default", "test"]

# --- API Routes ---


@ai_api_namespace.route("/")
class ApiAiData(Resource):

    @ai_api_namespace.marshal_with(AI_ADDON_DATA, code=200)
    def get(self):
        addons = current_app.ai_addons.get_all_addons()

        return {
            "addons": [
                {
                    "id": addon_id,
                    "name": addon.addon_name,
                    "desc": addon.addon_description,
                    "enabled": addon.enabled,
                }
                for addon_id, addon in addons.items()
            ]
        }


@ai_api_namespace.route("/addon/<action>")
@ai_api_namespace.doc(params={"action": f"One of: {', '.join(ADDON_ACTIONS)}"})
class AddonActions(Resource):
    @ai_api_namespace.expect(ADDON_INPUT)
    @ai_api_namespace.response(204, "Success")
    @ai_api_namespace.response(400, "Unknown action")
    def post(self, action):
        actions = {
            "toggle": current_app.ai_addons.toggle_addon,
            "activate_all": current_app.ai_addons.activate_all_addons,
            "deactivate_all": current_app.ai_addons.deactivate_all_addons,
        }
        if action not in actions:
            ai_api_namespace.abort(400, f"Unknown action: {action}")

        if action == "toggle":
            actions[action](ai_api_namespace.payload.get("addon_id"))
        else:
            actions[action]()
        return None, 204


@ai_api_namespace.route("/provider/<action>")
@ai_api_namespace.doc(params={"action": f"One of: {', '.join(PROVIDER_ACTIONS)}"})
class ProviderActions(Resource):
    @ai_api_namespace.expect(PROVIDER_INPUT)
    @ai_api_namespace.response(204, "Success")
    @ai_api_namespace.response(400, "Unknown action")
    def post(self, action):
        actions = {
            "set_default": current_app.ai_request.set_default_provider,
            "test": current_app.ai_request.activity_test_provider,
            "rescan": lambda _: current_app.ai_request.scan_provider(True),
            "test_all": lambda _: current_app.ai_request.test_all_provider_models(),
        }
        if action not in actions:
            ai_api_namespace.abort(400, f"Unknown action: {action}")
        actions[action](ai_api_namespace.payload.get("provider"))
        return None, 204


@ai_api_namespace.route("/model/<action>")
@ai_api_namespace.doc(params={"action": f"One of: {', '.join(MODEL_ACTIONS)}"})
class ModelActions(Resource):
    @ai_api_namespace.expect(PROVIDER_MODEL_INPUT)
    @ai_api_namespace.response(204, "Success")
    @ai_api_namespace.response(400, "Unknown action")
    def post(self, action):
        actions = {
            "set_default": current_app.ai_request.set_default_model,
            "test": current_app.ai_request.activity_test_model,
        }
        if action not in actions:
            ai_api_namespace.abort(400, f"Unknown action: {action}")
        payload = ai_api_namespace.payload
        actions[action](payload.get("provider"), payload.get("model"))
        return None, 204
