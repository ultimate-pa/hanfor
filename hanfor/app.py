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
from functools import wraps, update_wrapper

import flask
from flask import render_template, request, jsonify, make_response, json
from hanfor_falsk import HanforFlask
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import HTTPException

from typing import Callable
from json_db_connector.json_db import JsonDatabase

from boogie_parsing import BoogieType
import utils
from guesser.Guess import Guess
from guesser.guesser_registerer import REGISTERED_GUESSERS
from reqtransformer import Requirement, VariableCollection, Variable, Scope
from ressources import Reports, QueryAPI
from ressources.simulator_ressource import SimulatorRessource
from static_utils import (
    get_filenames_from_dir,
    choice,
    hash_file_sha1,
    SessionValue,
)
from patterns import PATTERNS, VARIABLE_AUTOCOMPLETE_EXTENSION
from tags.tags import TagsApi

import mimetypes

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/javascript", ".js")


# Create the app
app = HanforFlask(__name__)
# app = Flask(__name__)
app.config.from_object("config")
app.db = None

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
        response.headers["Last-Modified"] = str(datetime.datetime.now())
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
            requirement = app.db.get_object(Requirement, id)
            var_collection = VariableCollection(app)

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
            reqs = app.db.get_objects(Requirement)
            result["data"] = [reqs[k].to_dict() for k in sorted(reqs.keys())]
            return jsonify(result)

        # Update a requirement
        if command == "update" and request.method == "POST":
            id = request.form.get("id", "")
            requirement = app.db.get_object(Requirement, id)
            error = False
            error_msg = ""

            if requirement:
                logging.debug(f"Updating requirement: {requirement.rid}")

                new_status = request.form.get("status", "")
                if requirement.status != new_status:
                    requirement.status = new_status
                    utils.add_msg_to_flask_session_log(
                        app, f"Set status to {new_status} for requirement", [requirement]
                    )
                    logging.debug(f"Requirement status set to {requirement.status}")

                new_tag_set = json.loads(request.form.get("tags", ""))
                req_tags = {t.name: c for t, c in requirement.tags.items()}
                if req_tags != new_tag_set:
                    added_tags = new_tag_set.keys() - req_tags.keys()
                    tag_api = TagsApi()
                    removed_tags = req_tags.keys() - new_tag_set.keys()
                    for tag in removed_tags:
                        if not tag_api.tag_exists(tag):
                            continue
                        requirement.tags.pop(tag_api.get_tag(tag))
                    for tag, comment in new_tag_set.items():
                        if not tag_api.tag_exists(tag):
                            tag_api.add(tag)
                        requirement.tags[tag_api.get_tag(tag)] = comment
                    # do logging
                    utils.add_msg_to_flask_session_log(
                        app, f"Tags: + {added_tags} and - {removed_tags} to requirement", [requirement]
                    )
                    logging.debug(f"Tags: + {added_tags} and - {removed_tags} to requirement {requirement.rid}")

                # Update formalization.
                if request.form.get("update_formalization") == "true":
                    formalizations = json.loads(request.form.get("formalizations", ""))
                    logging.debug("Updated Formalizations: {}".format(formalizations))
                    try:
                        requirement.update_formalizations(formalizations, app)
                        utils.add_msg_to_flask_session_log(app, "Updated requirement formalization", [requirement])
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
                    app.db.update()
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
                tag_api = TagsApi()
                requirements = [app.db.get_object(Requirement, rid) for rid in rid_list]
                log_msg = f"Update {len(rid_list)} requirements."
                if len(add_tag) > 0:
                    log_msg += f"Adding tag `{add_tag}`"
                    utils.add_msg_to_flask_session_log(app, f"Adding tag `{add_tag}` to requirements.", requirements)
                    if not tag_api.tag_exists(add_tag):
                        tag_api.add(add_tag)
                    add_tag = tag_api.get_tag(add_tag)
                else:
                    add_tag = None
                if len(remove_tag) > 0:
                    log_msg += f", removing Tag `{remove_tag}` (is present)"
                    utils.add_msg_to_flask_session_log(
                        app, f"Removing tag `{remove_tag}` from requirements.", requirements
                    )
                    if not tag_api.tag_exists(remove_tag):
                        remove_tag = None
                    else:
                        remove_tag = tag_api.get_tag(remove_tag)
                else:
                    remove_tag = None
                if len(set_status) > 0:
                    log_msg += ", set Status=`{}`.".format(set_status)
                    utils.add_msg_to_flask_session_log(
                        app, f"Set status to `{set_status}` for requirements. ", requirements
                    )
                logging.info(log_msg)

                for requirement in requirements:
                    logging.info(f"Updating requirement `{requirement.rid}`")
                    if remove_tag and remove_tag in requirement.tags:
                        requirement.tags.pop(remove_tag)
                    if add_tag and add_tag not in requirement.tags:
                        requirement.tags[add_tag] = ""
                    if set_status:
                        requirement.status = set_status
                app.db.update()

            return jsonify(result)

        # Add a new empty formalization
        if command == "new_formalization" and request.method == "POST":
            id = request.form.get("id", "")
            requirement = app.db.get_object(Requirement, id)  # type: Requirement
            formalization_id, formalization = requirement.add_empty_formalization()
            app.db.update()
            utils.add_msg_to_flask_session_log(app, "Added new Formalization to requirement", [requirement])
            result = utils.get_formalization_template(app.config["TEMPLATES_FOLDER"], formalization_id, formalization)
            return jsonify(result)

        # Delete a formalization
        if command == "del_formalization" and request.method == "POST":
            result = dict()
            formalization_id = request.form.get("formalization_id", "")
            requirement_id = request.form.get("requirement_id", "")
            requirement = app.db.get_object(Requirement, requirement_id)
            requirement.delete_formalization(formalization_id, app)
            app.db.update()

            utils.add_msg_to_flask_session_log(app, "Deleted formalization from requirement", [requirement])
            result["html"] = utils.formalizations_to_html(app, requirement.formalizations)
            return jsonify(result)

        # Get available guesses.
        if command == "get_available_guesses" and request.method == "POST":
            result = {"success": True}
            requirement_id = request.form.get("requirement_id", "")
            requirement = app.db.get_object(Requirement, requirement_id)
            if requirement is None:
                result["success"] = False
                result["errormsg"] = "Requirement `{}` not found".format(requirement_id)
            else:
                result["available_guesses"] = list()
                tmp_guesses = list()
                var_collection = VariableCollection(app)

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
            requirement = app.db.get_object(Requirement, requirement_id)
            formalization_id, formalization = requirement.add_empty_formalization()
            # Add content to the formalization.
            requirement.update_formalization(
                formalization_id=formalization_id, scope_name=scope, pattern_name=pattern, mapping=mapping, app=app
            )
            app.db.update()
            utils.add_msg_to_flask_session_log(app, "Added formalization guess to requirement", [requirement])

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

            if not result["success"]:
                return jsonify(result)

            var_collection = VariableCollection(app)
            requirements = [app.db.get_object(Requirement, rid) for rid in requirement_ids]
            for requirement in requirements:
                if requirement is not None:
                    logging.info("Add top guess to requirement `{}`".format(requirement.rid))
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
                                    app.db.update()

                        except ValueError as e:
                            result["success"] = False
                            result["errormsg"] = "Could not determine a guess: "
                            result["errormsg"] += e.__str__()
            utils.add_msg_to_flask_session_log(app, "Added top guess to requirements", requirements)

            return jsonify(result)

    if resource == "var":
        # Get available variables
        result = {"success": False, "errormsg": "sorry, request not supported."}
        if command == "gets":
            result = {"data": utils.get_available_vars(app, full=True)}
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
                    var_collection = VariableCollection(app)
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
                    var_collection = VariableCollection(app)
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

            var_collection = VariableCollection(app)
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
            var_collection = VariableCollection(app)
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

            var_collection = VariableCollection(app)
            var_collection.del_constraint(var_name=var_name, constraint_id=constraint_id)
            var_collection.collection[var_name].reload_constraints_type_inference_errors(var_collection)
            var_collection.store()
            result["html"] = utils.formalizations_to_html(app, var_collection.collection[var_name].get_constraints())
            return jsonify(result)

        elif command == "del_var":
            result = {"success": True, "errormsg": ""}
            var_name = request.form.get("name", "").strip()

            var_collection = VariableCollection(app)
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
            var_collection = VariableCollection(app)

            # Apply some tests if the new Variable is legal.
            if len(variable_name) == 0 or not re.match("^[a-zA-Z0-9_]+$", variable_name):
                result = {
                    "success": False,
                    "errormsg": "Illegal Variable name. Must Be at least 1 Char and only alphanum + {_}",
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
                return jsonify(result)
        elif command == "get_enumerators":
            result = {"success": True, "errormsg": ""}
            enum_name = request.form.get("name", "").strip()
            var_collection = VariableCollection(app)
            enumerators = var_collection.get_enumerators(enum_name)
            enum_results = [(enumerator.name, enumerator.value) for enumerator in enumerators]
            try:
                enum_results.sort(key=lambda x: float(x[1]))
            except Exception as e:
                logging.info(f"Cloud not sort ENUMERATORS: {e}")
            result["enumerators"] = enum_results

            return jsonify(result)
        elif command == "gen_req":
            content = utils.generate_req_file_content(app, variables_only=True)
            name = "{}_variables_only.req".format(app.config["CSV_INPUT_FILE"][:-4])

            return utils.generate_file_response(content, name)
        elif command == "import_csv":
            result = {"success": True, "errormsg": ""}

            variables_csv_str = request.form.get("variables_csv_str", "")
            var_collection = VariableCollection(app)

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
            raise DeprecationWarning

    if resource == "logs":
        if command == "get":
            return utils.get_flask_session_log(app, html_format=True)

    if resource == "report":
        return Reports(app, request).apply_request()

    return jsonify({"success": False, "errormsg": "This is not an api-enpoint."}), 404


@app.route("/variable_import/<id>", methods=["GET"])
@nocache
def variable_import(id):
    return render_template("variables/variable-import-session.html", id=id, query=request.args, patterns=PATTERNS)


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
            return render_template(
                "{}.html".format(site + "/" + site),
                available_sessions=[],
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


def varcollection_consistency_check(app, args=None):
    logging.info("Check Variables for consistency.")
    # Update usages and constraint type check.
    var_collection = VariableCollection(app)
    if args is not None and args.reload_type_inference:
        var_collection.reload_type_inference_errors_in_constraints()

    update_var_usage(var_collection)
    var_collection.store()


def create_revision(args, base_revision_name, *, db_test_mode: bool = False):
    """Create new revision.

    :param args: Parser arguments
    :param base_revision_name: Name of revision the created will be based on. Creates initial revision_0 if none given.
    :param db_test_mode: db testmode
    :return: None
    """
    revision = utils.Revision(app, args, base_revision_name)
    revision.create_revision(add_custom_serializer_to_database, db_test_mode=db_test_mode)


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


def user_request_new_revision(args, *, db_test_mode: bool = False):
    """Asks the user about the base revision and triggers create_revision with the user choice.

    :param args:
    :param db_test_mode:
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
    create_revision(args, base_revision_choice, db_test_mode=db_test_mode)


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

    def boogie_type_serialize(obj: BoogieType, db_serializer: Callable[[any, str], any], user: str) -> dict:
        return db_serializer(obj.value, user)

    def boogie_type_deserialize(data: dict, db_deserializer: Callable[[any], any]) -> BoogieType:
        return BoogieType(db_deserializer(data))

    database.add_custom_serializer(BoogieType, boogie_type_serialize, boogie_type_deserialize)


def startup_hanfor(args, HERE, *, db_test_mode: bool = False) -> bool:
    """Setup session config Variables.
     Trigger:
     Revision creation/loading.
     Variable script evaluation.
     Version migrations.
     Consistency checks.

    :param args:
    :returns: True if startup should continue
    """
    app.db = JsonDatabase(test_mode=db_test_mode)
    add_custom_serializer_to_database(app.db)

    set_session_config_vars(args, HERE)
    set_app_config_paths(args, HERE)

    # Create a new revision if requested.
    if args.revision:
        if args.input_csv is None:
            utils.HanforArgumentParser(app).error("--revision requires a Input CSV -c INPUT_CSV.")
        user_request_new_revision(args, db_test_mode=db_test_mode)
    else:
        # If there is no session with given tag: Create a new (initial) revision.
        if not os.path.exists(app.config["SESSION_FOLDER"]):
            create_revision(args, None, db_test_mode=db_test_mode)
        # If this is an already existing session, ask the user which revision to start.
        else:
            revision_choice = user_choose_start_revision()
            logging.info("Loading session `{}` at `{}`".format(app.config["SESSION_TAG"], revision_choice))
            load_revision(revision_choice)

    # Check CSV file change.
    if args.input_csv:
        logging.info("Check CSV integrity.")
        csv_hash = hash_file_sha1(args.input_csv)
        if not app.db.key_in_table(SessionValue, "csv_hash"):
            app.db.add_object(SessionValue("csv_hash", csv_hash))
        if csv_hash != app.db.get_object(SessionValue, "csv_hash").value:
            print(
                f"Sha-1 hash mismatch between: \n`{app.db.get_object(SessionValue, 'csv_input_file').value}`\nand\n`{args.input_csv}`."
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
    args = utils.HanforArgumentParser(app).parse_args()
    if startup_hanfor(args, HERE):
        app.run(**get_app_options())
