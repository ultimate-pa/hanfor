""" 
@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""

import logging
import os
import subprocess

from flask import jsonify
from flask_socketio import SocketIO
from hanfor_flask import HanforFlask
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import HTTPException
from flask_restx import Api

from lib_core.startup import startup_hanfor, PrefixMiddleware, HanforArgumentParser
from lib_core.utils import setup_logging
from lib_core.api_models import api_models

from requirements import requirements
from variables import variables
from logs.logs import api_blueprint as logs_api
from reports.reports import api_blueprint as reports_api
from tools.tools import api_blueprint as tools_api
from queries.queries import api_blueprint as queries_api
from req_simulator import simulator_blueprint
from tags import tags
from statistics import statistics

import mimetypes

# import Socket IO modules
from telemetry.telemetry import TelemetryWs
from ai.ai_socket import AiDataNamespace


mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/javascript", ".js")


# Create the app
app = HanforFlask(__name__)
app.config.from_pyfile("config.dist.py")
app.config.from_object("config")
app.db = None

# Initialize SocketIO
socketio = SocketIO(app)

# Initialize Api framework
api = Api(app, version="1.0", title="Hanfor API", prefix="/api/v1", doc="/api")
# load all api models
api.add_namespace(api_models)

# Register core blueprints and apis
# Requirements
app.register_blueprint(requirements.blueprint)
app.register_blueprint(requirements.api_blueprint)
# Variables
app.register_blueprint(variables.blueprint)
app.register_blueprint(variables.blueprint2)  # import for variable_import
app.register_blueprint(variables.api_blueprint)
# Logs
app.register_blueprint(logs_api)
# Tags
app.register_blueprint(tags.blueprint)
api.add_namespace(tags.api)
# Statistics
app.register_blueprint(statistics.blueprint)
app.register_blueprint(statistics.api_blueprint)
# Reports
app.register_blueprint(reports_api)
# Tools
app.register_blueprint(tools_api)
# Quereis
app.register_blueprint(queries_api)
# Simulator
app.register_blueprint(simulator_blueprint.blueprint)

# Register feature blueprints and apis
if app.config["FEATURE_EXAMPLE_BLUEPRINT"]:
    from example_blueprint import example_blueprint

    app.register_blueprint(example_blueprint.blueprint)
    api.add_namespace(example_blueprint.api)

if app.config["FEATURE_ULTIMATE"]:
    from ultimate import ultimate

    app.register_blueprint(ultimate.blueprint)
    api.add_namespace(ultimate.api)

# Ai
if app.config["FEATURE_AI"]:
    from hanfor.ai.ai_api import ai_api
    from hanfor.ai.ai_core import AiCore

    app.ai = AiCore()
    app.register_blueprint(ai_api.blueprint)
    app.register_blueprint(ai_api.api_blueprint)

if app.config["FEATURE_TELEMETRY"]:
    from telemetry import telemetry_frontend

    app.register_blueprint(telemetry_frontend.blueprint)

if app.config["FEATURE_QUICK_CHECKS"]:
    from quickchecks import quickchecks

    # quickchecks
    app.register_blueprint(quickchecks.blueprint)
    app.register_blueprint(quickchecks.api_blueprint)


# register SocketIO namespaces
telemetry_namespace = TelemetryWs("/telemetry")
socketio.on_namespace(telemetry_namespace)

ai_data_namespace = AiDataNamespace("/ai_data")
socketio.on_namespace(ai_data_namespace)


logging.basicConfig(
    format="[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


@app.errorhandler(Exception)
def unhandled_exception(e):
    # Pass through HTTP errors in range 300-308.
    if isinstance(e, HTTPException) and e.code in range(300, 309):
        return e

    app.logger.error("Unhandled Exception: {}".format(e))
    logging.exception(e)

    # Pass through HTTP errors.
    if isinstance(e, HTTPException):
        return e

    # Handle non-HTTP errors.
    return jsonify({"success": False, "errormsg": repr(e)}), 500


def fetch_hanfor_version():
    """Get `git describe --always --tags` and store to config at HANFOR_VERSION"""
    try:
        app.config["HANFOR_VERSION"] = (
            subprocess.check_output(["git", "describe", "--always", "--tags"]).decode("utf-8").strip()
        )
        app.config["HANFOR_COMMIT_HASH"] = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except Exception as e:
        logging.info(f"Could not get Hanfor version. Is git installed and Hanfor run from its repo?: {e}")
        app.config["HANFOR_VERSION"] = "?"
        app.config["HANFOR_COMMIT_HASH"] = "?"


def get_app_options():
    """Returns Flask runtime options.

    :rtype: dict
    """
    app_options = {"host": app.config["HOST"], "port": app.config["PORT"]}

    if app.config["PYCHARM_DEBUG"]:
        app_options["debug"] = False
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    return app_options


if __name__ == "__main__":
    setup_logging(app)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config["URL_PREFIX"])
    HERE = os.path.dirname(os.path.realpath(__file__))

    app.debug = app.config["DEBUG_MODE"]
    if app.config["DEBUG_MODE"]:
        toolbar = DebugToolbarExtension(app)

    fetch_hanfor_version()

    # Parse python args and startup hanfor session.
    parsed_args = HanforArgumentParser(app).parse_args()
    if startup_hanfor(app, parsed_args, HERE):

        # Startup AI (start clustering if Flagged)
        if app.config["FEATURE_AI"]:
            with app.app_context():
                app.ai.startup(app.config["REVISION_FOLDER"], socketio)

        if app.config["FEATURE_TELEMETRY"]:
            telemetry_namespace.set_data_folder(app.config["REVISION_FOLDER"])
        socketio.run(app, **get_app_options(), allow_unsafe_werkzeug=True)
