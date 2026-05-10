from flask import Blueprint, render_template
import config
import logging
from hanfor_flask import current_app, HanforFlask
from lib_core.data import Requirement
from flask_restx import Resource, Namespace, fields
from jinja2 import ChoiceLoader, FileSystemLoader, TemplateNotFound
from os import path

core_ai_addon_blueprint = Blueprint(
    "ai_addons",
    __name__,
    template_folder="templates",
    static_folder=path.join(str(path.dirname(__file__)), "static"),
    static_url_path="/ai_addons/core_ui/static",
    url_prefix="/core_ai_addon",
)


BUNDLE_JS = ["dist/ai_core_addons-bundle.js", "dist/threading-bundle.js"]
TAB_NAMES = ["Threading"]
TAB_PAGES = ["ai_addons/threading.html"]

core_ai_addon_api_namespace = Namespace(
    "AI Addon: Core", "Routes for core things for the ai Addon", path="/core-ai-addon", ordered=True
)

# --- Models ---

REQ_IDS = core_ai_addon_api_namespace.model(
    "Requirement Ids", {"ids": fields.List(fields.String, example=["REQ001", "REQ002", "REQ003"])}
)

MODEL_DATA = core_ai_addon_api_namespace.model(
    "Model Data",
    {
        "name": fields.String(description="Model name"),
        "desc": fields.String(description="Model description"),
        "default": fields.Boolean(description="Whether this is the default model"),
        "active": fields.String(description="Model activity status"),
    },
)

PROVIDER_DATA = core_ai_addon_api_namespace.model(
    "Provider Data",
    {
        "name": fields.String(description="Provider name"),
        "default": fields.Boolean(description="Whether this is the default provider"),
        "url": fields.String(description="Provider URL"),
        "max_request": fields.Integer(description="Maximum concurrent API requests"),
        "api_method": fields.String(description="Supported API methods"),
        "reachable": fields.String(description="Provider reachability/activity status"),
        "models": fields.List(fields.Nested(MODEL_DATA), description="Available models"),
    },
)

PROVIDERS_RESPONSE = core_ai_addon_api_namespace.model(
    "Providers Response",
    {
        "providers": fields.List(fields.Nested(PROVIDER_DATA), description="List of providers"),
    },
)

# --- Helpers ---


def register_addon_templates(app: HanforFlask, addons: dict):
    extra_loaders = []
    for addon in addons.values():
        template_folder = addon.get_template_folder()
        if template_folder:
            extra_loaders.append(FileSystemLoader(template_folder))

    if extra_loaders:
        app.jinja_loader = ChoiceLoader([app.jinja_loader] + extra_loaders)


def register_addon_statics(app: HanforFlask, addons: dict):
    for addon_name, addon in addons.items():
        static_folder = addon.get_static_folder()
        if static_folder:
            blueprint = Blueprint(
                f"addon_static_{addon_name}",
                __name__,
                static_folder=static_folder,
                static_url_path=f"/ai_addons/{addon_name}/static",
            )
            app.register_blueprint(blueprint)


# --- API Routes ---


@core_ai_addon_blueprint.route("/", methods=["GET"])
def index():
    tab_names = TAB_NAMES.copy()
    tab_pages = TAB_PAGES.copy()
    tab_js = BUNDLE_JS.copy()
    if current_app.config["FEATURE_AI"]:
        tab_names.append("AI")
        tab_pages.append("ai_addons/ai.html")
        tab_js.append("dist/ai-bundle.js")
        for addon_id, addon in current_app.ai_addons.get_all_addons().items():
            if addon.enabled:
                template_path = addon.addon_html
                js_path = addon.addon_js

                try:
                    current_app.jinja_env.get_template(template_path)
                except TemplateNotFound:
                    logging.warning(f"Addon '{addon_id}': template '{template_path}' not found, skipping.")
                    continue

                js_full_path = path.join(str(current_app.static_folder), js_path)
                if not path.exists(js_full_path):
                    logging.warning(f"Addon '{addon_id}': JS bundle '{js_path}' not found, skipping.")
                    continue

                tab_names.append(addon.addon_name)
                tab_pages.append(template_path)
                tab_js.append(js_path)

    tabs = list(zip(tab_names, tab_pages))
    return render_template("ai_addons/index.html", BUNDLE_JS=tab_js, tabs=tabs, BASE_URL=f"{config.URL_PREFIX}/api/v1")


@core_ai_addon_api_namespace.route("/ai-provider-data")
class CoreAiAddonProviderData(Resource):
    @core_ai_addon_api_namespace.response(200, "Success", PROVIDERS_RESPONSE)
    @core_ai_addon_api_namespace.response(403, "AI is disabled")
    def get(self):
        if current_app.config["FEATURE_AI"]:
            return current_app.ai_request.catalog_to_frontend()
        return 403, "AI is disabled"


@core_ai_addon_api_namespace.route("/req-ids")
class CoreAiAddonReqIds(Resource):
    @core_ai_addon_api_namespace.response(200, "Success", REQ_IDS)
    def get(self):
        return {"ids": list(current_app.db.get_objects(Requirement).keys())}
