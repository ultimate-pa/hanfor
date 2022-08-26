from flask import Blueprint, render_template, request, current_app, jsonify

BUNDLE_JS = 'dist/example_blueprint-bundle.js'
example_bp = Blueprint('example', __name__, template_folder='templates', url_prefix='/example_blueprint')

api_example_bp = Blueprint('api', __name__, url_prefix='/api')
example_bp.register_blueprint(api_example_bp)


@example_bp.route('/', methods=['GET'])
def index():
    # Get config from application context.
    config = current_app.config

    return render_template('example_blueprint/index.html', BUNDLE_JS=BUNDLE_JS)


@example_bp.route('/get_awesome_message', methods=['GET'])
def get_message():
    response = {'message': 'Hello World'}
    return jsonify(response)


@api_example_bp.route('/', methods=['GET'])
def get():
    return "there u go"
