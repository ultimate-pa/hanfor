from typing import Type

from flask import Blueprint, render_template, request
from flask.views import MethodView

from ultimate.ultimate_connector import UltimateConnector

BUNDLE_JS = 'dist/ultimate-bundle.js'
blueprint = Blueprint('ultimate', __name__, template_folder='templates', url_prefix='/ultimate')
api_blueprint = Blueprint('api_ultimate', __name__, url_prefix='/api/ultimate')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('ultimate/index.html', BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('ultimate_api')
    bp.add_url_rule('/version',
                    defaults={'command': 'version', 'job_id': None},
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
        self.ultimate = UltimateConnector

    def get(self, command: str, job_id: str) -> str:
        if command == 'version':
            return self.ultimate.get_version()
        elif command == 'job':
            return self.ultimate.get_job(job_id)

    def post(self) -> str:
        data = request.get_data()
        return self.ultimate.start_job(
            data,
            ".req",
            "ReqCheck",
            "ReqCheck-non-lin"
        )

    def delete(self, command: str, job_id: str) -> str:
        if command == 'job':
            return self.ultimate.delete_job(job_id)


register_api(api_blueprint, UltimateApi)
