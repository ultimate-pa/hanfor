from http import HTTPStatus

from flask import json, Response, Blueprint
from flask_restx import Namespace, Resource, fields

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.pattern_prediction.pattern_prediction import PatternPrediction
from hanfor_flask import current_app
from json_db_connector.json_db import DatabaseKeyError
from lib_core.data import Requirement
from thread_handling.threading_core import ThreadTask, SchedulingClass, ThreadGroup


blueprint = Blueprint(
    "pattern_prediction", __name__, static_folder="static", static_url_path="/ai_addons/pattern_prediction/static"
)

pattern_prediction_namespace = Namespace(
    "AI Addon: Pattern Prediction", description="Pattern Prediction API", path="/pattern-prediction", ordered=True
)

_handle_disabled = AiAddonAbstractClass.handle_disabled(pattern_prediction_namespace)

# --- Models ---

TRACE_SID_INPUT = pattern_prediction_namespace.model(
    "TraceSidInput",
    {
        "req_id": fields.String(required=True, example="REQ_01"),
        "sid": fields.String(required=True, example="abc123xyz"),
    },
)

ENSEMBLE_ITEM = pattern_prediction_namespace.model(
    "EnsembleItem",
    {
        "id": fields.Integer(required=True, example=1),
        "provider": fields.String(required=True, example="openai"),
        "model": fields.String(required=True, example="gpt-4"),
        "count": fields.Integer(required=True, example=1),
        "weight": fields.Float(required=True, example=1.0),
    },
)

ENSEMBLE_INPUT = pattern_prediction_namespace.model(
    "EnsembleInput",
    {
        "ensemble": fields.List(
            fields.Nested(ENSEMBLE_ITEM),
            required=True,
            example=[{"id": 1, "provider": "openai", "model": "gpt-4", "count": 1, "weight": 1.0}],
        ),
    },
)

REQ_ID_INPUT = pattern_prediction_namespace.model(
    "ReqIdInput",
    {
        "req_id": fields.String(required=True, example="REQ_01"),
    },
)

FILE_INPUT = pattern_prediction_namespace.model(
    "FileInput",
    {
        "file": fields.String(required=True, example="tree_v2.json"),
    },
)


# --- Helpers ---


def _get_addon() -> PatternPrediction:
    return current_app.ai_addons.get_addon("pattern_prediction", PatternPrediction)


# --- API Routes ---


@pattern_prediction_namespace.route("/tree")
class ApiTree(Resource):

    @pattern_prediction_namespace.response(HTTPStatus.OK, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        addon = _get_addon()
        return {"file": addon.get_tree_file_name(), "tree": addon.prediction_tree.to_dict()}


@pattern_prediction_namespace.route("/trace-sid")
class ApiTraceSid(Resource):
    @pattern_prediction_namespace.expect(TRACE_SID_INPUT)
    @pattern_prediction_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        payload = pattern_prediction_namespace.payload
        _get_addon().set_sid_for_req(payload.get("req_id"), payload.get("sid"))
        return None, HTTPStatus.NO_CONTENT

    @pattern_prediction_namespace.expect(TRACE_SID_INPUT)
    @pattern_prediction_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def delete(self):
        payload = pattern_prediction_namespace.payload
        _get_addon().clear_sid_for_req(payload.get("req_id"), payload.get("sid"))
        return None, HTTPStatus.NO_CONTENT


@pattern_prediction_namespace.route("/ensemble")
class ApiEnsemble(Resource):

    @pattern_prediction_namespace.response(HTTPStatus.OK, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        return {"ensemble": _get_addon().get_selected_ensemble()}

    @pattern_prediction_namespace.expect(ENSEMBLE_INPUT)
    @pattern_prediction_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        _get_addon().set_selected_ensemble(pattern_prediction_namespace.payload.get("ensemble"))
        return None, HTTPStatus.NO_CONTENT


@pattern_prediction_namespace.route("/generate-trace/<string:req_id>")
@pattern_prediction_namespace.doc(
    params={"req_id": "Requirement ID to generate trace for. Omit to generate traces for all requirements."}
)
class ApiGenerateTrace(Resource):

    @pattern_prediction_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @pattern_prediction_namespace.response(404, "Requirement ID not found")
    @_handle_disabled
    def post(self, req_id: str):
        if req_id == "__all__":
            reqs = current_app.db.get_objects(Requirement)
            current_app.thread_handler.submit(
                ThreadTask(
                    _get_addon().predict_patterns_for_all_requirements,
                    SchedulingClass.CALLER_DEPTH_1,
                    ThreadGroup("PATTERN_PREDICTION"),
                    None,
                    None,
                    (reqs,),
                    {},
                )
            )
        else:
            try:
                req = current_app.db.get_object(Requirement, req_id).to_dict()
            except DatabaseKeyError:
                pattern_prediction_namespace.abort(404, f"Requirement not found: {req_id}")

            current_app.thread_handler.submit(
                ThreadTask(
                    _get_addon().predict_pattern_for_requirement,
                    SchedulingClass.SYSTEM_CALL,
                    ThreadGroup("PATTERN_PREDICTION"),
                    None,
                    None,
                    (
                        req["id"],
                        req["desc"],
                    ),
                    {},
                    info_text=f"PP for {req["id"]}",
                )
            )
        return None, HTTPStatus.NO_CONTENT


@pattern_prediction_namespace.route("/detailed-traces-file")
class ApiDetailedTracesFile(Resource):

    @pattern_prediction_namespace.response(HTTPStatus.OK, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        traces = _get_addon().get_all_detailed_traces_as_file()
        return Response(
            json.dumps(traces, indent=2, ensure_ascii=False),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=detailed_traces.json"},
        )


@pattern_prediction_namespace.route("/tree-file")
class ApiTreeFile(Resource):

    @pattern_prediction_namespace.response(HTTPStatus.OK, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        return _get_addon().get_all_tree_file()

    @pattern_prediction_namespace.expect(FILE_INPUT)
    @pattern_prediction_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @pattern_prediction_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        _get_addon().select_tree_file(pattern_prediction_namespace.payload.get("file"))
        return None, HTTPStatus.NO_CONTENT
