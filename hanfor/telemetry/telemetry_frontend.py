from flask import Blueprint, render_template


BUNDLE_JS = "dist/telemetry_frontend-bundle.js"
blueprint = Blueprint("telemetry", __name__, template_folder="templates", url_prefix="/telemetry")


@blueprint.route("/", methods=["GET"])
def index():
    return render_template(
        "telemetry/index.html",
        BUNDLE_JS=BUNDLE_JS,
    )


@blueprint.route("/set-name", methods=["GET"])
def set_name():
    return render_template(
        "telemetry/set_name.html",
        BUNDLE_JS=BUNDLE_JS,
    )
