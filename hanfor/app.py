""" 
@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""

import csv
import datetime
import logging
import os
import re
import subprocess
import sys
from functools import wraps, update_wrapper

import flask
from flask import Flask, render_template, request, jsonify, make_response, json
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import HTTPException

import reqtransformer
import utils
from guesser.Guess import Guess
from guesser.guesser_registerer import REGISTERED_GUESSERS
from reqtransformer import Requirement, VariableCollection, Variable, VarImportSessions, Formalization, Scope
from ressources import Report, QueryAPI
from ressources.simulator_ressource import SimulatorRessource
from static_utils import get_filenames_from_dir, pickle_dump_obj_to_file, choice, pickle_load_from_dump, hash_file_sha1
from patterns import PATTERNS, VARIABLE_AUTOCOMPLETE_EXTENSION
from tags.tags import TagsApi

import mimetypes

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/javascript", ".js")


# Create the app
app = Flask(__name__)
app.config.from_object("config")

from example_blueprint import example_blueprint
from tags import tags
from statistics import statistics
from ultimate import ultimate

# Example Blueprint
app.register_blueprint(example_blueprint.blueprint)
app.register_blueprint(example_blueprint.api_blueprint)
# Tags
app.register_blueprint(tags.blueprint)
app.register_blueprint(tags.api_blueprint)
# Statistics
app.register_blueprint(statistics.blueprint)
app.register_blueprint(statistics.api_blueprint)
# ultimate
app.register_blueprint(ultimate.blueprint)
app.register_blueprint(ultimate.api_blueprint)


if "USE_SENTRY" in app.config and app.config["USE_SENTRY"]:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()])

logging.basicConfig(
    format="[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


def nocache(view):
    """Decorator for a flask view. If applied this will prevent caching."""

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Last-Modified"] = datetime.datetime.now()
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return update_wrapper(no_cache, view)


@app.route("/simulator", methods=["GET", "POST", "DELETE"])
@nocache
def simulator():
    return SimulatorRessource(app, request).apply_request()


@app.route("/api/tools/<command>", methods=["GET", "POST"])
@nocache
def tools_api(command):
    filter_list = request.form.get("selected_requirement_ids", "")
    if len(filter_list) > 0:
        filter_list = json.loads(filter_list)
    else:
        filter_list = None

    file_name = f"{app.config['CSV_INPUT_FILE'][:-4]}"

    if command == "req_file":
        content = utils.generate_req_file_content(app, filter_list=filter_list)
        return utils.generate_file_response(content, file_name + ".req")

    if command == "csv_file":
        file = utils.generate_csv_file_content(app, filter_list=filter_list)
        name = f"{app.config['SESSION_TAG']}_{app.config['USING_REVISION']}_out.csv"
        return utils.generate_file_response(file, name, mimetype="text/csv")

    if command == "xls_file":
        file = utils.generate_xls_file_content(app, filter_list=filter_list)
        file.seek(0)
        return flask.send_file(file, download_name=file_name + ".xlsx", as_attachment=True)


@app.route("/api/table/colum_defs", methods=["GET"])
@nocache
def table_api():
    result = utils.get_datatable_additional_cols(app)
    return jsonify(result)


@app.route("/api/query", methods=["GET", "POST", "DELETE"])
@nocache
def api_query():
    return QueryAPI(app, request).apply_request()


@app.route("/api/<resource>/<command>", methods=["GET", "POST", "DELETE"])
@nocache
def api(resource, command):
    resources = ["req", "var", "stats", "tag", "meta", "logs", "report"]
    commands = [
        "get",
        "gets",
        "set",
        "update",
        "delete",
        "new_formalization",
        "new_constraint",
        "del_formalization",
        "del_tag",
        "del_var",
        "multi_update",
        "var_import_info",
        "get_available_guesses",
        "add_formalization_from_guess",
        "multi_add_top_guess",
        "get_constraints_html",
        "del_constraint",
        "add_new_variable",
        "get_enumerators",
        "start_import_session",
        "gen_req",
        "add_standard",
        "import_csv",
    ]
    if resource not in resources or command not in commands:
        return jsonify({"success": False, "errormsg": "sorry, request not supported."}), 404

    if resource == "req":
        # Get a single requirement.
        if command == "get" and request.method == "GET":
            id = request.args.get("id", "")
            requirement = Requirement.load_requirement_by_id(id, app)
            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])

            result = requirement.to_dict(include_used_vars=True)
            result["formalizations_html"] = utils.formalizations_to_html(app, requirement.formalizations)
            result["available_vars"] = var_collection.get_available_var_names_list(
                used_only=False, exclude_types={"ENUM"}
            )

            result["additional_static_available_vars"] = VARIABLE_AUTOCOMPLETE_EXTENSION

            if requirement:
                return jsonify(result)

        # Get all requirements
        if command == "gets":
            filenames = get_filenames_from_dir(app.config["REVISION_FOLDER"])
            result = dict()
            result["data"] = list()
            for filename in filenames:
                try:
                    req = Requirement.load(filename)
                    result["data"].append(req.to_dict())
                except Exception as e:
                    logging.debug(e)
            return jsonify(result)

        # Update a requirement
        if command == "update" and request.method == "POST":
            id = request.form.get("id", "")
            requirement = Requirement.load_requirement_by_id(id, app)
            error = False
            error_msg = ""

            if requirement:
                logging.debug(f"Updating requirement: {requirement.rid}")

                new_status = request.form.get("status", "")
                if requirement.status != new_status:
                    requirement.status = new_status
                    utils.add_msg_to_flask_session_log(app, f"Set status to {new_status} for requirement", id)
                    logging.debug(f"Requirement status set to {requirement.status}")

                new_tag_set = json.loads(request.form.get("tags", ""))
                if requirement.tags != new_tag_set:
                    added_tags = new_tag_set.keys() - requirement.tags.keys()
                    tags = TagsApi()
                    for tag in added_tags:
                        tags.add_if_new(tag)
                    removed_tags = requirement.tags.keys() - new_tag_set.keys()
                    requirement.tags = new_tag_set
                    # do logging
                    utils.add_msg_to_flask_session_log(
                        app, f"Tags: + {added_tags} and - {removed_tags} to requirement", id
                    )
                    logging.debug(f"Tags: + {added_tags} and - {removed_tags} to requirement {requirement.tags}")

                # Update formalization.
                if request.form.get("update_formalization") == "true":
                    formalizations = json.loads(request.form.get("formalizations", ""))
                    logging.debug("Updated Formalizations: {}".format(formalizations))
                    try:
                        requirement.update_formalizations(formalizations, app)
                        utils.add_msg_to_flask_session_log(app, "Updated requirement formalization", id)
                    except KeyError as e:
                        error = True
                        error_msg = f"Could not set formalization: Missing expression/variable for {e}"
                    except Exception as e:
                        error = True
                        error_msg = f"Could not parse formalization: `{e}`"
                else:
                    logging.debug("Skipping formalization update.")

                if error:
                    logging.error(f"We got an error parsing the expressions: {error_msg}. Omitting requirement update.")
                    return jsonify({"success": False, "errormsg": error_msg})
                else:
                    requirement.store()
                    return jsonify(requirement.to_dict()), 200

        # Multi Update Tags or Status.
        if command == "multi_update":
            logging.info("Multi edit requirements.")
            result = {"success": True, "errormsg": ""}

            # Get user Input
            add_tag = request.form.get("add_tag", "").strip()
            remove_tag = request.form.get("remove_tag", "").strip()
            set_status = request.form.get("set_status", "").strip()
            rid_list = request.form.get("selected_ids", "")
            logging.debug(rid_list)
            if len(rid_list) > 0:
                rid_list = json.loads(rid_list)
            else:
                result["success"] = False
                result["errormsg"] = "No requirements selected."

            # Check if the status is valid.
            available_status = ["Todo", "Review", "Done"]
            if len(set_status) > 0 and set_status not in available_status:
                result["success"] = False
                result["errormsg"] = "Status `{}` not supported.\nChoose from `{}`".format(
                    set_status, ", ".join(available_status)
                )

            # Update all requirements given by the rid_list
            if result["success"]:
                log_msg = f"Update {len(rid_list)} requirements."
                if len(add_tag) > 0:
                    log_msg += f"Adding tag `{add_tag}`"
                    utils.add_msg_to_flask_session_log(
                        app, f"Adding tag `{add_tag}` to requirements.", rid_list=rid_list
                    )
                if len(remove_tag) > 0:
                    log_msg += f", removing Tag `{remove_tag}` (is present)"
                    utils.add_msg_to_flask_session_log(
                        app, f"Removing tag `{remove_tag}` from requirements.", rid_list=rid_list
                    )
                if len(set_status) > 0:
                    log_msg += ", set Status=`{}`.".format(set_status)
                    utils.add_msg_to_flask_session_log(
                        app, f"Set status to `{set_status}` for requirements. ", rid_list=rid_list
                    )
                logging.info(log_msg)

                for rid in rid_list:
                    requirement = Requirement.load_requirement_by_id(rid, app)
                    if requirement is None:
                        continue
                    logging.info(f"Updating requirement `{rid}`")
                    if remove_tag in requirement.tags:
                        requirement.tags.pop(remove_tag)
                    if add_tag and add_tag not in requirement.tags:
                        requirement.tags[add_tag] = ""
                    if set_status:
                        requirement.status = set_status
                    requirement.store()

            return jsonify(result)

        # Add a new empty formalization
        if command == "new_formalization" and request.method == "POST":
            id = request.form.get("id", "")
            requirement = Requirement.load_requirement_by_id(id, app)  # type: Requirement
            formalization_id, formalization = requirement.add_empty_formalization()
            requirement.store()
            utils.add_msg_to_flask_session_log(app, "Added new Formalization to requirement", id)
            result = utils.get_formalization_template(app.config["TEMPLATES_FOLDER"], formalization_id, formalization)
            return jsonify(result)

        # Delete a formalization
        if command == "del_formalization" and request.method == "POST":
            result = dict()
            formalization_id = request.form.get("formalization_id", "")
            requirement_id = request.form.get("requirement_id", "")
            requirement = Requirement.load_requirement_by_id(requirement_id, app)
            requirement.delete_formalization(formalization_id, app)
            requirement.store()

            utils.add_msg_to_flask_session_log(app, "Deleted formalization from requirement", requirement_id)
            result["html"] = utils.formalizations_to_html(app, requirement.formalizations)
            return jsonify(result)

        # Get available guesses.
        if command == "get_available_guesses" and request.method == "POST":
            result = {"success": True}
            requirement_id = request.form.get("requirement_id", "")
            requirement = Requirement.load_requirement_by_id(requirement_id, app)
            if requirement is None:
                result["success"] = False
                result["errormsg"] = "Requirement `{}` not found".format(requirement_id)
            else:
                result["available_guesses"] = list()
                tmp_guesses = list()
                var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])

                for guesser in REGISTERED_GUESSERS:
                    try:
                        guesser_instance = guesser(requirement, var_collection, app)
                        guesser_instance.guess()
                        tmp_guesses += guesser_instance.guesses
                    except ValueError as e:
                        result["success"] = False
                        result["errormsg"] = "Could not determine a guess: "
                        result["errormsg"] += e.__str__()

                tmp_guesses = sorted(tmp_guesses, key=Guess.eval_score)
                guesses = list()
                for g in tmp_guesses:
                    if type(g) is list:
                        guesses += g
                    else:
                        guesses.append(g)

                for score, scoped_pattern, mapping in guesses:
                    result["available_guesses"].append(
                        {
                            "scope": scoped_pattern.scope.name,
                            "pattern": scoped_pattern.pattern.name,
                            "mapping": mapping,
                            "string": scoped_pattern.get_string(mapping),
                        }
                    )

            return jsonify(result)

        if command == "add_formalization_from_guess" and request.method == "POST":
            requirement_id = request.form.get("requirement_id", "")
            scope = request.form.get("scope", "")
            pattern = request.form.get("pattern", "")
            mapping = request.form.get("mapping", "")
            mapping = json.loads(mapping)

            # Add an empty Formalization.
            requirement = Requirement.load_requirement_by_id(requirement_id, app)
            formalization_id, formalization = requirement.add_empty_formalization()
            # Add content to the formalization.
            requirement.update_formalization(
                formalization_id=formalization_id, scope_name=scope, pattern_name=pattern, mapping=mapping, app=app
            )
            requirement.store()
            utils.add_msg_to_flask_session_log(app, "Added formalization guess to requirement", requirement_id)

            result = utils.get_formalization_template(
                app.config["TEMPLATES_FOLDER"], formalization_id, requirement.formalizations[formalization_id]
            )

            return jsonify(result)

        if command == "multi_add_top_guess" and request.method == "POST":
            result = {"success": True}
            requirement_ids = request.form.get("selected_ids", "")
            insert_mode = request.form.get("insert_mode", "append")
            if len(requirement_ids) > 0:
                requirement_ids = json.loads(requirement_ids)
            else:
                result["success"] = False
                result["errormsg"] = "No requirements selected."

            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            for req_id in requirement_ids:
                requirement = Requirement.load_requirement_by_id(req_id, app)
                if requirement is not None:
                    logging.info("Add top guess to requirement `{}`".format(req_id))
                    tmp_guesses = list()
                    for guesser in REGISTERED_GUESSERS:
                        try:
                            guesser_instance = guesser(requirement, var_collection, app)
                            guesser_instance.guess()
                            tmp_guesses += guesser_instance.guesses
                            tmp_guesses = sorted(tmp_guesses, key=Guess.eval_score)
                            if len(tmp_guesses) > 0:
                                if type(tmp_guesses[0]) is Guess:
                                    top_guesses = [tmp_guesses[0]]
                                elif type(tmp_guesses[0]) is list:
                                    top_guesses = tmp_guesses[0]
                                else:
                                    raise TypeError("Type: `{}` not supported as guesses".format(type(tmp_guesses[0])))
                                if insert_mode == "override":
                                    for f_id in requirement.formalizations.keys():
                                        requirement.delete_formalization(f_id, app)
                                for score, scoped_pattern, mapping in top_guesses:
                                    formalization_id, formalization = requirement.add_empty_formalization()
                                    # Add content to the formalization.
                                    requirement.update_formalization(
                                        formalization_id=formalization_id,
                                        scope_name=scoped_pattern.scope.name,
                                        pattern_name=scoped_pattern.pattern.name,
                                        mapping=mapping,
                                        app=app,
                                    )
                                    requirement.store()

                        except ValueError as e:
                            result["success"] = False
                            result["errormsg"] = "Could not determine a guess: "
                            result["errormsg"] += e.__str__()
            utils.add_msg_to_flask_session_log(app, "Added top guess to requirements", rid_list=requirement_ids)

            return jsonify(result)

    if resource == "var":
        # Get available variables
        result = {"success": False, "errormsg": "sorry, request not supported."}
        if command == "gets":
            result = {"data": utils.get_available_vars(app, full=True, fetch_evals=True)}
        elif command == "update":
            result = utils.update_variable_in_collection(app, request)
        elif command == "var_import_info":
            result = utils.varcollection_diff_info(app, request)
            varcollection_consistency_check(app)
        elif command == "multi_update":
            logging.info("Multi edit Variables.")
            result = {"success": True, "errormsg": ""}

            # Get user Input.
            change_type = request.form.get("change_type", "").strip()
            var_list = request.form.get("selected_vars", "")
            delete = request.form.get("del", "false")
            if len(var_list) > 0:
                var_list = json.loads(var_list)
            else:
                result["success"] = False
                result["errormsg"] = "No variables selected."

            # Update all requirements given by the rid_list
            if result["success"]:
                if len(change_type) > 0:  # Change the var type.
                    logging.debug("Change type to `{}`.\nAffected Vars:\n{}".format(change_type, "\n".join(var_list)))
                    var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
                    for var_name in var_list:
                        try:
                            logging.debug(
                                "Set type for `{}` to `{}`. Formerly was `{}`".format(
                                    var_name, change_type, var_collection.collection[var_name].type
                                )
                            )
                            var_collection.collection[var_name].set_type(change_type)
                        except KeyError:
                            logging.debug("Variable `{}` not found".format(var_list))
                    var_collection.store()

                if delete == "true":
                    logging.info("Deleting variables.\nAffected Vars:\n{}".format("\n".join(var_list)))
                    var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
                    for var_name in var_list:
                        try:
                            logging.debug("Deleting `{}`".format(var_name))
                            var_collection.del_var(var_name)
                        except KeyError:
                            logging.debug("Variable `{}` not found".format(var_list))
                    var_collection.store()

            return jsonify(result)
        elif command == "new_constraint":
            result = {"success": True, "errormsg": ""}
            var_name = request.form.get("name", "").strip()

            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            cid = var_collection.add_new_constraint(var_name=var_name)
            var_collection.store()
            result["html"] = utils.formalizations_to_html(
                app, {cid: var_collection.collection[var_name].constraints[cid]}
            )
            return jsonify(result)
        elif command == "get_constraints_html":
            result = {
                "success": True,
                "errormsg": "",
                "html": "<p>No constraints set.</p>",
                "type_inference_errors": dict(),
            }
            var_name = request.form.get("name", "").strip()
            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            try:
                var = var_collection.collection[var_name]
                var_dict = var.to_dict(var_collection.var_req_mapping)
                result["html"] = utils.formalizations_to_html(app, var.constraints)
                result["type_inference_errors"] = var_dict["type_inference_errors"]
            except AttributeError:
                pass

            return jsonify(result)

        elif command == "del_constraint":
            result = {"success": True, "errormsg": ""}
            var_name = request.form.get("name", "").strip()
            constraint_id = int(request.form.get("constraint_id", "").strip())

            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            var_collection.del_constraint(var_name=var_name, constraint_id=constraint_id)
            var_collection.collection[var_name].reload_constraints_type_inference_errors(var_collection)
            var_collection.store()
            result["html"] = utils.formalizations_to_html(app, var_collection.collection[var_name].get_constraints())
            return jsonify(result)

        elif command == "del_var":
            result = {"success": True, "errormsg": ""}
            var_name = request.form.get("name", "").strip()

            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            try:
                logging.debug("Deleting `{}`".format(var_name))
                success = var_collection.del_var(var_name)
                if not success:
                    result = {"success": False, "errormsg": "Variable is used and thus cannot be deleted."}
                var_collection.store()
            except KeyError:
                logging.debug("Variable `{}` not found".format(var_name))
                result = {"success": False, "errormsg": "Variable not found."}
            return jsonify(result)
        elif command == "add_new_variable":
            result = {"success": True, "errormsg": ""}
            variable_name = request.form.get("name", "").strip()
            variable_type = request.form.get("type", "").strip()
            variable_value = request.form.get("value", "").strip()
            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])

            # Apply some tests if the new Variable is legal.
            if len(variable_name) == 0 or not re.match("^[a-zA-Z][a-zA-Z0-9_]+$", variable_name):
                result = {
                    "success": False,
                    "errormsg": "Illegal Variable name. Start with a char followed by alphanumeric + {_}.",
                }
            elif var_collection.var_name_exists(variable_name):
                result = {"success": False, "errormsg": "`{}` is already existing.".format(variable_name)}
            elif variable_type not in ["ENUM_INT", "ENUM_REAL", "REAL", "INT", "BOOL", "CONST"]:
                result = {"success": False, "errormsg": "`{}` Is not a valid Variable type.".format(variable_type)}
            if variable_type == "CONST":
                try:
                    float(variable_value)
                except Exception:
                    result = {"success": False, "errormsg": "Const value not valid."}
            # We passed all tests, so add the new variable.
            if result["success"]:
                logging.debug("Adding new Variable `{}` to Variable collection.".format(variable_name))
                new_variable = Variable(variable_name, variable_type, None)
                var_collection.add_var(variable_name, new_variable)
                if variable_type == "CONST":
                    var_collection.collection[variable_name].value = variable_value
                var_collection.store()
                var_collection.reload_script_results(app, [variable_name])
                return jsonify(result)
        elif command == "get_enumerators":
            result = {"success": True, "errormsg": ""}
            enum_name = request.form.get("name", "").strip()
            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            enumerators = var_collection.get_enumerators(enum_name)
            enum_results = [(enumerator.name, enumerator.value) for enumerator in enumerators]
            try:
                enum_results.sort(key=lambda x: float(x[1]))
            except Exception as e:
                logging.info(f"Cloud not sort ENUMERATORS: {e}")
            result["enumerators"] = enum_results

            return jsonify(result)
        elif command == "start_import_session":
            result = {"success": True, "errormsg": ""}
            # create a new import session.
            source_session_name = request.form.get("sess_name", "").strip()
            source_revision_name = request.form.get("sess_revision", "").strip()

            result["session_id"] = utils.varcollection_create_new_import_session(
                app=app, source_session_name=source_session_name, source_revision_name=source_revision_name
            )

            if result["session_id"] < 0:
                result["success"] = False
                result["errormsg"] = "Could not create the import session."

            return jsonify(result)
        elif command == "gen_req":
            content = utils.generate_req_file_content(app, variables_only=True)
            name = "{}_variables_only.req".format(app.config["CSV_INPUT_FILE"][:-4])

            return utils.generate_file_response(content, name)
        elif command == "import_csv":
            result = {"success": True, "errormsg": ""}

            variables_csv_str = request.form.get("variables_csv_str", "")
            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])

            dict_reader = csv.DictReader(variables_csv_str.splitlines())
            variables = list(dict_reader)

            missing_fieldnames = {"name", "enum_name", "description", "type", "value", "constraint"}.difference(
                dict_reader.fieldnames
            )
            if len(missing_fieldnames) > 0:
                result["errormsg"] = f"Import failed due to missing fieldnames: {missing_fieldnames}."
                result["success"] = False
                return jsonify(result)

            for variable in variables:
                if variable["name"] == "" or var_collection.var_name_exists(variable["name"]):
                    continue

                var_collection.add_var(variable["name"])
                var_collection.collection[variable["name"]].belongs_to_enum = variable["enum_name"]
                var_collection.set_type(variable["name"], variable["type"])
                var_collection.collection[variable["name"]].value = variable["value"]
                var_collection.collection[variable["name"]].description = variable["description"]

                if variable["constraint"] != "":
                    constraint_id = var_collection.collection[variable["name"]].add_constraint()
                    var_collection.collection[variable["name"]].update_constraint(
                        constraint_id,
                        Scope.GLOBALLY.name,
                        "Universality",
                        {"R": variable["constraint"]},
                        var_collection,
                    )

            var_collection.store()

        return jsonify(result)

    if resource == "meta":
        if command == "get":
            return jsonify(utils.MetaSettings(app.config["META_SETTINGS_PATH"]).__dict__)

    if resource == "logs":
        if command == "get":
            return utils.get_flask_session_log(app, html=True)

    if resource == "report":
        return Report(app, request).apply_request()

    return jsonify({"success": False, "errormsg": "This is not an api-enpoint."}), 404


@app.route("/variable_import/<id>", methods=["GET"])
@nocache
def variable_import(id):
    return render_template("variables/variable-import-session.html", id=id, query=request.args, patterns=PATTERNS)


@app.route("/variable_import/api/<session_id>/<command>", methods=["GET", "POST"])
@nocache
def var_import_session(session_id, command):
    result = {
        "success": False,
    }
    var_import_sessions = VarImportSessions.load_for_app(app.config["SESSION_BASE_FOLDER"])

    if command == "get_var":
        result = dict()
        name = request.form.get("name", "")
        which_collection = request.form.get("which_collection", "")

        try:
            var_collection = var_import_sessions.import_sessions[int(session_id)]
            if which_collection == "source_link":
                var_collection = var_collection.source_var_collection
            if which_collection == "target_link":
                var_collection = var_collection.target_var_collection
            if which_collection == "result_link":
                var_collection = var_collection.result_var_collection
            result = var_collection.collection[name].to_dict(var_collection.var_req_mapping)
            return jsonify(result), 200
        except Exception:
            logging.info("Could not load var: {} from import session: {}".format(name, session_id))

    if command == "get_table_data":
        result = dict()
        try:
            result = {"data": var_import_sessions.import_sessions[int(session_id)].to_datatables_data()}
            return jsonify(result), 200
        except Exception as e:
            logging.info("Could not load session with id: {} ({})".format(session_id, e))
            raise e

    if command == "store_table":
        rows = json.loads(request.form.get("rows", ""))
        try:
            logging.info("Store changes for variable import session: {}".format(session_id))
            var_import_sessions.import_sessions[int(session_id)].store_changes(rows)
            var_import_sessions.store()
            result["success"] = True
            return jsonify(result), 200
        except Exception as e:
            logging.info("Could not store table: {}".format(e))
            result["success"] = False
            result["errormsg"] = "Could not store: {}".format(e)

    if command == "store_variable":
        row = json.loads(request.form.get("row", ""))
        try:
            logging.info('Store changes for variable "{}" of import session: {}'.format(row["name"], session_id))
            var_import_sessions.import_sessions[int(session_id)].store_variable(row)
            var_import_sessions.store()
            result["success"] = True
            return jsonify(result), 200
        except Exception as e:
            logging.info("Could not store table: {}".format(e))
            result["success"] = False
            result["errormsg"] = "Could not store: {}".format(e)

    if command == "apply_import":
        try:
            logging.info("Apply import for variable import session: {}".format(session_id))
            var_import_sessions.import_sessions[int(session_id)].apply_constraint_selection()
            var_import_sessions.store()
            var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
            import_collection = var_import_sessions.import_sessions[int(session_id)].result_var_collection
            var_collection.import_session(import_collection)
            var_collection.store()
            varcollection_consistency_check(app)
            result["success"] = True
            return jsonify(result), 200
        except Exception as e:
            logging.info("Could not apply import: {}".format(e))
            result["success"] = False
            result["errormsg"] = "Could not apply import: {}".format(e)

    if command == "delete_me":
        try:
            logging.info(f"Deleting variable import session id: {session_id}")
            var_import_sessions.import_sessions.pop(int(session_id))
            var_import_sessions.store()
            result["success"] = True
            return jsonify(result), 200
        except Exception as e:
            error_msg = f"Could not delete session with id {session_id} due to: {e}"
            logging.info(error_msg)
            result["success"] = False
            result["errormsg"] = error_msg

    return jsonify(result), 400


@app.route("/<site>")
def site(site):
    available_sites = [
        "help",
        # 'statistics',
        "variables",
        # 'tags'
    ]
    if site in available_sites:
        if site == "variables":
            available_sessions = utils.get_stored_session_names(
                app.config["SESSION_BASE_FOLDER"], only_names=True, with_revisions=True
            )
            running_import_sessions = VarImportSessions.load_for_app(app.config["SESSION_BASE_FOLDER"]).info()
            return render_template(
                "{}.html".format(site + "/" + site),
                available_sessions=available_sessions,
                running_import_sessions=running_import_sessions,
                query=request.args,
                patterns=PATTERNS,
            )
        else:
            return render_template("{}.html".format(site + "/" + site), query=request.args, patterns=PATTERNS)
    else:
        return render_template("404.html", query=request.args), 404


@app.route("/")
def index():
    default_cols = [
        {"name": "Pos", "target": 1},
        {"name": "Id", "target": 2},
        {"name": "Description", "target": 3},
        {"name": "Type", "target": 4},
        {"name": "Tags", "target": 5},
        {"name": "Status", "target": 6},
        {"name": "Formalization", "target": 7},
    ]
    additional_cols = utils.get_datatable_additional_cols(app)["col_defs"]
    return render_template(
        "index.html", query=request.args, additional_cols=additional_cols, default_cols=default_cols, patterns=PATTERNS
    )


"""
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: {}'.format(error))
    logging.error(error)

    return jsonify({
        'success': False,
        'errormsg': 'Server Error: {}'.format(error)
    })


