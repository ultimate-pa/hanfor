import logging
import os
import datetime
import argparse
import json
import hashlib
from typing import Callable
from terminaltables import DoubleTable
import shutil
import re

import config
from hanfor_flask import HanforFlask
from json_db_connector.json_db import JsonDatabase, remove_json_database_data_tracing_logger

from lib_core import boogie_parsing
from lib_core.utils import (
    get_requirements,
    get_default_pattern_options,
    clean_identifier_for_ultimate_parser,
    get_filenames_from_dir,
    choice,
)
from lib_core.data import Tag, VariableCollection, Scope, SessionValue, Requirement, Variable
from configuration.patterns import APattern
from configuration.defaults import Color
from configuration.tags import STANDARD_TAGS, FUNCTIONAL_TAGS

from reqtransformer import RequirementCollection
from thread_handling.threading_core import ThreadHandler

if config.FEATURE_AI:
    from ai_request.ai_core_requests import AiRequest


def config_check(app_config):
    to_ensure_configs = ["PATTERNS_GROUP_ORDER"]
    for to_ensure_config in to_ensure_configs:
        if to_ensure_config not in app_config:
            raise SyntaxError("Could not find {} in config.".format(to_ensure_config))

    # Check pattern groups set correctly.
    pattern_groups_used = set((pattern.group for pattern in APattern.get_patterns().values()))
    pattern_groups_set = set((group for group in app_config["PATTERNS_GROUP_ORDER"]))
    # Pattern group for downwards compatibility: Legacy patterns are not shown in dropdown (but still deserializable)
    pattern_groups_set.add("Legacy")

    if not pattern_groups_used == pattern_groups_set:
        if len(pattern_groups_used - pattern_groups_set) > 0:
            raise SyntaxError(
                "No group order set in config for pattern groups {}".format(pattern_groups_used - pattern_groups_set)
            )

    try:
        get_default_pattern_options()
    except Exception as e:
        raise SyntaxError("Could not parse pattern config. Please check your config.py: {}.".format(e))


def update_var_usage(flask_app: HanforFlask, var_collection):
    var_collection.refresh_var_usage(flask_app.db.get_objects(Requirement).values())
    var_collection.req_var_mapping = var_collection.invert_mapping(var_collection.var_req_mapping)
    var_collection.refresh_var_constraint_mapping()
    var_collection.store()
    flask_app.db.update()


def varcollection_consistency_check(flask_app: HanforFlask, args=None):
    logging.info("Check Variables for consistency.")
    # Update usages and constraint type check.
    var_collection = VariableCollection(
        flask_app.db.get_objects(Variable).values(), flask_app.db.get_objects(Requirement).values()
    )
    if args is not None and args.reload_type_inference:
        var_collection.reload_type_inference_errors_in_constraints(SessionValue.get_standard_tags(flask_app.db))

    update_var_usage(flask_app, var_collection)
    var_collection.store()
    flask_app.db.update()


def create_revision(flask_app: HanforFlask, args, base_revision_name):
    revision = Revision(flask_app, args, base_revision_name)
    revision.create_revision()


def load_revision(flask_app: HanforFlask, revision_id):
    if revision_id not in get_available_revisions(flask_app.config):
        logging.error("Revision `{}` not found in `{}`".format(revision_id, flask_app.config["SESSION_FOLDER"]))
        raise FileNotFoundError

    flask_app.config["USING_REVISION"] = revision_id
    flask_app.config["REVISION_FOLDER"] = os.path.join(flask_app.config["SESSION_FOLDER"], revision_id)
    flask_app.config["SESSION_VARIABLE_COLLECTION"] = os.path.join(
        flask_app.config["REVISION_FOLDER"], "session_variable_collection.pickle"
    )
    flask_app.db.init_tables(flask_app.config["REVISION_FOLDER"])


