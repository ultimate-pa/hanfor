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

from json_db_connector.json_db import JsonDatabase

import utils
from utils import add_custom_serializer_to_database
from lib_core.data import VariableCollection

from static_utils import (
    get_filenames_from_dir,
    choice,
    hash_file_sha1,
    SessionValue,
)

from tags.tags import TagsApi
from requirements import requirements
from variables import variables
from logs.logs import api_blueprint as logs_api
from reports.reports import api_blueprint as reports_api
from tools.tools import api_blueprint as tools_api
from queries.queries import api_blueprint as queries_api
from req_simulator import simulator_blueprint
from example_blueprint import example_blueprint
from tags import tags
from statistics import statistics

import mimetypes

# import Socket IO modules
from telemetry.telemetry import TelemetryWs


mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/javascript", ".js")


# Create the app
app = HanforFlask(__name__)
app.config.from_object("config")
app.db = None
socketio = SocketIO(app)

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
app.register_blueprint(tags.api_blueprint)
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


if app.config["FEATURE_ULTIMATE"]:
    from ultimate import ultimate

    app.register_blueprint(ultimate.blueprint)
    app.register_blueprint(ultimate.api_blueprint)

if app.config["FEATURE_TELEMETRY"]:
    from telemetry import telemetry_frontend

    app.register_blueprint(telemetry_frontend.blueprint)

# register Blueprints
# Example Blueprint
app.register_blueprint(example_blueprint.blueprint)
app.register_blueprint(example_blueprint.api_blueprint)

# register socket IO namespaces
telemetry_namespace = TelemetryWs("/telemetry")
socketio.on_namespace(telemetry_namespace)


if "USE_SENTRY" in app.config and app.config["USE_SENTRY"]:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()])

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


def update_var_usage(var_collection):
    var_collection.refresh_var_usage(app)
    var_collection.req_var_mapping = var_collection.invert_mapping(var_collection.var_req_mapping)
    var_collection.refresh_var_constraint_mapping()
    var_collection.store()
    app.db.update()


def varcollection_consistency_check(flask_app, args=None):
    logging.info("Check Variables for consistency.")
    # Update usages and constraint type check.
    var_collection = VariableCollection(flask_app)
    if args is not None and args.reload_type_inference:
        var_collection.reload_type_inference_errors_in_constraints()

    update_var_usage(var_collection)
    var_collection.store()
    app.db.update()


def create_revision(args, base_revision_name, *, no_data_tracing: bool = False):
    """Create new revision.

    :param args: Parser arguments
    :param base_revision_name: Name of revision the created will be based on. Creates initial revision_0 if none given.
    :param no_data_tracing: db testmode
    :return: None
    """
    revision = utils.Revision(app, args, base_revision_name)
    revision.create_revision()


def load_revision(revision_id):
    """Loads a revision to be served by hanfor by setting the config.

    :param revision_id: An existing revision name
    :type revision_id: str
    """
    if revision_id not in utils.get_available_revisions(app.config):
        logging.error("Revision `{}` not found in `{}`".format(revision_id, app.config["SESSION_FOLDER"]))
        raise FileNotFoundError

    app.config["USING_REVISION"] = revision_id
    app.config["REVISION_FOLDER"] = os.path.join(app.config["SESSION_FOLDER"], revision_id)
    app.config["SESSION_VARIABLE_COLLECTION"] = os.path.join(
        app.config["REVISION_FOLDER"], "session_variable_collection.pickle"
    )
    app.db.init_tables(app.config["REVISION_FOLDER"])
    if app.config["FEATURE_TELEMETRY"]:
        telemetry_namespace.set_data_folder(app.config["REVISION_FOLDER"])


def user_request_new_revision(args, *, no_data_tracing: bool = False):
    """Asks the user about the base revision and triggers create_revision with the user choice.

    :param args:
    :param no_data_tracing:
    """
    logging.info("Generating a new revision.")
    available_sessions = utils.get_stored_session_names(app.config["SESSION_BASE_FOLDER"], only_names=True)
    if app.config["SESSION_TAG"] not in available_sessions:
        logging.error(
            "Session `{tag}` not found (in `{sessions_folder}`)".format(
                tag=app.config["SESSION_TAG"], sessions_folder=app.config["SESSION_BASE_FOLDER"]
            )
        )
        raise FileNotFoundError
    # Ask user for base revision.
    available_revisions = utils.get_available_revisions(app.config)
    if len(available_revisions) == 0:
        logging.error("No base revisions found in `{}`.".format(app.config["SESSION_FOLDER"]))
        raise FileNotFoundError
    print("Which revision should I use as a base?")
    base_revision_choice = choice(available_revisions, "revision_0")
    create_revision(args, base_revision_choice, no_data_tracing=no_data_tracing)


def set_session_config_vars(args, here):
    """Initialize config vars:
    SESSION_TAG,
    SESSION_FOLDER
    for current session.

    :param args: Parsed arguments.
    :param here: path to folder of this file
    """
    app.config["SESSION_TAG"] = args.tag
    if app.config["SESSION_BASE_FOLDER"] is None:
        app.config["SESSION_BASE_FOLDER"] = os.path.join(here, "data")
    app.config["SESSION_FOLDER"] = os.path.join(app.config["SESSION_BASE_FOLDER"], app.config["SESSION_TAG"])


