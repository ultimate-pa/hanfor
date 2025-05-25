from flask import Blueprint, request
from hanfor_flask import current_app, nocache
from ressources import QueryAPI

api_blueprint = Blueprint("queries_api", __name__, url_prefix="/api/query")


@api_blueprint.route("/", methods=["GET", "POST", "DELETE"])
@nocache
def api_query():
    return QueryAPI(current_app, request).apply_request()