def user_request_new_revision(flask_app: HanforFlask, args):
    logging.info("Generating a new revision.")
    available_sessions = get_stored_session_names(flask_app.config["SESSION_BASE_FOLDER"], only_names=True)
    if flask_app.config["SESSION_TAG"] not in available_sessions:
        logging.error(
            "Session `{tag}` not found (in `{sessions_folder}`)".format(
                tag=flask_app.config["SESSION_TAG"], sessions_folder=flask_app.config["SESSION_BASE_FOLDER"]
            )
        )
        raise FileNotFoundError
    # Ask user for base revision.
    available_revisions = get_available_revisions(flask_app.config)
    if len(available_revisions) == 0:
        logging.error("No base revisions found in `{}`.".format(flask_app.config["SESSION_FOLDER"]))
        raise FileNotFoundError
    print("Which revision should I use as a base?")
    base_revision_choice = choice(available_revisions, "revision_0")
    create_revision(flask_app, args, base_revision_choice)


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
    available_revisions = get_available_revisions(flask_app.config)
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
        available_revisions = sorted(get_available_revisions(flask_app.config))
        revision_choice = choice(available_revisions, available_revisions[-1])
    return revision_choice


def set_app_config_paths(flask_app: HanforFlask, here):
    flask_app.config["SCRIPT_UTILS_PATH"] = os.path.join(here, "script_utils")
    flask_app.config["TEMPLATES_FOLDER"] = os.path.join(here, "templates")


def startup_hanfor(flask_app: HanforFlask, args, here, *, no_data_tracing: bool = False) -> bool:
    flask_app.thread_handler = ThreadHandler()
    if config.FEATURE_AI:
        flask_app.ai_request = AiRequest()

    flask_app.db = JsonDatabase(no_data_tracing=no_data_tracing)
    add_custom_serializer_to_database(flask_app.db)

    set_session_config_vars(flask_app, args, here)
    set_app_config_paths(flask_app, here)

    # Create a new revision if requested.
    if args.revision:
        if args.input_csv is None:
            HanforArgumentParser(flask_app).error("--revision requires a Input CSV -c INPUT_CSV.")
        user_request_new_revision(flask_app, args)
    else:
        if not os.path.exists(flask_app.config["SESSION_FOLDER"]):
            # If there is no session with given tag: Create a new (initial) revision.
            create_revision(flask_app, args, None)
            # insert functional and standard tags
            for name, values in FUNCTIONAL_TAGS.items():
                tag = Tag(name, **values)
                flask_app.db.add_object(tag, delay_update=True)
                flask_app.db.add_object(SessionValue(f"TAG_{name}", tag), delay_update=True)
            for name, properties in STANDARD_TAGS.items():
                flask_app.db.add_object(Tag(name, **properties), delay_update=True)
            flask_app.db.update()
        else:
            # If this is an already existing session, ask the user which revision to start.
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
    config_check(flask_app.config)

    # check functional Tags
    existing_tags: dict[str, Tag] = {t.name: t for t in flask_app.db.get_objects(Tag).values()}
    for name, values in FUNCTIONAL_TAGS.items():
        if name not in existing_tags:
            tag = Tag(name, **values)
            flask_app.db.add_object(tag)
            if flask_app.db.key_in_table(SessionValue, f"TAG_{name}"):
                s: SessionValue = flask_app.db.get_object(SessionValue, f"TAG_{name}")
                s.value = tag
                flask_app.db.update()
            else:
                flask_app.db.add_object(SessionValue(f"TAG_{name}", tag))
        else:
            tag = existing_tags[name]
            if not flask_app.db.key_in_table(SessionValue, f"TAG_{name}"):
                flask_app.db.add_object(SessionValue(f"TAG_{name}", tag))

    # Run consistency checks.
    varcollection_consistency_check(flask_app, args)

    return True


