from flask import Blueprint, render_template
from flask_restx import Namespace

BUNDLE_JS = "dist/ts_editor-bundle.js"
blueprint = Blueprint("ts-editor", __name__, template_folder="templates", url_prefix="/ts-editor")

api = Namespace("TS Editor", "TS Editor api Description", path="/ts-editor", ordered=True)


@blueprint.route("", methods=["GET"])
def index():
    return render_template(
        "ts-editor/index.html",
        BUNDLE_JS=BUNDLE_JS,
    )
