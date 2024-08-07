from typing import Type

from hanfor_flask import current_app
from flask import Blueprint, render_template, request
from flask.views import MethodView

import json


from ultimate.ultimate_connector import UltimateConnector
from ultimate.ultimate_job import UltimateJob
from configuration.ultimate_config import DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION

BUNDLE_JS = "dist/ultimate-bundle.js"
blueprint = Blueprint("ultimate", __name__, template_folder="templates", url_prefix="/ultimate")
api_blueprint = Blueprint("api_ultimate", __name__, url_prefix="/api/ultimate")


@blueprint.route("/", methods=["GET"])
def index():
    return render_template(
        "ultimate/index.html",
        BUNDLE_JS=BUNDLE_JS,
        DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION=DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION,
    )


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view("ultimate_api")
    "version, jobs, configurations, update-all"
    bp.add_url_rule("/<string:command>", defaults={"job_id": None}, view_func=view, methods=["GET"])
    bp.add_url_rule("/job", defaults={}, view_func=view, methods=["POST"])
    bp.add_url_rule("/job/<string:job_id>", defaults={"command": "job"}, view_func=view, methods=["GET", "DELETE"])


class UltimateApi(MethodView):
    def __init__(self):
        self.ultimate = UltimateConnector

    def get(self, command: str, job_id: str) -> dict:
        if command == "version":
            return {"version": self.ultimate.get_version()}
        elif command == "jobs":
            jobs: list[UltimateJob] = get_all_jobs()
            return {"data": [j.get() for j in jobs]}
        elif command == "configurations":
            return self.ultimate.get_ultimate_configurations()
        elif command == "update-all":
            jobs: list[UltimateJob] = get_all_jobs()
            for j in jobs:
                if j.job_status == "scheduled":
                    j.update(self.ultimate.get_job(j.job_id))
                current_app.db.update()
            return {"status": "done"}
        elif command == "job":
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
        else:
            return {"status": "error", "message": "unknown command"}

    def post(self) -> dict:
        data = json.loads(request.get_data())
        job = self.ultimate.start_requirement_job(data["req_file"], data["configuration"], data["req_ids"])
        current_app.db.add_object(job)
        return job.get()

    def delete(self, command: str, job_id: str) -> dict:
        if command == "job":
            return self.ultimate.delete_job(job_id)


def get_all_jobs() -> list[UltimateJob]:
    jobs: list[UltimateJob] = [x for x in current_app.db.get_objects(UltimateJob).values()]
    return jobs


register_api(api_blueprint, UltimateApi)
