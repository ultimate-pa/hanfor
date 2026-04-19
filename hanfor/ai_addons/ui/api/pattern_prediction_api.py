from threading import Event
from flask import Blueprint, jsonify, request

from ai_addons.pattern_prediction.pattern_prediction import PatternPrediction
from hanfor_flask import current_app
from lib_core.data import Requirement

pattern_blueprint = Blueprint(
    "ai_addons_pattern_prediction",
    __name__,
    url_prefix="/ai_addons/pattern_prediction",
)


def _get_addon() -> PatternPrediction:
    return current_app.ai_addons.get_addon("pattern_prediction", PatternPrediction)


@pattern_blueprint.route("/tree", methods=["GET"])
def get_tree():
    pp = _get_addon()
    return jsonify(pp.prediction_tree.to_dict(pp.prediction_tree.root))


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


@pattern_blueprint.route("/set_provider", methods=["POST"])
def set_provider():
    _get_addon().set_provider(request.json.get("provider"))
    return "", 204


@pattern_blueprint.route("/set_model", methods=["POST"])
def set_model():
    _get_addon().set_model(request.json.get("model"))
    return "", 204


@pattern_blueprint.route("/get_selected_provider_model", methods=["GET"])
def get_selected_provider_model():
    return jsonify(_get_addon().get_selected_provider_model())


@pattern_blueprint.route("/generate_trace", methods=["POST"])
def generate_trace_for_req():
    req_id = request.json.get("req_id")
    req = current_app.db.get_object(Requirement, req_id).to_dict()
    _get_addon().predict_pattern_for_requirement(req["id"], req["desc"], Event())
    return "", 204


@pattern_blueprint.route("/generate_trace_all", methods=["POST"])
def generate_trace_for_req_all():
    reqs = current_app.db.get_objects(Requirement)
    _get_addon().predict_patterns_for_all_requirements(reqs, Event())
    return "", 204
