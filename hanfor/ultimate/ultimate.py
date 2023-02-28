from typing import Type

from flask import Blueprint
from flask.views import MethodView

from ultimate.ultimate_connector import UltimateConnector

api_blueprint = Blueprint('api_ultimate', __name__, url_prefix='/api/ultimate')


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('ultimate_api')
    bp.add_url_rule('/version',
                    defaults={'command': 'version', 'name': None},
                    view_func=view, methods=['GET'])
    bp.add_url_rule('/job/<string:name>',
                    defaults={'command': 'job'},
                    view_func=view,
                    methods=['GET', 'POST', 'DELETE'])


class UltimateApi(MethodView):
    def __init__(self):
        self.ultimate = UltimateConnector
        pass

    def get(self, command: str, name: str) -> str:
        if command == 'version':
            return self.ultimate.get_version()
        elif command == 'job':
            return f'job {name}'

    def post(self, command: str, name: str) -> str:
        raise NotImplementedError

    def delete(self, command: str, name: str) -> str:
        raise NotImplementedError


register_api(api_blueprint, UltimateApi)
