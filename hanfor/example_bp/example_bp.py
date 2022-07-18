from flask import Blueprint, render_template, request, current_app

BUNDLE_JS = 'dist/example_bp-bundle.js'
blueprint = Blueprint('example_bp', __name__, template_folder='templates', static_folder='static')


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    # Get config from application context.
    config = current_app.config

    #if request.method == 'GET':
    return render_template('example_bp/index.html', BUNDLE_JS=BUNDLE_JS)

    #if request.method == 'POST':

