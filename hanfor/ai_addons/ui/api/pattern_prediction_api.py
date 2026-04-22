from flask import Blueprint, jsonify, request, json, Response

from ai_addons.pattern_prediction.pattern_prediction import PatternPrediction
from hanfor_flask import current_app
from lib_core.data import Requirement
from thread_handling.threading_core import ThreadTask, SchedulingClass, ThreadGroup

pattern_blueprint = Blueprint(
    "ai_addons_pattern_prediction",
    __name__,
    url_prefix="/ai_addons/pattern_prediction",
)


def _get_addon() -> PatternPrediction:
    return current_app.ai_addons.get_addon("pattern_prediction", PatternPrediction)


@pattern_blueprint.route("/tree", methods=["GET"])
def get_tree():
    return jsonify({"file": _get_addon().get_tree_file_name(), "tree": _get_addon().prediction_tree.to_dict()})


@pattern_blueprint.route("/set_trace_sid", methods=["POST"])
def set_trace_sid():
    payload = request.json
    _get_addon().set_sid_for_req(payload.get("req_id"), payload.get("sid"))
    return "", 204


@pattern_blueprint.route("/clear_trace_sid", methods=["POST"])
def clear_trace_sid():
    payload = request.json
    _get_addon().clear_sid_for_req(payload.get("req_id"), payload.get("sid"))
    return "", 204


@pattern_blueprint.route("/set_selected_ensemble", methods=["POST"])
def set_selected_ensemble():
    _get_addon().set_selected_ensemble(request.json.get("ensemble"))
    return "", 204


@pattern_blueprint.route("/get_selected_ensemble", methods=["GET"])
def get_selected_ensemble():
    return jsonify({"ensemble": _get_addon().get_selected_ensemble()})


@pattern_blueprint.route("/generate_trace", methods=["POST"])
def generate_trace_for_req():
    req_id = request.json.get("req_id")
    req = current_app.db.get_object(Requirement, req_id).to_dict()
    current_app.thread_handler.submit(
        ThreadTask(
            _get_addon().predict_pattern_for_requirement,
            SchedulingClass.SYSTEM_CALL,
            ThreadGroup.PATTERN_PREDICTION,
            None,
            None,
            (
                req["id"],
                req["desc"],
            ),
            {},
        )
    )

    return "", 204


@pattern_blueprint.route("/get_all_detailed_traces_as_file", methods=["GET"])
def get_all_detailed_traces_as_file():

    traces = _get_addon().get_all_detailed_traces_as_file()
    return Response(
        json.dumps(traces, indent=2, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=detailed_traces.json"},
    )


@pattern_blueprint.route("/generate_trace_all", methods=["POST"])
def generate_trace_for_req_all():
    reqs = current_app.db.get_objects(Requirement)

    current_app.thread_handler.submit(
        ThreadTask(
            _get_addon().predict_patterns_for_all_requirements,
            SchedulingClass.CALLER_DEPTH_1,
            ThreadGroup.PATTERN_PREDICTION,
            None,
            None,
            (reqs,),
            {},
        )
    )

    return "", 204


@pattern_blueprint.route("/get_all_tree_file", methods=["GET"])
def get_all_tree_file():
    return jsonify(_get_addon().get_all_tree_file())


@pattern_blueprint.route("/select_tree_file", methods=["POST"])
def select_tree_file():
    file = request.json.get("file")
    _get_addon().select_tree_file(file)
    return "", 204
