import logging
import os

from hanfor_flask import HanforFlask
from json_db_connector.json_db import JsonDatabase

import utils
from utils import add_custom_serializer_to_database
from lib_core.data import VariableCollection
from tags.tags import TagsApi

from static_utils import (
    get_filenames_from_dir,
    choice,
    hash_file_sha1,
    SessionValue,
)


def update_var_usage(flask_app: HanforFlask, var_collection):
    var_collection.refresh_var_usage(flask_app)
    var_collection.req_var_mapping = var_collection.invert_mapping(var_collection.var_req_mapping)
    var_collection.refresh_var_constraint_mapping()
    var_collection.store()
    flask_app.db.update()


def varcollection_consistency_check(flask_app: HanforFlask, args=None):
    logging.info("Check Variables for consistency.")
    # Update usages and constraint type check.
    var_collection = VariableCollection(flask_app)
    if args is not None and args.reload_type_inference:
        var_collection.reload_type_inference_errors_in_constraints()

    update_var_usage(flask_app, var_collection)
    var_collection.store()
    flask_app.db.update()


def create_revision(flask_app: HanforFlask, args, base_revision_name, *, no_data_tracing: bool = False):
    revision = utils.Revision(flask_app, args, base_revision_name)
    revision.create_revision()


def load_revision(flask_app: HanforFlask, revision_id):
    if revision_id not in utils.get_available_revisions(flask_app.config):
        logging.error("Revision `{}` not found in `{}`".format(revision_id, flask_app.config["SESSION_FOLDER"]))
        raise FileNotFoundError

    flask_app.config["USING_REVISION"] = revision_id
    flask_app.config["REVISION_FOLDER"] = os.path.join(flask_app.config["SESSION_FOLDER"], revision_id)
    flask_app.config["SESSION_VARIABLE_COLLECTION"] = os.path.join(
        flask_app.config["REVISION_FOLDER"], "session_variable_collection.pickle"
    )
    flask_app.db.init_tables(flask_app.config["REVISION_FOLDER"])


def user_request_new_revision(flask_app: HanforFlask, args, *, no_data_tracing: bool = False):
    logging.info("Generating a new revision.")
    available_sessions = utils.get_stored_session_names(flask_app.config["SESSION_BASE_FOLDER"], only_names=True)
    if flask_app.config["SESSION_TAG"] not in available_sessions:
        logging.error(
            "Session `{tag}` not found (in `{sessions_folder}`)".format(
                tag=flask_app.config["SESSION_TAG"], sessions_folder=flask_app.config["SESSION_BASE_FOLDER"]
            )
        )
        raise FileNotFoundError
    # Ask user for base revision.
    available_revisions = utils.get_available_revisions(flask_app.config)
    if len(available_revisions) == 0:
        logging.error("No base revisions found in `{}`.".format(flask_app.config["SESSION_FOLDER"]))
        raise FileNotFoundError
    print("Which revision should I use as a base?")
    base_revision_choice = choice(available_revisions, "revision_0")
    create_revision(flask_app, args, base_revision_choice, no_data_tracing=no_data_tracing)


def set_session_config_vars(flask_app: HanforFlask, args, here):
    flask_app.config["SESSION_TAG"] = args.tag
    if flask_app.config["SESSION_BASE_FOLDER"] is None:
        flask_app.config["SESSION_BASE_FOLDER"] = os.path.join(here, "data")
    flask_app.config["SESSION_FOLDER"] = os.path.join(
        flask_app.config["SESSION_BASE_FOLDER"], flask_app.config["SESSION_TAG"]
    )


def user_choose_start_revision(flask_app: HanforFlask):
    """Asks the user which revision should be loaded if there is more than one revision.
    :rtype: str
    :return: revision name
    """
    available_revisions = utils.get_available_revisions(flask_app.config)
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
                path for path in get_filenames_from_dir(flask_app.config["SESSION_FOLDER"]) if path.endswith(".pickle")
            ]
            revision_folder = os.path.join(flask_app.config["SESSION_FOLDER"], revision_choice)
            logging.info("Create revision folder and copy existing data.")
            os.makedirs(revision_folder, exist_ok=True)
            for path in file_paths:
                new_path = os.path.join(revision_folder, os.path.basename(path))
                os.rename(path, new_path)
        else:
            exit()
    else:
        print("Which revision should I start.")
        available_revisions = sorted(utils.get_available_revisions(flask_app.config))
        revision_choice = choice(available_revisions, available_revisions[-1])
    return revision_choice


def set_app_config_paths(flask_app: HanforFlask, here):
    flask_app.config["SCRIPT_UTILS_PATH"] = os.path.join(here, "script_utils")
    flask_app.config["TEMPLATES_FOLDER"] = os.path.join(here, "templates")


def startup_hanfor(flask_app: HanforFlask, args, here, *, no_data_tracing: bool = False) -> bool:
    flask_app.db = JsonDatabase(no_data_tracing=no_data_tracing)
    add_custom_serializer_to_database(flask_app.db)

    set_session_config_vars(flask_app, args, here)
    set_app_config_paths(flask_app, here)

    # Create a new revision if requested.
    if args.revision:
        if args.input_csv is None:
            utils.HanforArgumentParser(flask_app).error("--revision requires a Input CSV -c INPUT_CSV.")
        user_request_new_revision(flask_app, args, no_data_tracing=no_data_tracing)
    else:
        # If there is no session with given tag: Create a new (initial) revision.
        if not os.path.exists(flask_app.config["SESSION_FOLDER"]):
            create_revision(flask_app, args, None, no_data_tracing=no_data_tracing)
        # If this is an already existing session, ask the user which revision to start.
        else:
            revision_choice = user_choose_start_revision(flask_app)
            logging.info("Loading session `{}` at `{}`".format(flask_app.config["SESSION_TAG"], revision_choice))
            load_revision(flask_app, revision_choice)

    if args.input_csv:
        logging.info("Check CSV integrity.")
        csv_hash = hash_file_sha1(args.input_csv)
        if not flask_app.db.key_in_table(SessionValue, "csv_hash"):
            flask_app.db.add_object(SessionValue("csv_hash", csv_hash))
        if csv_hash != flask_app.db.get_object(SessionValue, "csv_hash").value:
            print(
                f"Sha-1 hash mismatch between: \n`{flask_app.db.get_object(SessionValue, 'csv_input_file').value}`"
                f"\nand\n`{args.input_csv}`."
            )
            print("Consider starting a new revision.\nShould I stop loading?")
            if choice(["Yes", "No"], default="Yes") == "Yes":
                return False
            flask_app.db.get_object(SessionValue, "csv_hash").value = csv_hash
            flask_app.db.update()
        if not flask_app.db.key_in_table(SessionValue, "csv_input_file"):
            flask_app.db.add_object(SessionValue("csv_input_file", args.input_csv))
        else:
            flask_app.db.get_object(SessionValue, "csv_input_file").value = args.input_csv
        flask_app.db.update()

    flask_app.config["CSV_INPUT_FILE"] = os.path.basename(flask_app.db.get_object(SessionValue, "csv_input_file").value)
    flask_app.config["CSV_INPUT_FILE_PATH"] = flask_app.db.get_object(SessionValue, "csv_input_file").value

    # Initialize variables collection, import session
    utils.config_check(flask_app.config)

    # Run consistency checks.
    varcollection_consistency_check(flask_app, args)

    # instantiate TagsApi for generating init_tags
    with flask_app.app_context():
        TagsApi()

    return True
