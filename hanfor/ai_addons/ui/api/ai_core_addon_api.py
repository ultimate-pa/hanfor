from flask import Blueprint, render_template, jsonify
from hanfor_flask import current_app
from lib_core.data import Requirement

# Define the main blueprint for rendering the frontend
blueprint = Blueprint("ai_addons", __name__, template_folder="templates", url_prefix="/core_ai_addon")
BUNDLE_JS = ["dist/ai_core_addons-bundle.js", "dist/threading-bundle.js"]
TAB_NAMES = ["Threading"]
TAB_PAGES = ["ai_addons/threading.html"]


@blueprint.route("/", methods=["GET"])
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
                tab_names.append(addon.addon_name)
                tab_pages.append(addon.addon_html)
                tab_js.append(addon.addon_js)

    tabs = list(zip(tab_names, tab_pages))
    return render_template("ai_addons/index.html", BUNDLE_JS=tab_js, tabs=tabs)


@blueprint.route("/ai_provider_data", methods=["GET"])
def get_ai_provider_data():
    return jsonify(current_app.ai_request.catalog_to_frontend())


@blueprint.route("/req_ids", methods=["GET"])
def get_req_ids():
    return jsonify(list(current_app.db.get_objects(Requirement).keys()))
