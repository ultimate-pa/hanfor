from ressources.simulator_ressource import SimulatorRessource  # TODO move this class to some better place
from flask import Blueprint, request
from hanfor_flask import current_app, nocache

blueprint = Blueprint("simulator", __name__, template_folder="templates", url_prefix="/simulator")


@blueprint.route("", methods=["GET", "POST", "DELETE"])
@nocache
def index():
    return SimulatorRessource(current_app, request).apply_request()