@app.errorhandler(Exception)
def unhandled_exception(exception):
    if hasattr(exception, 'code') and exception.code in range(300, 309):
        return exception

    app.logger.error('Unhandled Exception: {}'.format(exception))
    logging.exception(exception)

    return jsonify({
        'success': False,
        'errormsg': repr(exception)
    })
"""


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


def varcollection_version_migrations(app, args):
    """migrate old collection format"""
    try:
        VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
    except ImportError:
        # The "old" var_collection before the refactoring.
        sys.modules["reqtransformer.reqtransformer"] = reqtransformer
        sys.modules["reqtransformer.patterns"] = reqtransformer

        var_collection = utils.pickle_load_from_dump(app.config["SESSION_VARIABLE_COLLECTION"])
        vars_to_collection = list()
        for name, var in var_collection.items():
            vars_to_collection.append({"name": name, "type": var.type, "value": var.value})
        del sys.modules["reqtransformer.reqtransformer"]
        del sys.modules["reqtransformer.patterns"]

        new_var_collection = VariableCollection(path=app.config["SESSION_VARIABLE_COLLECTION"])
        for var in vars_to_collection:
            new_var_collection.collection[var["name"]] = Variable(var["name"], var["type"], var["value"])
        new_var_collection.store()
        logging.info("Migrated old collection.")


def varcollection_consistency_check(app, args=None):
    logging.info("Check Variables for consistency.")
    # Update usages and constraint type check.
    var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])
    if args is not None and args.reload_type_inference:
        var_collection.reload_type_inference_errors_in_constraints()

    update_var_usage(var_collection)
    var_collection.reload_script_results(app)
    var_collection.store()


def metasettings_version_migration(app, args):
    logging.info("Running metaconfig version migration...")
    meta_settings = utils.MetaSettings(app.config["META_SETTINGS_PATH"])

    meta_settings_keys = ["tag_colors", "tag_descriptions", "tag_internal"]
    for key in meta_settings_keys:
        if key not in meta_settings:
            logging.info(f"Upgrading metaconfig with empty `{key}` store.")
            meta_settings[key] = dict()
    for filename in get_filenames_from_dir(app.config["REVISION_FOLDER"]):
        try:
            req = Requirement.load(filename)
        except TypeError:
            continue
        for tag in req.tags:
            if tag not in meta_settings["tag_colors"]:
                meta_settings["tag_colors"][tag] = "#5bc0de"
            if tag not in meta_settings["tag_descriptions"]:
                meta_settings["tag_descriptions"][tag] = ""
            if tag not in meta_settings["tag_internal"]:
                meta_settings["tag_internal"][tag] = False

    # TODO: Hacky. @Vincent pls fix
    for tag in meta_settings["tag_colors"].keys():
        if tag not in meta_settings["tag_internal"]:
            meta_settings["tag_internal"][tag] = False

    meta_settings.update_storage()


def requirements_version_migrations(app, args):
    logging.info("Running requirements version migration...")
    filenames = get_filenames_from_dir(app.config["REVISION_FOLDER"])
    var_collection = VariableCollection.load(app.config["SESSION_VARIABLE_COLLECTION"])

    for filename in filenames:
        try:
            req = Requirement.load(filename)
        except TypeError:
            continue
        changes = False
        if req.formalizations is None:
            req.formalizations = dict()
            changes = True
        if isinstance(req.tags, set):
            sanitize = lambda t: t.replace("<", "leq").replace(">", "geq")
            req.tags = {sanitize(tag): "" for tag in req.tags}
            changes = True
        if isinstance(req.tags, dict):
            # clean up old data sets  with empty tags that mess up exporting (if necessary)
            new_tags = {tag: comment for tag, comment in req.tags.items() if tag != ""}
            if new_tags != req.tags:
                req.tags = new_tags
                changes = True
        if type(req.type_in_csv) is tuple:
            changes = True
            req.type_in_csv = req.type_in_csv[0]
        if type(req.csv_row) is tuple:
            changes = True
            req.csv_row = req.csv_row[0]
        if type(req.description) is tuple:
            changes = True
            req.description = req.description[0]
        # Derive type inference errors if not set.
        try:
            for i, f in req.formalizations.items():
                if not hasattr(f, "id") or not f.id:
                    changes = True
                    setattr(f, "id", i)
        except Exception as e:
            logging.info(f"Something when updating formalisations went terribly wrong `{req.rid}:\n {e}`")
        # ensure some well-formedness of requirements objects
        for k, f in req.formalizations.items():
            if not isinstance(f, Formalization):
                del req.formalizations[k]
                changes = True
            else:
                if not f.scoped_pattern:
                    f.scoped_pattern = reqtransformer.ScopedPattern()
                    changes = True
                if not f.scoped_pattern.scope or not f.scoped_pattern.pattern:
                    f.scoped_pattern = reqtransformer.ScopedPattern()
                    changes = True
            # Add tags for requirements with (incomplete) formalizations.
            if (
                f.scoped_pattern.scope != reqtransformer.Scope.NONE
                and f.scoped_pattern.pattern.name != "NotFormalizable"
            ):
                req.tags["has_formalization"] = ""
                changes = True
            else:
                req.tags["incomplete_formalization"] = req.format_incomplete_formalization_tag(f.id)
                changes = True
        if args.reload_type_inference:
            req.reload_type_inference(var_collection, app)
        if changes:
            req.store()

    update_var_usage(var_collection)


def create_revision(args, base_revision_name):
    """Create new revision.

    :param args: Parser arguments
    :param base_revision_name: Name of revision the created will be based on. Creates initial revision_0 if none given.
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
    app.config["SESSION_STATUS_PATH"] = os.path.join(app.config["REVISION_FOLDER"], "session_status.pickle")


