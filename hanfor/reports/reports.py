from flask import Blueprint, request

from hanfor_flask import current_app, nocache
from ressources import Reports


api_blueprint = Blueprint("api_reports", __name__, url_prefix="/api/report")


@api_blueprint.route("/get", methods=["GET"])
@nocache
def get():
    return Reports(current_app, request).apply_request()


@api_blueprint.route("/set", methods=["POST"])
@nocache
def set_report():
    return Reports(current_app, request).apply_request()
