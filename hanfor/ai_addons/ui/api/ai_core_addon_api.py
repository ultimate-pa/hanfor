import random
import time
from threading import Event
from flask import Blueprint, render_template, jsonify, request

from hanfor_flask import current_app
from lib_core.data import Requirement
from thread_handling.threading_core import ThreadGroup, ThreadTask, SchedulingClass

# Define the main blueprint for rendering the frontend
blueprint = Blueprint("ai_addons", __name__, template_folder="templates", url_prefix="/ai_addons/ui/api/")
# Define the blueprint for the API endpoints
api_blueprint = Blueprint("api_ai_addons", __name__, url_prefix="/api/ai_addons")


@blueprint.route("/", methods=["GET"])
def index():
    BUNDLE_JS = [
        "dist/ai_core_addons-bundle.js",
        "dist/threading-bundle.js",
        "dist/ai-bundle.js",
        "dist/pattern_prediction-bundle.js",
    ]
    tab_names = ["Threading", "AI", "Pattern"]
    tab_pages = ["ai_addons/threading.html", "ai_addons/ai.html", "ai_addons/pattern_prediction.html"]
    tabs = list(zip(tab_names, tab_pages))
    return render_template("ai_addons/index.html", BUNDLE_JS=BUNDLE_JS, tabs=tabs)


def catalog_to_frontend(catalog):
    data = {"providers": []}

    for provider_name, entry in catalog.items():
        provider_dict = {
            "name": provider_name,
            "default": entry.default_provider,
            "url": entry.url,
            "max_request": entry.maximum_concurrent_api_requests,
            "api_method": ", ".join(entry.api_methods.keys()),
            "reachable": entry.activity.name,
            "models": [],
        }

        for model_name, (desc, activity) in entry.models.items():
            model_dict = {
                "name": model_name,
                "desc": desc,
                "default": model_name == entry.default_model,
                "active": activity.name,
            }
            provider_dict["models"].append(model_dict)

        data["providers"].append(provider_dict)

    return data


@blueprint.route("/data", methods=["GET"])
def get_data():
    send_data = catalog_to_frontend(current_app.ai_request.info_for_dashboard())
    send_data["addons"] = [
        {
            "id": "pattern_prediction",
            "name": "Pattern Prediction",
            "desc": "Using a decision tree, a requirement can be assigned to a pattern with the help of an AI.",
            "enabled": True,
        }
    ]
    return jsonify(send_data)


@blueprint.route("/set_default_provider", methods=["POST"])
def set_default_provider():
    payload = request.json
    name = payload.get("provider")
    current_app.ai_request.set_default_provider(name)

    data = catalog_to_frontend(current_app.ai_request.info_for_dashboard())
    return jsonify(data)


@blueprint.route("/set_default_model", methods=["POST"])
def set_default_model():
    payload = request.json
    provider = payload.get("provider")
    model = payload.get("model")
    current_app.ai_request.set_default_model(provider, model)

    data = catalog_to_frontend(current_app.ai_request.info_for_dashboard())
    return jsonify(data)


@blueprint.route("/test_provider", methods=["POST"])
def activity_test_provider():
    payload = request.json
    provider = payload.get("provider")
    current_app.ai_request.activity_test_provider(provider)

    data = catalog_to_frontend(current_app.ai_request.info_for_dashboard())
    return jsonify(data)


@blueprint.route("/test_model", methods=["POST"])
def activity_test_model():
    payload = request.json
    provider = payload.get("provider")
    model = payload.get("model")
    current_app.ai_request.activity_test_model(provider, model)

    data = catalog_to_frontend(current_app.ai_request.info_for_dashboard())
    return jsonify(data)


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
    req = current_app.db.get_object(Requirement, req_id).to_dict()
    pattern_prediction.set_sid_for_req(req_id, sid)
    pattern_prediction.predict_pattern_for_requirement(req["id"], req["desc"], Event())

    return "", 204


@blueprint.route("pattern_prediction/clear_trace_sid", methods=["POST"])
def clear_trace_sid():
    payload = request.json
    req_id = payload.get("req_id")
    sid = payload.get("sid")
    pattern_prediction = current_app.ai_addons.get_addons()["pattern_prediction"]
    pattern_prediction.clear_sid_for_req(req_id, sid)

    return "", 204
