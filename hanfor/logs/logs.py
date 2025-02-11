import utils

from flask import Blueprint
from hanfor_flask import current_app, nocache


api_blueprint = Blueprint("api_logs", __name__, url_prefix="/api/logs")


@api_blueprint.route("/get", methods=["GET"])
@nocache
def get_logs():
    return utils.get_flask_session_log(current_app, html_format=True)
