from flask import Blueprint, request, render_template
import logging
import json
import re
import csv

import utils
from hanfor_flask import current_app, nocache
from lib_core.data import VariableCollection, Variable, Scope
from patterns import PATTERNS

blueprint = Blueprint("variables", __name__, template_folder="templates", url_prefix="/variables")
blueprint2 = Blueprint("variables_import", __name__, template_folder="templates", url_prefix="/variable_import")
api_blueprint = Blueprint("api_variables", __name__, url_prefix="/api/var")


@blueprint.route("", methods=["GET"])
def index():
    return render_template(
        "variables/variables.html",
        available_sessions=[],
        query=request.args,
        patterns=PATTERNS,
    )


@blueprint2.route("/<rid>", methods=["GET"])
@nocache
def variable_import(rid):
    return render_template("variables/variable-import-session.html", id=rid, query=request.args, patterns=PATTERNS)


@api_blueprint.route("/gets", methods=["GET"])
@nocache
def api_gets():
    return {"data": utils.get_available_vars(current_app, full=True)}


@api_blueprint.route("/get_constraints_html", methods=["POST"])
@nocache
def api_get_constraints_html():
    result = {
        "success": True,
        "errormsg": "",
        "html": "<p>No constraints set.</p>",
        "type_inference_errors": dict(),
    }
    var_name = request.form.get("name", "").strip()
    var_collection = VariableCollection(current_app)
    try:
        var = var_collection.collection[var_name]
        var_dict = var.to_dict(var_collection.var_req_mapping)
        result["html"] = utils.formalizations_to_html(current_app, var.constraints)
        result["type_inference_errors"] = var_dict["type_inference_errors"]
    except AttributeError:
        pass

    return result


@api_blueprint.route("/multi_update", methods=["POST"])
@nocache
def api_multi_update():
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
            var_collection = VariableCollection(current_app)
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
            var_collection = VariableCollection(current_app)
            for var_name in var_list:
                try:
                    logging.debug("Deleting `{}`".format(var_name))
                    var_collection.del_var(var_name)
                except KeyError:
                    logging.debug("Variable `{}` not found".format(var_list))
            var_collection.store()
    current_app.db.update()
    return result


@api_blueprint.route("/new_constraint", methods=["POST"])
@nocache
def api_new_constraint():
    result = {"success": True, "errormsg": ""}
    var_name = request.form.get("name", "").strip()

    var_collection = VariableCollection(current_app)
    cid = var_collection.add_new_constraint(var_name=var_name)
    var_collection.store()
    current_app.db.update()
    result["html"] = utils.formalizations_to_html(
        current_app, {cid: var_collection.collection[var_name].constraints[cid]}
    )
    return result


@api_blueprint.route("/del_constraint", methods=["POST"])
@nocache
def api_del_constraint():
    result = {"success": True, "errormsg": ""}
    var_name = request.form.get("name", "").strip()
    constraint_id = int(request.form.get("constraint_id", "").strip())

    var_collection = VariableCollection(current_app)
    var_collection.del_constraint(var_name=var_name, constraint_id=constraint_id)
    var_collection.collection[var_name].reload_constraints_type_inference_errors(var_collection)
    var_collection.store()
    current_app.db.update()
    result["html"] = utils.formalizations_to_html(current_app, var_collection.collection[var_name].get_constraints())
    return result


@api_blueprint.route("/del_var", methods=["POST"])
@nocache
def api_del_var():
    result = {"success": True, "errormsg": ""}
    var_name = request.form.get("name", "").strip()

    var_collection = VariableCollection(current_app)
    try:
        logging.debug("Deleting `{}`".format(var_name))
        success = var_collection.del_var(var_name)
        if not success:
            result = {"success": False, "errormsg": "Variable is used and thus cannot be deleted."}
        var_collection.store()
        current_app.db.update()
    except KeyError:
        logging.debug("Variable `{}` not found".format(var_name))
        result = {"success": False, "errormsg": "Variable not found."}
    return result


@api_blueprint.route("/add_new_variable", methods=["POST"])
@nocache
def api_add_new_variable():
    result = {"success": True, "errormsg": ""}
    variable_name = request.form.get("name", "").strip()
    variable_type = request.form.get("type", "").strip()
    variable_value = request.form.get("value", "").strip()
    var_collection = VariableCollection(current_app)

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
        except Exception as e:
            logging.info(f"Cloud not cast ENUMERATORS: {e}")
            result = {"success": False, "errormsg": "Const value not valid."}
    # We passed all tests, so add the new variable.
    if result["success"]:
        logging.debug("Adding new Variable `{}` to Variable collection.".format(variable_name))
        new_variable = Variable(variable_name, variable_type, None)
        var_collection.add_var(variable_name, new_variable)
        if variable_type == "CONST":
            var_collection.collection[variable_name].value = variable_value
        var_collection.store()
        current_app.db.update()
        return result


@api_blueprint.route("/get_enumerators", methods=["POST"])
@nocache
def api_get_enumerators():
    result = {"success": True, "errormsg": ""}
    enum_name = request.form.get("name", "").strip()
    var_collection = VariableCollection(current_app)
    enumerators = var_collection.get_enumerators(enum_name)
    enum_results = [(enumerator.name, enumerator.value) for enumerator in enumerators]
    try:
        enum_results.sort(key=lambda x: float(x[1]))
    except Exception as e:
        logging.info(f"Cloud not sort ENUMERATORS: {e}")
    result["enumerators"] = enum_results

    return result


@api_blueprint.route("/gen_req", methods=["POST"])
@nocache
def api_gen_req():
    content = utils.generate_req_file_content(current_app, variables_only=True)
    name = "{}_variables_only.req".format(current_app.config["CSV_INPUT_FILE"][:-4])

    return utils.generate_file_response(content, name)


@api_blueprint.route("/update", methods=["POST"])
@nocache
def api_update():
    return utils.update_variable_in_collection(current_app, request)


@api_blueprint.route("/import_csv", methods=["POST"])
@nocache
def api_import_csv():
    result = {"success": True, "errormsg": ""}

    variables_csv_str = request.form.get("variables_csv_str", "")
    var_collection = VariableCollection(current_app)

    dict_reader = csv.DictReader(variables_csv_str.splitlines())
    variables = list(dict_reader)

    missing_fieldnames = {"name", "enum_name", "description", "type", "value", "constraint"}.difference(
        dict_reader.fieldnames
    )
    if len(missing_fieldnames) > 0:
        result["errormsg"] = f"Import failed due to missing fieldnames: {missing_fieldnames}."
        result["success"] = False
        return result

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
    current_app.db.update()
    return result