class Revision:  # TODO wohin damit
    def __init__(self, app: HanforFlask, args, base_revision_name):
        self.app = app
        self.args = args
        self.base_revision_name = base_revision_name
        self.is_initial_revision = True
        self.base_revision_folder = None
        self.base_revision_db = None
        self.available_sessions = None
        self.requirement_collection = None

        self._set_is_initial_revision()
        self._set_revision_name()
        self._set_base_revision_folder()

    def create_revision(self):
        self._check_base_revision_available()
        self._set_config_vars()
        self._set_available_sessions()
        if self.is_initial_revision:
            self._create_revision_folder()
        else:
            self._copy_base_revision()

        self._set_base_revision_db()
        self.app.db.init_tables(self.app.config["REVISION_FOLDER"])
        self._try_save(self._load_from_csv, "Could not read CSV")
        if self.is_initial_revision:
            for req in self.requirement_collection.requirements:
                self.app.db.add_object(req, delay_update=True)
            self.app.db.update()
            self._generate_session_values()
        else:
            self._update_session_values()
            self._try_save(self._merge_with_base_revision, " Could not merge with base session")

    def _try_save(self, what, error_msg):
        """Safely run a method. Cleanup the revision in case of an exception.

        Args:
            what: Method to run.
            error_msg: Message in case of failure.
        """
        try:
            what()
        except Exception as e:
            logging.error("Abort creating revision. {msg}: {error}".format(msg=error_msg, error=type(e)))
            self._revert_and_cleanup()
            raise e

    def _set_revision_name(self):
        if not self.base_revision_name:
            logging.info("No revisions for `{}`. Creating initial revision.".format(self.args.tag))
            self.revision_name = "revision_0"
        # Revision based on an existing revision
        else:
            new_revision_count = max([int(name.split("_")[1]) for name in get_available_revisions(self.app.config)]) + 1
            self.revision_name = "revision_{}".format(new_revision_count)

    def _set_base_revision_db(self):
        if not self.is_initial_revision:
            self.base_revision_db = JsonDatabase(read_only=True)
            add_custom_serializer_to_database(self.base_revision_db)
            self.base_revision_db.init_tables(self.base_revision_folder)

    def _set_base_revision_folder(self):
        if not self.is_initial_revision:
            self.base_revision_folder = os.path.join(self.app.config["SESSION_FOLDER"], self.base_revision_name)

    def _set_is_initial_revision(self):
        if self.base_revision_name:
            self.is_initial_revision = False

    def _set_config_vars(self):
        self.app.config["USING_REVISION"] = self.revision_name
        self.app.config["REVISION_FOLDER"] = os.path.join(self.app.config["SESSION_FOLDER"], self.revision_name)

    def _check_base_revision_available(self):
        if not self.is_initial_revision and self.base_revision_name not in get_available_revisions(self.app.config):
            logging.error(
                "Base revision `{}` not found in `{}`".format(
                    self.base_revision_name, self.app.config["SESSION_FOLDER"]
                )
            )
            raise FileNotFoundError

    def _set_available_sessions(self):
        self.available_sessions = get_stored_session_names(self.app.config["SESSION_BASE_FOLDER"], with_revisions=True)

    def _load_from_csv(self):
        # Load requirements from .csv file and store them into separate requirements.
        if self.args.input_csv is None:
            HanforArgumentParser(self.app).error("Creating an (initial) revision requires -c INPUT_CSV")
        self.requirement_collection = RequirementCollection()
        base_revision_headers = {}
        if self.base_revision_db:
            base_revision_headers = self.base_revision_db.get_objects(SessionValue)
        self.requirement_collection.create_from_csv(
            csv_file=self.args.input_csv,
            app=self.app,
            input_encoding="utf8",
            base_revision_headers=base_revision_headers,
            user_provided_headers=(json.loads(self.args.headers) if self.args.headers else None),
            available_sessions=self.available_sessions,
        )

    def _create_revision_folder(self):
        os.makedirs(self.app.config["REVISION_FOLDER"], exist_ok=True)

    def _copy_base_revision(self):
        shutil.copytree(self.base_revision_folder, self.app.config["REVISION_FOLDER"])

    def _revert_and_cleanup(self):
        logging.info("Reverting revision creation.")
        if self.is_initial_revision:
            logging.debug("Revert initialized session folder. Deleting: `{}`".format(self.app.config["SESSION_FOLDER"]))
            remove_json_database_data_tracing_logger(True)
            shutil.rmtree(self.app.config["SESSION_FOLDER"])
        else:
            logging.debug(
                "Revert initialized revision folder. Deleting: `{}`".format(self.app.config["REVISION_FOLDER"])
            )
            remove_json_database_data_tracing_logger(True)
            shutil.rmtree(self.app.config["REVISION_FOLDER"])

    def _generate_session_values(self):
        # Generate the session values: Store some meta information.
        self.app.db.add_object(SessionValue("csv_input_file", self.args.input_csv))
        self.app.db.add_object(SessionValue("csv_fieldnames", self.requirement_collection.csv_meta.fieldnames))
        self.app.db.add_object(SessionValue("csv_id_header", self.requirement_collection.csv_meta.id_header))
        self.app.db.add_object(SessionValue("csv_formal_header", self.requirement_collection.csv_meta.formal_header))
        self.app.db.add_object(SessionValue("csv_type_header", self.requirement_collection.csv_meta.type_header))
        self.app.db.add_object(SessionValue("csv_desc_header", self.requirement_collection.csv_meta.desc_header))
        self.app.db.add_object(SessionValue("csv_hash", hash_file_sha1(self.args.input_csv)))

    def _update_session_values(self):
        # Update the session values: Store some meta information.
        self.app.db.get_object(SessionValue, "csv_input_file").value = self.args.input_csv
        self.app.db.get_object(SessionValue, "csv_fieldnames").value = self.requirement_collection.csv_meta.fieldnames
        self.app.db.get_object(SessionValue, "csv_id_header").value = self.requirement_collection.csv_meta.id_header
        self.app.db.get_object(SessionValue, "csv_formal_header").value = (
            self.requirement_collection.csv_meta.formal_header
        )
        self.app.db.get_object(SessionValue, "csv_type_header").value = self.requirement_collection.csv_meta.type_header
        self.app.db.get_object(SessionValue, "csv_desc_header").value = self.requirement_collection.csv_meta.desc_header
        self.app.db.get_object(SessionValue, "csv_hash").value = hash_file_sha1(self.args.input_csv)

    def _merge_with_base_revision(self):
        # Merge the old revision into the new revision
        logging.info(f"Merging `{self.base_revision_name}` into `{self.revision_name}`.")
        reqs: dict[str, Requirement] = dict(self.app.db.get_objects(Requirement))
        new_reqs: dict[str, Requirement] = {r.rid: r for r in self.requirement_collection.requirements}

        req_ids: set[str] = set(reqs.keys())
        new_req_ids: set[str] = set(new_reqs.keys())

        # delete deleted requirements
        for rid in req_ids.difference(new_req_ids):
            self.app.db.remove_object(reqs[rid])

        # insert and tag new reqs
        revision_tag_name = f"{self.base_revision_name}_to_{self.revision_name}_new_requirement"
        if not self.app.db.key_in_table(Tag, revision_tag_name):
            revision_tag = Tag(revision_tag_name, Color.BS_INFO.value, False, "")
        else:
            revision_tag = self.app.db.get_object(Tag, revision_tag_name)

        for rid in new_req_ids.difference(req_ids):
            logging.info("Add newly introduced requirement `{}`".format(rid))
            new_reqs[rid].tags[revision_tag] = ""
            self.app.db.add_object(new_reqs[rid])

        # updating existing requirements
        data_changed_tag_name = f"{self.base_revision_name}_to_{self.revision_name}_data_changed"
        if not self.app.db.key_in_table(Tag, data_changed_tag_name):
            data_changed_tag = Tag(data_changed_tag_name, Color.BS_INFO.value, False, "")
        else:
            data_changed_tag = self.app.db.get_object(Tag, data_changed_tag_name)

        description_changed_tag_name = f"{self.base_revision_name}_to_{self.revision_name}_description_changed"
        if not self.app.db.key_in_table(Tag, description_changed_tag_name):
            description_changed_tag = Tag(description_changed_tag_name, Color.BS_INFO.value, False, "")
        else:
            description_changed_tag = self.app.db.get_object(Tag, description_changed_tag_name)

        migrated_formalization_tag_name = f"{self.base_revision_name}_to_{self.revision_name}_migrated_formalization"
        if not self.app.db.key_in_table(Tag, migrated_formalization_tag_name):
            migrated_formalization_tag = Tag(migrated_formalization_tag_name, Color.BS_INFO.value, False, "")
        else:
            migrated_formalization_tag = self.app.db.get_object(Tag, migrated_formalization_tag_name)

        for rid in new_req_ids.intersection(req_ids):
            r = reqs[rid]
            new_r = new_reqs[rid]
            # add revision diff and update description, type_in_csv, csv_row and pos_in_csv
            if r.description != new_r.description:
                logging.info(f"Description changed. Add `description_changed` tag to `{rid}`.")
                r.tags[description_changed_tag] = ""
                r.status = "Todo"

            r.revision_diff = new_r

            if len(r.revision_diff) > 0:
                logging.info(f"CSV entry changed. Add `revision_data_changed` tag to `{rid}`.")
                r.tags[data_changed_tag] = ""

            # If the new formalization is empty: just migrate the formalization.
            #  - Tag with `migrated_formalization` if the description changed.
            if len(new_r.formalizations) == 0 and len(r.formalizations) == 0:
                pass
            elif len(new_r.formalizations) == 0 and len(r.formalizations) > 0:
                logging.info("Migrate formalization for `{}`".format(rid))
                if r.description != new_r.description:
                    logging.info(
                        "Add `migrated_formalization` tag to `{}`, status to `Todo` since description changed".format(
                            rid
                        )
                    )
                    r.tags[migrated_formalization_tag] = ""
                    r.status = "Todo"
            elif len(new_r.formalizations) > 0 and len(r.formalizations) == 0:
                logging.error("Parsing of the requirement not supported.")
                raise NotImplementedError
            else:
                logging.error("Parsing of the requirement not supported.")
                raise NotImplementedError

        # Store the updated requirements for the new revision.
        logging.info("Store merge changes to revision `{}`".format(self.revision_name))
        self.app.db.update()


