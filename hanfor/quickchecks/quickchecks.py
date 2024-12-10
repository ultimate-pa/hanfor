import logging
from typing import Type
from flask import Blueprint, render_template, request, Response
from flask.views import MethodView
from pydantic import BaseModel
from hanfor_flask import current_app
from reqtransformer import Requirement, Variable
from quickchecks.check_poormanscomplete import PoorMansComplete, CompletenessCheckResult, CompletenessCheckOutcome

# Flask: Modular Applications with Blueprints. https://flask.palletsprojects.com/en/2.2.x/blueprints/
# Flask: Method Dispatching and APIs. https://flask.palletsprojects.com/en/2.2.x/views/#method-dispatching-and-apis
# HTTP request methods. https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# Pydantic: Models. https://pydantic-docs.helpmanual.io/usage/models

BUNDLE_JS = "dist/quickchecks-bundle.js"
blueprint = Blueprint("quickchecks", __name__, template_folder="templates", url_prefix="/quickchecks")
api_blueprint = Blueprint("quickchecks_api_completeness", __name__, url_prefix="/api/quickchecks/completeness")


@blueprint.route("/", methods=["GET"])
def index():
    return render_template("quickchecks/index.html", BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view("quickchecks_api")
    bp.add_url_rule("/", defaults={}, view_func=view, methods=["POST"])
    # bp.add_url_rule("/<int:id>", view_func=view, methods=["GET", "PUT", "PATCH", "DELETE"])


class CompletenessCheckApi(MethodView):

    def post(self) -> str | dict | tuple | Response:
        results = self.run_checks()
        return {"data": [[r.var.name, r.outcome.value, r.message] for r in results]}

    def run_checks(self) -> list[CompletenessCheckResult]:
        reqs = list(current_app.db.get_objects(Requirement).values())
        vars = set(current_app.db.get_objects(Variable).values())
        results = PoorMansComplete().run(reqs, vars)
        for result in results:
            if result.outcome == CompletenessCheckOutcome.OK:
                continue
            logging.info(result)
        return results


register_api(api_blueprint, CompletenessCheckApi)
