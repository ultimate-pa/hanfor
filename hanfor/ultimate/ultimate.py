import json

from hanfor_flask import current_app
from flask import Blueprint, render_template, request
from flask_restx import Resource, Namespace
from lib_core.api_models import (
    UltimateJobsModel,
    UltimateConfigurationsModel,
    UltimateJobModel,
    UltimateJobRequestModel,
    UltimateVersionModel,
)

from ultimate.ultimate_connector import UltimateConnector
from ultimate.ultimate_job import UltimateJob
from configuration.ultimate_config import DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION

BUNDLE_JS = "dist/ultimate-bundle.js"
blueprint = Blueprint("ultimate", __name__, template_folder="templates", url_prefix="/ultimate")

api = Namespace("Ultimate", "Ultimate api Description", path="/ultimate", ordered=True)


@blueprint.route("/", methods=["GET"])
def index():
    return render_template(
        "ultimate/index.html",
        BUNDLE_JS=BUNDLE_JS,
        DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION=DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION,
    )


@api.route("/version")
class ApiUltimateVersion(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultimate = UltimateConnector

    # @api.doc(summary="Get version of the ultimate backend")
    @api.response(200, "Success", UltimateVersionModel)
    def get(self):
        """Get version of the ultimate backend"""
        return {"version": self.ultimate.get_version()}, 200


@api.route("/configurations")
class ApiUltimateConfigurations(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultimate = UltimateConnector

    @api.response(200, "Success", UltimateConfigurationsModel)
    def get(self):
        """Get available ultimate configuration settings"""
        return self.ultimate.get_ultimate_configurations()


@api.route("/update-all")
class ApiUltimateUpdateAll(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultimate = UltimateConnector

    def post(self):
        """Update all Ultimate jobs"""
        jobs: list[UltimateJob] = get_all_jobs()
        for j in jobs:
            if j.job_status == "scheduled":
                j.update(self.ultimate.get_job(j.job_id))
            current_app.db.update()
        return {"status": "done"}


@api.route("/jobs")
class ApiUltimateJobs(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultimate = UltimateConnector

    @staticmethod
    @api.response(200, "Success", UltimateJobsModel)
    def get():
        """Get a list of all Ultimate jobs"""
        jobs: list[UltimateJob] = get_all_jobs()
        return {"data": [j.get() for j in jobs]}

    @api.expect(UltimateJobRequestModel)
    @api.response(200, "Success", UltimateJobModel)
    def post(self):
        """Create a new Ultimate job"""
        data = json.loads(request.get_data())
        job = self.ultimate.start_requirement_job(data["req_file"], data["configuration"], data["req_ids"])
        current_app.db.add_object(job)
        return job.get()


@api.route("/jobs/<string:job_id>")
class ApiUltimateJob(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultimate = UltimateConnector

    @api.doc(
        params={
            "job_id": {"description": "The ID of the Ultimate job", "required": True},
            "download": {"description": "Download flag", "required": False, "in": "query", "type": "boolean"},
        }
    )
    @api.response(200, "Success", UltimateJobModel)
    def get(self, job_id: str):
        """Get an Ultimate Job"""
        download = request.args.get("download", default=False, type=bool)
        job = current_app.db.get_object(UltimateJob, job_id)
        if job.job_status == "done":
            pass
        elif job.job_status == "scheduled":
            job.update(self.ultimate.get_job(job_id))
            current_app.db.update()
        else:
            pass
        if download:
            return job.get_download()
        return job.get()


@api.route("/jobs/<string:job_id>/abort")
class ApiUltimateUpdateAll(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultimate = UltimateConnector

    @api.doc(params={"job_id": {"description": "The ID of the Ultimate job", "required": True, "in": "path"}})
    def post(self, job_id: str):
        """Abort a running Ultimate job"""
        return self.ultimate.abort_job(job_id)


def get_all_jobs() -> list[UltimateJob]:
    jobs: list[UltimateJob] = [x for x in current_app.db.get_objects(UltimateJob).values()]
    return jobs
