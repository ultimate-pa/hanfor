import random
import time
from threading import Event

from engineio import payload
from flask import Blueprint, render_template, jsonify, request

from hanfor_flask import current_app
from lib_core.data import Requirement
from thread_handling.threading_core import ThreadGroup, ThreadTask, SchedulingClass

# Define the main blueprint for rendering the frontend
blueprint = Blueprint("ai_addons", __name__, template_folder="templates", url_prefix="/ai_addons/ui/api/")
# Define the blueprint for the API endpoints
api_blueprint = Blueprint("api_ai_addons", __name__, url_prefix="/api/ai_addons")
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
        for addon_id, addon in current_app.ai_addons.get_addons().items():
            if addon.enabled:
                tab_names.append(addon.addon_name)
                tab_pages.append(addon.addon_html)
                tab_js.append(addon.addon_js)

    tabs = list(zip(tab_names, tab_pages))
    return render_template("ai_addons/index.html", BUNDLE_JS=tab_js, tabs=tabs)


@blueprint.route("/ai_provider_data", methods=["GET"])
def get_ai_provider_data():
    return jsonify(current_app.ai_request.catalog_to_frontend())


@blueprint.route("/ai_addon_data", methods=["GET"])
def get_ai_addon_data():
    send_data = {}
    addons = current_app.ai_addons.get_addons()
    for addon_id, addon in addons.items():

        send_data["addons"] = [
            {
                "id": addon_id,
                "name": addon.addon_name,
                "desc": addon.addon_description,
                "enabled": addon.enabled,
            }
        ]
    return jsonify(send_data)


@blueprint.route("/toggle_addon", methods=["POST"])
def toggle_addon():
    payload = request.json
    id = payload.get("addon")
    current_app.ai_addons.toggle_addon(id)
    return "", 204


@blueprint.route("/set_default_provider", methods=["POST"])
def set_default_provider():
    payload = request.json
    name = payload.get("provider")
    current_app.ai_request.set_default_provider(name)
    return "", 204


@blueprint.route("/set_default_model", methods=["POST"])
def set_default_model():
    payload = request.json
    provider = payload.get("provider")
    model = payload.get("model")
    current_app.ai_request.set_default_model(provider, model)
    return "", 204


@blueprint.route("/test_provider", methods=["POST"])
def activity_test_provider():
    payload = request.json
    provider = payload.get("provider")
    current_app.ai_request.activity_test_provider(provider)
    return "", 204


@blueprint.route("/test_model", methods=["POST"])
def activity_test_model():
    payload = request.json
    provider = payload.get("provider")
    model = payload.get("model")
    current_app.ai_request.activity_test_model(provider, model)
    return "", 204


@blueprint.route("/threading/initial", methods=["GET"])
def threading_data_initial():
    return current_app.thread_handler.threading_data()


@blueprint.route("/threading/stop_group", methods=["POST"])
def threading_stop_group():
    payload = request.json
    group_name = payload.get("group")
    group = ThreadGroup[group_name]
    current_app.thread_handler.stop_group(group)

    return current_app.thread_handler.threading_data()


def _dummy_task(stop_event):
    for i in range(int(random.uniform(2000, 10000))):
        time.sleep(0.001)
        if stop_event.is_set():
            break


@blueprint.route("/threading/dummy_task", methods=["POST"])
def threading_dummy_task():
    task = ThreadTask(
        thread_function=_dummy_task,
        scheduling_class=random.choice(list(SchedulingClass)),
        group=random.choice(list(ThreadGroup)),
        semaphore=None,
        callback=None,
        args=(),
        kwargs={},
    )
    current_app.thread_handler.submit(task)
    return "", 200


@blueprint.route("pattern_prediction/tree", methods=["GET"])
def get_tree():
    pattern_prediction = current_app.ai_addons.get_addons()["pattern_prediction"]
    return jsonify(pattern_prediction.prediction_tree.to_dict(pattern_prediction.prediction_tree.root))


@blueprint.route("pattern_prediction/req_ids", methods=["GET"])
def get_req_ids():
    return jsonify(list(current_app.db.get_objects(Requirement).keys()))


@blueprint.route("pattern_prediction/set_trace_sid", methods=["POST"])
def set_trace_sid():
    payload = request.json
    req_id = payload.get("req_id")
    sid = payload.get("sid")
    pattern_prediction = current_app.ai_addons.get_addons()["pattern_prediction"]
    pattern_prediction.set_sid_for_req(req_id, sid)

    return "", 204


@blueprint.route("pattern_prediction/generate_trace", methods=["POST"])
def generate_trace_for_req():
    payload = request.json
    req_id = payload.get("req_id")
    pattern_prediction = current_app.ai_addons.get_addons()["pattern_prediction"]
    req = current_app.db.get_object(Requirement, req_id).to_dict()
    pattern_prediction.predict_pattern_for_requirement(req["id"], req["desc"], Event())
    return "", 204


@blueprint.route("pattern_prediction/generate_trace_all", methods=["POST"])
def generate_trace_for_req_all():
    pattern_prediction = current_app.ai_addons.get_addons()["pattern_prediction"]
    req = current_app.db.get_objects(Requirement)
    pattern_prediction.predict_patterns_for_all_requirements(req, Event())
    return "", 204


@blueprint.route("pattern_prediction/clear_trace_sid", methods=["POST"])
def clear_trace_sid():
    payload = request.json
    req_id = payload.get("req_id")
    sid = payload.get("sid")
    pattern_prediction = current_app.ai_addons.get_addons()["pattern_prediction"]
    pattern_prediction.clear_sid_for_req(req_id, sid)

    return "", 204
