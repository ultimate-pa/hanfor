from typing import Type
from flask import Blueprint, render_template, request, jsonify, Response
from flask.views import MethodView
from pydantic import BaseModel

# Flask: Modular Applications with Blueprints. https://flask.palletsprojects.com/en/2.2.x/blueprints/
# Flask: Method Dispatching and APIs. https://flask.palletsprojects.com/en/2.2.x/views/#method-dispatching-and-apis
# HTTP request methods. https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# Pydantic: Models. https://pydantic-docs.helpmanual.io/usage/models

BUNDLE_JS = 'dist/example_blueprint-bundle.js'
blueprint = Blueprint('example_blueprint', __name__, template_folder='templates', url_prefix='/example-blueprint')
api_blueprint = Blueprint('api_example_blueprint', __name__, url_prefix='/api/example-blueprint')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('example_blueprint/index.html', BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('example_blueprint_api')
    bp.add_url_rule('/', defaults={'id': None}, view_func=view, methods=['GET'])
    bp.add_url_rule('/', defaults={}, view_func=view, methods=['POST'])
    bp.add_url_rule('/<int:id>', view_func=view, methods=['GET', 'PUT', 'PATCH', 'DELETE'])


class ExampleBlueprintApi(MethodView):
    # The HTTP GET method requests a representation of the specified resource. Requests using GET should only be used to
    # request data (they shouldn't include data).
    def get(self, id: int) -> str | dict | tuple | Response:
        return f'HTTP GET for id `{id}` received.'

    # The HTTP POST method sends data to the server. The type of the body of the request is indicated by the
    # Content-Type header.
    def post(self) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            id: int
            data: str

        request_data = RequestData.parse_obj(request.json)

        return f'HTTP POST received.'

    # The HTTP PUT request method creates a new resource or replaces a representation of the target resource with the
    # request payload.
    def put(self, id: int) -> str | dict | tuple | Response:
        return f'HTTP PUT for id `{id}` received.'

    # The HTTP PATCH request method applies partial modifications to a resource.
    def patch(self, id: int) -> str | dict | tuple | Response:
        return f'HTTP PATCH for id `{id}` received.'

    # The HTTP DELETE request method deletes the specified resource.
    def delete(self, id: int) -> str | dict | tuple | Response:
        return f'HTTP DELETE for id `{id}` received.'


register_api(api_blueprint, ExampleBlueprintApi)