def user_request_new_revision(args):
    """Asks the user about the base revision and triggers create_revision with the user choice.

    :param args:
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
    create_revision(args, base_revision_choice)


def set_session_config_vars(args, HERE):
    """Initialize config vars:
    SESSION_TAG,
    SESSION_FOLDER
    for current session.

    :param args: Parsed arguments.
    """
    app.config["SESSION_TAG"] = args.tag
    if app.config["SESSION_BASE_FOLDER"] is None:
        app.config["SESSION_BASE_FOLDER"] = os.path.join(HERE, "data")
    app.config["SESSION_FOLDER"] = os.path.join(app.config["SESSION_BASE_FOLDER"], app.config["SESSION_TAG"])


def init_import_sessions():
    """Create import session file"""
    var_import_sessions_path = os.path.join(app.config["SESSION_BASE_FOLDER"], "variable_import_sessions.pickle")
    try:
        VarImportSessions.load(var_import_sessions_path)
    except FileNotFoundError:
        var_import_sessions = VarImportSessions(path=var_import_sessions_path)
        var_import_sessions.store()


def init_meta_settings():
    """Create meta setting file"""
    app.config["META_SETTINGS_PATH"] = os.path.join(app.config["SESSION_FOLDER"], "meta_settings.pickle")
    if not os.path.exists(app.config["META_SETTINGS_PATH"]):
        meta_settings = dict()
        meta_settings["tag_colors"] = dict()
        pickle_dump_obj_to_file(meta_settings, app.config["META_SETTINGS_PATH"])


def init_frontend_logs():
    """Initializes FRONTEND_LOGS_PATH and creates a new frontend_logs dict, if none is existent."""
    app.config["FRONTEND_LOGS_PATH"] = os.path.join(app.config["SESSION_FOLDER"], "frontend_logs.pickle")
    if not os.path.exists(app.config["FRONTEND_LOGS_PATH"]):
        frontend_logs = dict()
        frontend_logs["hanfor_log"] = list()
        pickle_dump_obj_to_file(frontend_logs, app.config["FRONTEND_LOGS_PATH"])


def init_script_eval_results():
    app.config["SCRIPT_EVAL_RESULTS_PATH"] = os.path.join(app.config["SESSION_FOLDER"], "script_eval_results.pickle")
    if not os.path.exists(app.config["SCRIPT_EVAL_RESULTS_PATH"]):
        script_eval_results = reqtransformer.ScriptEvals(path=app.config["SCRIPT_EVAL_RESULTS_PATH"])
        script_eval_results.store()


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


def set_app_config_paths(args, HERE):
    app.config["SCRIPT_UTILS_PATH"] = os.path.join(HERE, "script_utils")
    app.config["TEMPLATES_FOLDER"] = os.path.join(HERE, "templates")


def startup_hanfor(args, HERE) -> bool:
    """Setup session config Variables.
     Trigger:
     Revision creation/loading.
     Variable script evaluation.
     Version migrations.
     Consistency checks.

    :param args:
    :returns: True if startup should continue
    """
    set_session_config_vars(args, HERE)
    set_app_config_paths(args, HERE)

    # Create a new revision if requested.
    if args.revision:
        if args.input_csv is None:
            utils.HanforArgumentParser(app).error("--revision requires a Input CSV -c INPUT_CSV.")
        user_request_new_revision(args)
    else:
        # If there is no session with given tag: Create a new (initial) revision.
        if not os.path.exists(app.config["SESSION_FOLDER"]):
            create_revision(args, None)
        # If this is an already existing session, ask the user which revision to start.
        else:
            revision_choice = user_choose_start_revision()
            logging.info("Loading session `{}` at `{}`".format(app.config["SESSION_TAG"], revision_choice))
            load_revision(revision_choice)

    # Check CSV file change.
    session_dict = pickle_load_from_dump(app.config["SESSION_STATUS_PATH"])  # type: dict
    if args.input_csv:
        logging.info("Check CSV integrity.")
        csv_hash = hash_file_sha1(args.input_csv)
        if "csv_hash" not in session_dict:
            session_dict["csv_hash"] = csv_hash
        if csv_hash != session_dict["csv_hash"]:
            print(f"Sha-1 hash mismatch between: \n`{session_dict['csv_input_file']}`\nand\n`{args.input_csv}`.")
            print("Consider starting a new revision.\nShould I stop loading?")
            if choice(["Yes", "No"], default="Yes") == "Yes":
                return False
            session_dict["csv_hash"] = csv_hash
        session_dict["csv_input_file"] = args.input_csv

    app.config["CSV_INPUT_FILE"] = os.path.basename(session_dict["csv_input_file"])
    app.config["CSV_INPUT_FILE_PATH"] = session_dict["csv_input_file"]

    pickle_dump_obj_to_file(session_dict, app.config["SESSION_STATUS_PATH"])

    # Initialize variables collection, import session, meta settings.
    init_script_eval_results()
    utils.init_var_collection(app)
    init_import_sessions()
    init_meta_settings()
    init_frontend_logs()
    utils.config_check(app.config)

    # Run version migrations
    varcollection_version_migrations(app, args)
    requirements_version_migrations(app, args)
    metasettings_version_migration(app, args)

    # Run consistency checks.
    varcollection_consistency_check(app, args)
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
    args = utils.HanforArgumentParser(app).parse_args()
    if startup_hanfor(args, HERE):
        app.run(**get_app_options())