def user_choose_start_revision():
    """Asks the user which revision should be loaded if there is more than one revision.
    :rtype: str
    :return: revision name
    """
    available_revisions = utils.get_available_revisions(app.config)
    revision_choice = "revision_0"
    # Start the first revision if there is only one.
    if len(available_revisions) == 1:
        revision_choice = available_revisions[0]
    # If there is no revision it means probably that this is an old hanfor version.
    # ask the user to migrate.
    elif len(available_revisions) == 0:
        print("No revisions found. You might use a deprecated session version without revision support.")
        print("Is that true and should I migrate this session?")
        migrate_session = choice(["yes", "no"], "no")
        if migrate_session == "yes":
            file_paths = [
                path for path in get_filenames_from_dir(app.config["SESSION_FOLDER"]) if path.endswith(".pickle")
            ]
            revision_folder = os.path.join(app.config["SESSION_FOLDER"], revision_choice)
            logging.info("Create revision folder and copy existing data.")
            os.makedirs(revision_folder, exist_ok=True)
            for path in file_paths:
                new_path = os.path.join(revision_folder, os.path.basename(path))
                os.rename(path, new_path)
        else:
            exit()
    else:
        print("Which revision should I start.")
        available_revisions = sorted(utils.get_available_revisions(app.config))
        revision_choice = choice(available_revisions, available_revisions[-1])
    return revision_choice


def set_app_config_paths(here):
    app.config["SCRIPT_UTILS_PATH"] = os.path.join(here, "script_utils")
    app.config["TEMPLATES_FOLDER"] = os.path.join(here, "templates")


def startup_hanfor(args, here, *, no_data_tracing: bool = False) -> bool:
    """Setup session config Variables.
     Trigger:
     Revision creation/loading.
     Variable script evaluation.
     Version migrations.
     Consistency checks.

    :param args:
    :param here:
    :param no_data_tracing:
    :returns: True if startup should continue
    """
    app.db = JsonDatabase(no_data_tracing=no_data_tracing)
    add_custom_serializer_to_database(app.db)

    set_session_config_vars(args, here)
    set_app_config_paths(here)

    # Create a new revision if requested.
    if args.revision:
        if args.input_csv is None:
            utils.HanforArgumentParser(app).error("--revision requires a Input CSV -c INPUT_CSV.")
        user_request_new_revision(args, no_data_tracing=no_data_tracing)
    else:
        # If there is no session with given tag: Create a new (initial) revision.
        if not os.path.exists(app.config["SESSION_FOLDER"]):
            create_revision(args, None, no_data_tracing=no_data_tracing)
        # If this is an already existing session, ask the user which revision to start.
        else:
            revision_choice = user_choose_start_revision()
            logging.info("Loading session `{}` at `{}`".format(app.config["SESSION_TAG"], revision_choice))
            load_revision(revision_choice)

    if args.input_csv:
        logging.info("Check CSV integrity.")
        csv_hash = hash_file_sha1(args.input_csv)
        if not app.db.key_in_table(SessionValue, "csv_hash"):
            app.db.add_object(SessionValue("csv_hash", csv_hash))
        if csv_hash != app.db.get_object(SessionValue, "csv_hash").value:
            print(
                f"Sha-1 hash mismatch between: \n`{app.db.get_object(SessionValue, 'csv_input_file').value}`"
                f"\nand\n`{args.input_csv}`."
            )
            print("Consider starting a new revision.\nShould I stop loading?")
            if choice(["Yes", "No"], default="Yes") == "Yes":
                return False
            app.db.get_object(SessionValue, "csv_hash").value = csv_hash
            app.db.update()
        if not app.db.key_in_table(SessionValue, "csv_input_file"):
            app.db.add_object(SessionValue("csv_input_file", args.input_csv))
        else:
            app.db.get_object(SessionValue, "csv_input_file").value = args.input_csv
        app.db.update()

    app.config["CSV_INPUT_FILE"] = os.path.basename(app.db.get_object(SessionValue, "csv_input_file").value)
    app.config["CSV_INPUT_FILE_PATH"] = app.db.get_object(SessionValue, "csv_input_file").value

    # Initialize variables collection, import session
    utils.config_check(app.config)

    # Run consistency checks.
    varcollection_consistency_check(app, args)

    # instantiate TagsApi for generating init_tags
    with app.app_context():
        TagsApi()
    return True


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
    utils.setup_logging(app)
    app.wsgi_app = utils.PrefixMiddleware(app.wsgi_app, prefix=app.config["URL_PREFIX"])
    HERE = os.path.dirname(os.path.realpath(__file__))

    app.debug = app.config["DEBUG_MODE"]
    if app.config["DEBUG_MODE"]:
        toolbar = DebugToolbarExtension(app)

    fetch_hanfor_version()
    utils.register_assets(app)

    # Parse python args and startup hanfor session.
    parsed_args = utils.HanforArgumentParser(app).parse_args()
    if startup_hanfor(parsed_args, HERE):
        socketio.run(app, **get_app_options(), allow_unsafe_werkzeug=True)
