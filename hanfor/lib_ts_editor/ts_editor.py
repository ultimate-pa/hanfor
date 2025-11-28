import json

from flask import Blueprint, render_template, request
from flask_restx import Resource, Namespace

from lib_core.api_models import TransitionSystemModel
from lib_core.data import TransitionSystem

BUNDLE_JS = "dist/ts_editor-bundle.js"
blueprint = Blueprint("ts-editor", __name__, template_folder="templates", url_prefix="/ts-editor")

api = Namespace("TS Editor", "TS Editor api Description", path="/ts-editor", ordered=True)


@blueprint.route("", methods=["GET"])
def index():
    return render_template(
        "ts-editor/index.html",
        BUNDLE_JS=BUNDLE_JS,
    )


@api.route("/parse")
class ApiParseTransitionSystem(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @api.expect(TransitionSystemModel)
    @api.response(200, "Success")
    @api.response(400, "Bad Request")
    def post(self):
        """Create a new Ultimate job"""
        data = json.loads(request.get_data())
        ts: TransitionSystem = TransitionSystem()
        if ts.parse_from_dict(data):
            return ts.get_hanfor_pl_patterns(), 200
        return None, 400
