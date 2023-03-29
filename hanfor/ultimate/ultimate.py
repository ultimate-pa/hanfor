from os import path, mkdir
from typing import Type

from flask import Blueprint, render_template, request, current_app
from flask.views import MethodView

from static_utils import get_filenames_from_dir

from ultimate.ultimate_connector import UltimateConnector
from ultimate.ultimate_job import UltimateJob

BUNDLE_JS = 'dist/ultimate-bundle.js'
blueprint = Blueprint('ultimate', __name__, template_folder='templates', url_prefix='/ultimate')
api_blueprint = Blueprint('api_ultimate', __name__, url_prefix='/api/ultimate')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('ultimate/index.html', BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('ultimate_api')
    'version, jobs, configurations, update-all'
    bp.add_url_rule('/<string:command>',
                    defaults={'job_id': None},
                    view_func=view,
                    methods=['GET'])
    bp.add_url_rule('/job',
                    defaults={},
                    view_func=view,
                    methods=['POST'])
    bp.add_url_rule('/job/<string:job_id>',
                    defaults={'command': 'job'},
                    view_func=view,
                    methods=['GET', 'DELETE'])


class UltimateApi(MethodView):
    def __init__(self):
        self.data_folder = path.join(current_app.config['REVISION_FOLDER'], 'ultimate_jobs')
        if not path.exists(self.data_folder):
            mkdir(self.data_folder)
        self.ultimate = UltimateConnector

    def get(self, command: str, job_id: str) -> dict:
        if command == 'version':
            return {'version': self.ultimate.get_version()}
        elif command == 'jobs':
            jobs: list[UltimateJob] = get_all_jobs(self.data_folder)
            return {'data': [j.get() for j in jobs]}
        elif command == 'configurations':
            return self.ultimate.get_ultimate_configurations()
        elif command == 'update-all':
            jobs: list[UltimateJob] = get_all_jobs(self.data_folder)
            for j in jobs:
                if j.job_status == 'scheduled':
                    j.update(self.ultimate.get_job(j.job_id), self.data_folder)
            return {'status': 'done'}
        elif command == 'job':
            job = UltimateJob.from_file(save_dir=self.data_folder, job_id=job_id)
            if job.job_status == 'done':
                pass
            elif job.job_status == 'scheduled':
                job.update(self.ultimate.get_job(job_id), self.data_folder)
            else:
                pass
            return job.get()
        else:
            return {'status': 'error', 'message': 'unknown command'}

    def post(self) -> dict:
        data = request.get_data()
        configuration = request.args.get('configuration')
        job = self.ultimate.start_requirement_job(data, configuration)
        job.save_to_file(self.data_folder)
        return job.get()

    def delete(self, command: str, job_id: str) -> dict:
        if command == 'job':
            return self.ultimate.delete_job(job_id)


def get_all_jobs(data_folder: str) -> list[UltimateJob]:
    jobs: list[UltimateJob] = []
    for jf in get_filenames_from_dir(data_folder):
        jobs.append(UltimateJob.from_file(file_name=jf))
    return jobs


register_api(api_blueprint, UltimateApi)
