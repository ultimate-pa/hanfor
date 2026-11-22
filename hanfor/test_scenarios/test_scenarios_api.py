"""Test scenarios of a requirement and global ones, in a table of their own.

A scenario with a requirement_id tests that requirement and is edited in the requirement modal. A global one
(requirement_id "") is checked against all requirements, e.g. "key in the ignition and turned -> engine runs",
and is edited on the page of this blueprint. In the .req file they are
NAME: TestScenario for <RID | ALL>, trace has to hold: (duration, formula), ...
"""

from flask import Blueprint, render_template, request
from flask_restx import Namespace, Resource

from hanfor_flask import current_app, nocache
from lib_core.api_models import (
    ErrorMessageModel,
    SuccessResponseModel,
    TestScenarioImportReportModel,
    TestScenarioListModel,
    TestScenarioRequestModel,
    TestScenarioResponseModel,
    TestScenarioVariablesModel,
)
from lib_core.data import Variable
from lib_core.test_scenario import TestScenario
from lib_core.utils import log_request_response
from requirements.requirements import _SUBTYPE_WRITE_LOCK
from requirements.subtypes import InvalidPayload, SubtypeNotFound, subtype_errors_to_response
from test_scenarios import test_scenarios

BUNDLE_JS = "dist/test_scenarios-bundle.js"
blueprint = Blueprint("test_scenarios", __name__, template_folder="templates", url_prefix="/test_scenarios")
api_ns = Namespace(
    "Test scenarios", "Test scenarios of a requirement and global ones", path="/test_scenarios", ordered=True
)


@blueprint.route("", methods=["GET"])
def index():
    return render_template("test_scenarios/index.html", BUNDLE_JS=BUNDLE_JS)


def _get(scenario_id: int) -> TestScenario:
    scenario = current_app.db.get_objects(TestScenario).get(scenario_id)
    if scenario is None:
        raise SubtypeNotFound(f"Test scenario {scenario_id} not found.")
    return scenario


@api_ns.route("")
@log_request_response
class ApiTestScenarios(Resource):
    @api_ns.doc(
        description="Returns test scenarios, sorted by id.",
        params={
            "requirement_id": "Query param: only the scenarios of this requirement",
            "global": "Query param: true for only the global scenarios",
        },
    )
    @api_ns.response(200, "Success", TestScenarioListModel)
    @nocache
    def get(self):
        scenarios = current_app.db.get_objects(TestScenario).values()
        if request.args.get("global") == "true":
            scenarios = [s for s in scenarios if s.is_global]
        elif "requirement_id" in request.args:
            scenarios = [s for s in scenarios if s.requirement_id == request.args["requirement_id"]]
        return {"success": True, "scenarios": [s.to_dict() for s in sorted(scenarios, key=lambda s: s.id)]}

    @api_ns.doc(description="Creates a test scenario. Without a name it gets TS_<rid | GLOBAL>_<POS | NEG>_<n>.")
    @api_ns.expect(TestScenarioRequestModel)
    @api_ns.response(201, "Created", TestScenarioResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Requirement Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def post(self):
        with _SUBTYPE_WRITE_LOCK:
            scenario = test_scenarios.apply(current_app.db, None, request.get_json(silent=True))
            current_app.db.add_object(scenario)
        return {"success": True, "scenario": scenario.to_dict()}, 201


@api_ns.route("/<int:scenario_id>")
@log_request_response
class ApiTestScenario(Resource):
    @api_ns.doc(description="Returns one test scenario.", params={"scenario_id": "The id of the test scenario"})
    @api_ns.response(200, "Success", TestScenarioResponseModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def get(self, scenario_id: int):
        return {"success": True, "scenario": _get(scenario_id).to_dict()}

    @api_ns.doc(
        description="Changes a test scenario, same body as for creating it. The requirement stays.",
        params={"scenario_id": "The id of the test scenario"},
    )
    @api_ns.expect(TestScenarioRequestModel)
    @api_ns.response(200, "Success", TestScenarioResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def put(self, scenario_id: int):
        with _SUBTYPE_WRITE_LOCK:
            scenario = test_scenarios.apply(current_app.db, _get(scenario_id), request.get_json(silent=True))
            current_app.db.update()
        return {"success": True, "scenario": scenario.to_dict()}

    @api_ns.doc(description="Deletes a test scenario.", params={"scenario_id": "The id of the test scenario"})
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def delete(self, scenario_id: int):
        with _SUBTYPE_WRITE_LOCK:
            current_app.db.remove_object(_get(scenario_id))
        return {"success": True}


@api_ns.route("/variables")
@log_request_response
class ApiTestScenarioVariables(Resource):
    @api_ns.doc(description="The variable names to offer as lanes.")
    @api_ns.response(200, "Success", TestScenarioVariablesModel)
    @nocache
    def get(self):
        return {"success": True, "variables": sorted(v.name for v in current_app.db.get_objects(Variable).values())}


@api_ns.route("/import")
@log_request_response
class ApiTestScenarioImport(Resource):
    @api_ns.doc(
        description="Imports test scenarios, one per line: "
        "NAME: TestScenario for <RID | ALL>, trace has to hold: (duration, formula), ... (the format of the .req "
        "export). ALL makes a global scenario, other lines are ignored.",
        params={
            "file": "The file to import (multipart upload)",
            "replace": "true: overwrite scenarios whose name exists already, otherwise they are skipped",
        },
    )
    @api_ns.response(200, "Success", TestScenarioImportReportModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def post(self):
        upload = request.files.get("file")
        if upload is None:
            raise InvalidPayload("No file uploaded.")
        text = upload.read().decode("utf-8-sig")
        with _SUBTYPE_WRITE_LOCK:
            report = test_scenarios.import_text(current_app.db, text, request.form.get("replace") == "true")
        return {"success": True, **report}
