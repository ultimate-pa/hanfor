from dataclasses import dataclass, field
from datetime import datetime
from typing import Type
from flask import Blueprint, render_template, Response
from flask.views import MethodView
from hanfor_flask import current_app
from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField
from quickchecks.check_poormanscomplete import PoorMansComplete, CompletenessCheckResult, CompletenessCheckOutcome
from lib_core.data import Variable, Requirement


BUNDLE_JS = "dist/quickchecks-bundle.js"
blueprint = Blueprint("quickchecks", __name__, template_folder="templates", url_prefix="/quickchecks")
api_blueprint = Blueprint("quickchecks_api", __name__, url_prefix="/api/quickchecks")


@DatabaseTable(TableType.Folder)
@DatabaseID("check_id", str)
@DatabaseField("check_name", str)
@DatabaseField("results", list[dict])
@DatabaseField("start_time", datetime)
@DatabaseField("last_update", datetime)
@dataclass(kw_only=True)
class QuickcheckTask:
    check_id: str
    check_name: str
    results: list = field(default_factory=list)
    start_time: datetime
    last_update: datetime


@blueprint.route("/", methods=["GET"])
def index():
    return render_template("quickchecks/index.html", BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view("quickchecks_api")
    bp.add_url_rule("/", defaults={}, view_func=view, methods=["GET", "POST"])


class QuickcheckApi(MethodView):

    def post(self) -> str | dict | tuple | Response:
        if current_app.db.key_in_table(QuickcheckTask, PoorMansComplete.CHECK_ID):
            r = current_app.db.get_object(QuickcheckTask, PoorMansComplete.CHECK_ID)
        else:
            r = QuickcheckTask(
                check_id=PoorMansComplete.CHECK_ID,
                check_name=PoorMansComplete.CHECK_ID,
                start_time=datetime.now(),
                last_update=datetime.now(),
            )
        current_app.db.add_object(r)
        r.results = self.run_checks()
        r.last_updated = datetime.now()
        current_app.db.update()
        return "ok"

    @staticmethod
    def run_checks() -> list[CompletenessCheckResult]:
        reqs = list(current_app.db.get_objects(Requirement).values())
        variables = set(current_app.db.get_objects(Variable).values())
        results = PoorMansComplete().run(reqs, variables)
        for result in results:
            if result.outcome == CompletenessCheckOutcome.OK:
                continue
        return results


def register_api_results(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view("quickchecks_api_results")
    bp.add_url_rule("/results", defaults={}, view_func=view, methods=["GET"])


class QuickChecksResultApi(MethodView):

    @staticmethod
    def get() -> list:
        data = []
        for key, check in current_app.db.get_objects(QuickcheckTask).items():
            for r in check.results:
                data.append([r.var, check.check_name, r.outcome, r.message])
        return data


register_api(api_blueprint, QuickcheckApi)
register_api_results(api_blueprint, QuickChecksResultApi)
