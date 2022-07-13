from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

blueprint = Blueprint('example_bp', __name__, template_folder='templates')


@blueprint.route('/', defaults={'page': 'index'})
@blueprint.route('/<page>')
def show(page):
    try:
        return render_template(f'example_bp/{page}.html')
    except TemplateNotFound:
        abort(404)