class HanforArgumentParser(argparse.ArgumentParser):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.add_argument("tag", help="A tag for the session. Session will be reloaded, if tag exists.")
        self.add_argument("-c", "--input_csv", help="Path to the csv to be processed.")
        self.add_argument(
            "-r",
            "--revision",
            action="store_true",
            help="Create a new session by updating a existing session with a new csv file.",
        )
        self.add_argument(
            "-rti", "--reload_type_inference", action="store_true", help="Reload the type inference results."
        )
        self.add_argument(
            "-L",
            "--list_stored_sessions",
            nargs=0,
            help="List the tags of stored sessions..",
            action=ListStoredSessions,
            app=self.app,
        )
        self.add_argument(
            "-G",
            "--generate_scoped_pattern_training_data",
            nargs=0,
            help="Generate training data out of description with assigned scoped pattern.",
            action=GenerateScopedPatternTrainingData,
            app=self.app,
        )
        self.add_argument(
            "-hd",
            "--headers",
            type=str,
            help='Header Definition of the form --header=\'{ "csv_id_header": "ID", "csv_desc_header": "Description", '
            '"csv_formal_header": "Hanfor_Formalization", "csv_type_header" : "Type"}\', must be valid json.',
            default=None,
        )


class ListStoredSessions(argparse.Action):
    """List available session tags."""

    def __init__(self, option_strings, app, dest, *args, **kwargs):
        self.app = app
        super(ListStoredSessions, self).__init__(option_strings=option_strings, dest=dest, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        entries = get_stored_session_names(self.app.config["SESSION_BASE_FOLDER"], with_revisions=True)
        data = [["Tag", "Revision", "Last Modified"]]
        for entry in entries:
            revisions = list()
            for name, values in entry["revisions_stats"].items():
                revisions.append((name, values["last_mod"]))
            revisions.sort()
            if len(revisions) > 0:
                data.append([entry["name"], revisions[0][0], revisions[0][1]])
                for i in range(1, len(revisions)):
                    data.append(["", revisions[i][0], revisions[i][1]])
            else:
                data.append([entry["name"], "", ""])
        print("Stored sessions: ")
        if len(data) > 1:
            print(DoubleTable(data).table)
        else:
            print("No sessions in found.")
        exit(0)


class GenerateScopedPatternTrainingData(argparse.Action):
    """Generate training data consisting of requirement descriptions with assigned scoped pattern."""

    def __init__(self, option_strings, app, dest, *args, **kwargs):
        self.app = app
        super(GenerateScopedPatternTrainingData, self).__init__(
            option_strings=option_strings, dest=dest, *args, **kwargs
        )

    def __call__(self, *args, **kwargs):
        # logging.debug(self.app.config)
        entries = get_stored_session_names(self.app.config["SESSION_BASE_FOLDER"])
        result = dict()
        for entry in entries:
            logging.debug("Looking into {}".format(entry[1]))
            current_session_folder = os.path.join(self.app.config["SESSION_BASE_FOLDER"], entry[1])
            revisions = get_available_revisions(self.app.config, folder=current_session_folder)
            for revision in revisions:
                current_revision_folder = os.path.join(str(current_session_folder), revision)
                logging.debug("Processing `{}`".format(current_revision_folder))
                requirements = get_requirements(self.app)
                logging.debug("Found {} requirements .. fetching the formalized ones.".format(len(requirements)))
                used_slugs = set()
                for requirement in requirements:
                    try:
                        if len(requirement.description) == 0:
                            continue
                        slug, used_slugs = clean_identifier_for_ultimate_parser(requirement.rid, 0, used_slugs)
                        result[slug] = dict()
                        result[slug]["desc"] = requirement.description
                        for index, formalization in requirement.formalizations.items():
                            if formalization.scoped_pattern is None:
                                continue
                            if formalization.scoped_pattern.get_scope_slug().lower() == "none":
                                continue
                            if formalization.scoped_pattern.get_pattern_slug() in ["NotFormalizable", "None"]:
                                continue
                            if len(formalization.get_string()) == 0:
                                # formalization string is empty if expressions are missing or none set. Ignore in output
                                continue
                            f_key = "formalization_{}".format(index)
                            result[slug][f_key] = dict()
                            result[slug][f_key]["scope"] = formalization.scoped_pattern.get_scope_slug()
                            result[slug][f_key]["pattern"] = formalization.scoped_pattern.get_pattern_slug()
                            result[slug][f_key]["formalization"] = formalization.get_string()
                    except AttributeError:
                        continue
            with open("training_data.json", mode="w", encoding="utf-8") as f:
                json.dump(result, f)
        exit(0)


def get_stored_session_names(session_folder, only_names=False, with_revisions=False) -> tuple:
    """Get stored session tags (folder names) including os.stat.
    Returned tuple is (
        (os.stat(), name),
        ...
    )
    If only_names == True the tuple is (
        name_1,
        ...
    )
    If with_with_revisions == True the tuple is (
        {
            name: 'name_1',
            'revisions': [revision_1, ...],
            revisions_stats: {
                revision_1: {
                    name: 'revision_1',
                    last_mod: "%A %d. %B %Y at %X" formatted mtime,
                    num_vars: Number of variables used in this revision.
                }
            }
        },
        ...
    )

    Args:
        session_folder (str): path to hanfor data folder.
        only_names (bool): Only return the names (tags).
        with_revisions (bool): Recurse also into the available revisions.

    Returns:
        tuple: Only folder names or stats with names.
    """
    result = ()
    if not session_folder:
        session_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

    try:
        result = [
            (os.path.join(session_folder, file_name), file_name)
            for file_name in os.listdir(session_folder)
            if os.path.isdir(os.path.join(session_folder, file_name))
        ]
        if with_revisions:
            result = (
                {
                    "name": entry[1],
                    "revisions": get_available_revisions(None, entry[0]),
                    "revisions_stats": get_revisions_with_stats(entry[0]),
                }
                for entry in result
            )
        elif only_names:
            result = (entry[1] for entry in result)
        else:
            result = ((os.stat(entry[0]), entry[1]) for entry in result)
    except Exception as e:
        logging.error("Could not fetch stored sessions: {}".format(e))

    return result


def get_revisions_with_stats(session_path):
    """Get meta information about available revisions for a given session path.

    Returns a dict with revision name as key for each revision.
    Each item is then a dict like:
        {
            name: 'revision_1',
            last_mod: %A %d. %B %Y at %X formatted mtime,
            num_vars: 9001
        }


    :param session_path: { revision_1: { name: 'revision_1', last_mod: %A %d. %B %Y at %X, num_vars: 9001} ... }
    """
    revisions = get_available_revisions(None, session_path)
    revisions_stats = dict()
    for revision in revisions:
        revision_path = os.path.join(session_path, revision)
        tmp_db = JsonDatabase(read_only=True)
        add_custom_serializer_to_database(tmp_db)
        tmp_db.init_tables(revision_path)

        revisions_stats[revision] = {
            "name": revision,
            "last_mod": get_last_edit_from_path(revision_path),
            "num_vars": len(tmp_db.get_objects(Variable)),
        }
    return revisions_stats


def get_last_edit_from_path(path_str):
    """Return a human-readable form of the last edit (mtime) for a path.

    :param path_str: str to path.
    :return: "%A %d. %B %Y at %X" formatted mtime
    """
    return datetime.datetime.fromtimestamp(os.stat(path_str).st_mtime).strftime("%A %d. %B %Y at %X")


def add_custom_serializer_to_database(database: JsonDatabase) -> None:

    def scope_serialize(obj: Scope, db_serializer: Callable[[any, str], any], user: str) -> dict:
        return db_serializer(obj.value, user)

    def scope_deserialize(data: dict, db_deserializer: Callable[[any], any]) -> Scope:
        return Scope(db_deserializer(data))

    database.add_custom_serializer(Scope, scope_serialize, scope_deserialize)

    def datetime_serialize(obj: datetime.datetime, db_serializer: Callable[[any, str], any], user: str) -> dict:
        return db_serializer(obj.isoformat(), user)

    def datetime_deserialize(data: dict, db_deserializer: Callable[[any], any]) -> datetime.datetime:
        return datetime.datetime.fromisoformat(db_deserializer(data))

    database.add_custom_serializer(datetime.datetime, datetime_serialize, datetime_deserialize)

    def boogie_type_serialize(
        obj: boogie_parsing.BoogieType, db_serializer: Callable[[any, str], any], user: str
    ) -> dict:
        return db_serializer(obj.value, user)

    def boogie_type_deserialize(data: dict, db_deserializer: Callable[[any], any]) -> boogie_parsing.BoogieType:
        return boogie_parsing.BoogieType(db_deserializer(data))

    database.add_custom_serializer(boogie_parsing.BoogieType, boogie_type_serialize, boogie_type_deserialize)


def get_available_revisions(config, folder=None):
    """Returns available revisions for a given session folder.
    Uses config['SESSION_FOLDER'] if no explicit folder is given.

    :param config:
    :param folder:
    :return:
    """
    result = []

    if folder is None:
        folder = config["SESSION_FOLDER"]

    try:
        names = os.listdir(folder)
        result = [
            name for name in names if os.path.isdir(os.path.join(folder, name)) and re.match(r"revision_[0-9]+", name)
        ]
    except Exception as e:
        logging.error("Could not fetch stored revisions: {}".format(e))

    return result


class PrefixMiddleware(object):
    """Support for url prefixes."""

    def __init__(self, app, prefix=""):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"].startswith(self.prefix):
            environ["PATH_INFO"] = environ["PATH_INFO"][len(self.prefix) :]
            environ["SCRIPT_NAME"] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response("404", [("Content-Type", "text/plain")])
            return ["Sorry, this url does not belong to Hanfor.".encode()]


def hash_file_sha1(path, encoding="utf-8"):
    """Returns md5 hash for a csv (text etc.) file.

    :param path: Path to file to hash.
    :param encoding: Defaults to utf-8
    :return: md5 hash (hex formatted).
    """
    sha1sum = hashlib.sha1()

    with open(path, "r", encoding=encoding) as f:
        while True:
            data = f.readline().encode(encoding=encoding)
            if not data:
                break
            sha1sum.update(data)

    return sha1sum.hexdigest()
