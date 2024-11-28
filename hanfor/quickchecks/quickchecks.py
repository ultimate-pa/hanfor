from typing import Type
from flask import Blueprint, render_template, request, Response
from flask.views import MethodView
from pydantic import BaseModel
from hanfor_flask import current_app
from reqtransformer import Requirement, Variable
from quickchecks.check_poormanscomplete import PoorMansComplete

# Flask: Modular Applications with Blueprints. https://flask.palletsprojects.com/en/2.2.x/blueprints/
# Flask: Method Dispatching and APIs. https://flask.palletsprojects.com/en/2.2.x/views/#method-dispatching-and-apis
# HTTP request methods. https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# Pydantic: Models. https://pydantic-docs.helpmanual.io/usage/models

BUNDLE_JS = "dist/quickchecks-bundle.js"
blueprint = Blueprint("quickchecks", __name__, template_folder="templates", url_prefix="/quickchecks")
api_blueprint = Blueprint("quickchecks_api", __name__, url_prefix="/api/quickchecks")


@blueprint.route("/", methods=["GET"])
def index():
    return render_template("quickchecks/index.html", BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view("quickchecks_api")
    bp.add_url_rule("/", defaults={"id": None}, view_func=view, methods=["GET"])
    bp.add_url_rule("/", defaults={}, view_func=view, methods=["POST"])
    # bp.add_url_rule("/<int:id>", view_func=view, methods=["GET", "PUT", "PATCH", "DELETE"])


class QuickChecksApi(MethodView):

    # The HTTP POST method sends data to the server. The type of the body of the request is indicated by the
    # Content-Type header.
    def post(self) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            id: int
            data: str

        # request_data = RequestData.parse_obj(request.json)
        reqs = list(current_app.db.get_objects(Requirement).values())
        vars = list(current_app.db.get_objects(Variable).values())
        result = PoorMansComplete()(reqs, vars)
        return "OI"

    def get(self, id: int) -> str | dict | tuple | Response:
        return "OK"


register_api(api_blueprint, QuickChecksApi)
