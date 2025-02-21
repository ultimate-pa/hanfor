from flask import Blueprint, request, render_template, Request
import logging
import json
import re
import csv

from hanfor_flask import current_app, nocache, HanforFlask
from lib_core.data import VariableCollection, Variable, Scope, Requirement, replace_prefix
from lib_core.utils import (
    get_requirements,
    formalizations_to_html,
    generate_file_response,
    generate_req_file_content,
)
from lib_core import boogie_parsing
from configuration.patterns import PATTERNS

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
    var_collection = VariableCollection(current_app)
    result = var_collection.get_available_vars_list(used_only=False)
    return {"data": result}


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
        result["html"] = formalizations_to_html(current_app, var.constraints)
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
    result["html"] = formalizations_to_html(current_app, {cid: var_collection.collection[var_name].constraints[cid]})
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
    result["html"] = formalizations_to_html(current_app, var_collection.collection[var_name].get_constraints())
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
    content = generate_req_file_content(current_app, variables_only=True)
    name = "{}_variables_only.req".format(current_app.config["CSV_INPUT_FILE"][:-4])

    return generate_file_response(content, name)


@api_blueprint.route("/update", methods=["POST"])
@nocache
def api_update():
    return update_variable_in_collection(current_app, request)


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


def update_variable_in_collection(app: HanforFlask, req: Request) -> dict:
    """Update a single variable. The request should contain a form:
        name -> the new name of the var.
        name_old -> the name of the var before.
        type -> the new type of the var.
        type_old -> the old type of the var.
        occurrences -> Ids of requirements using this variable.
        enumerators -> The dict of enumerators

    :param app: the running flask app
    :param req: A form request
    :return: Dictionary containing changed data and request status information.
    """
    # Get properties from request
    var_name = req.form.get("name", "").strip()
    var_name_old = req.form.get("name_old", "").strip()
    var_type = req.form.get("type", "").strip()
    var_type_old = req.form.get("type_old", "").strip()
    var_const_val = req.form.get("const_val", "").strip()
    var_const_val_old = req.form.get("const_val_old", "").strip()
    belongs_to_enum = req.form.get("belongs_to_enum", "").strip()
    belongs_to_enum_old = req.form.get("belongs_to_enum_old", "").strip()
    occurrences = req.form.get("occurrences", "").strip().split(",")
    enumerators = json.loads(req.form.get("enumerators", ""))

    # TODO: remove
    while "" in occurrences:
        occurrences.remove("")

    var_collection = VariableCollection(app)
    result = {
        "success": True,
        "has_changes": False,
        "type_changed": False,
        "name_changed": False,
        "rebuild_table": False,
        "data": {"name": var_name, "type": var_type, "used_by": occurrences, "const_val": var_const_val},
    }

    # Check for changes
    if (
        var_type_old != var_type
        or var_name_old != var_name
        or var_const_val_old != var_const_val
        or req.form.get("updated_constraints") == "true"
        or belongs_to_enum != belongs_to_enum_old
    ):
        logging.info("Update Variable `{}`".format(var_name_old))
        result["has_changes"] = True
        reload_type_inference = False

        # Update type.
        if var_type_old != var_type:
            logging.info("Change type from `{}` to `{}`.".format(var_type_old, var_type))
            try:
                var_collection.collection[var_name_old].belongs_to_enum = belongs_to_enum
                var_collection.set_type(var_name_old, var_type)
            except TypeError as e:
                result = {"success": False, "errormsg": str(e)}
                return result
            result["type_changed"] = True
            reload_type_inference = True

        # Update const value.
        if var_const_val_old != var_const_val:
            try:
                if var_type == "ENUMERATOR_INT":
                    int(var_const_val)
                if var_type in ["ENUMERATOR_REAL"]:
                    float(var_const_val)
            except Exception as e:
                result = {
                    "success": False,
                    "errormsg": "Enumerator value `{}` for {} `{}` not valid: {}".format(
                        var_const_val, var_type, var_name, e
                    ),
                }
                return result
            logging.info("Change value from `{}` to `{}`.".format(var_const_val_old, var_const_val))
            var_collection.collection[var_name].value = var_const_val
            result["val_changed"] = True

        # Update constraints.
        if req.form.get("updated_constraints") == "true":
            constraints = json.loads(req.form.get("constraints", ""))
            logging.debug("Update Variable Constraints")
            try:
                var_collection = var_collection.collection[var_name_old].update_constraints(
                    constraints, app, var_collection
                )
                result["rebuild_table"] = True
                app.db.update()
            except KeyError as e:
                result["success"] = False
                result["error_msg"] = "Could not set constraint: Missing expression/variable for {}".format(e)
            except Exception as e:
                result["success"] = False
                result["error_msg"] = "Could not parse formalization: `{}`".format(e)
        else:
            logging.debug("Skipping variable Constraints update.")

        # update name.
        if var_name_old != var_name:
            logging.debug("Change name of var `{}` to `{}`".format(var_name_old, var_name))
            #  Case: New name which does not exist -> remove the old var and replace in reqs occurring.
            if var_name not in var_collection:
                logging.debug("`{}` is a new var name. Rename the var, replace occurrences.".format(var_name))
                # Rename the var (Copy to new name and remove the old item. Rename it)
                affected_enumerators = var_collection.rename(var_name_old, var_name, app)

            else:  # Case: New name exists. -> Merge the two vars into one. -> Complete rebuild.
                if var_collection.collection[var_name_old].type != var_collection.collection[var_name].type:
                    result["success"] = False
                    result["errormsg"] = "To merge two variables the types must be identical. {} != {}".format(
                        var_collection.collection[var_name_old].type, var_collection.collection[var_name].type
                    )
                    return result
                logging.debug("`{}` is an existing var name. Merging the two vars. ".format(var_name))
                # var_collection.merge_vars(var_name_old, var_name, app)
                affected_enumerators = var_collection.rename(var_name_old, var_name, app)
                result["rebuild_table"] = True
                reload_type_inference = True

            # Update the requirements using this var.
            if len(occurrences) > 0:
                rename_variable_in_expressions(app, occurrences, var_name_old, var_name)

            for old_enumerator_name, new_enumerator_name in affected_enumerators:
                # Todo: Implement this more eff.
                # Todo: Refactor Formalizations to use hashes as vars and fetch them in __str__ from the var collection.
                requirements = get_requirements(app)
                affected_requirements = get_requirements_using_var(requirements, old_enumerator_name)
                rename_variable_in_expressions(app, affected_requirements, old_enumerator_name, new_enumerator_name)

            result["name_changed"] = True

        # Change ENUM parent.
        if belongs_to_enum != belongs_to_enum_old and var_type in ["ENUMERATOR_INT", "ENUMERATOR_REAL"]:
            logging.debug("Change enum parent of enumerator `{}` to `{}`".format(var_name, belongs_to_enum))
            if belongs_to_enum not in var_collection:
                result["success"] = False
                result["errormsg"] = "The new ENUM parent `{}` does not exist.".format(belongs_to_enum)
                return result
            if var_collection.collection[belongs_to_enum].type != replace_prefix(var_type, "ENUMERATOR", "ENUM"):
                result["success"] = False
                result["errormsg"] = "The new ENUM parent `{}` is not an {} (is `{}`).".format(
                    belongs_to_enum,
                    replace_prefix(var_type, "ENUMERATOR", "ENUM"),
                    var_collection.collection[belongs_to_enum].type,
                )
                return result
            new_enumerator_name = replace_prefix(var_name, belongs_to_enum_old, "")
            new_enumerator_name = replace_prefix(new_enumerator_name, "_", "")
            new_enumerator_name = replace_prefix(new_enumerator_name, "", belongs_to_enum + "_")
            if new_enumerator_name in var_collection:
                result["success"] = False
                result["errormsg"] = "The new ENUM parent `{}` already has a ENUMERATOR `{}`.".format(
                    belongs_to_enum, new_enumerator_name
                )
                return result

            var_collection.collection[var_name].belongs_to_enum = belongs_to_enum
            var_collection.rename(var_name, new_enumerator_name, app)

        logging.info("Store updated variables.")
        var_collection.refresh_var_constraint_mapping()
        var_collection.store()
        app.db.update()
        logging.info("Update derived types by parsing affected formalizations.")
        if reload_type_inference and var_name in var_collection.var_req_mapping:
            for rid in var_collection.var_req_mapping[var_name]:
                if app.db.key_in_table(Requirement, rid):
                    requirement = app.db.get_object(Requirement, rid)
                    requirement.run_type_checks(var_collection)
            app.db.update()

    if var_type in ["ENUM_INT", "ENUM_REAL"]:
        new_enumerators = []
        for enumerator_name, enumerator_value in enumerators:
            if len(enumerator_name) == 0 and len(enumerator_value) == 0:
                continue
            if len(enumerator_name) == 0 or not re.match("^[a-zA-Z0-9_-]+$", enumerator_name):
                result = {"success": False, "errormsg": "Enumerator name `{}` not valid".format(enumerator_name)}
                break
            try:
                if var_type == "ENUM_INT":
                    int(enumerator_value)
                if var_type == "ENUM_REAL":
                    float(enumerator_value)
            except Exception as e:
                result = {
                    "success": False,
                    "errormsg": "Enumerator value `{}` for enumerator `{}` not valid: {}".format(
                        enumerator_value, enumerator_name, e
                    ),
                }
                break

            enumerator_name = "{}_{}".format(var_name, enumerator_name)
            # Add new enumerators to the var_collection
            if not var_collection.var_name_exists(enumerator_name):
                var_collection.add_var(enumerator_name)
                new_enumerators.append(enumerator_name)

            var_collection.collection[enumerator_name].set_type(f"ENUMERATOR_{var_type[5:]}")
            var_collection.collection[enumerator_name].value = enumerator_value
            var_collection.collection[enumerator_name].belongs_to_enum = var_name

        var_collection.store()
        app.db.update()

    return result


def rename_variable_in_expressions(
    app: HanforFlask, occurrences, var_name_old, var_name
):  # TODO nach variables, refactor that expressions use uuids
    """Updates (replace) the variables in the requirement expressions.

    :param app: Flask app (used for session).
    :type app: HanforFlask
    :param occurrences: Requirement ids to be taken into account.
    :type occurrences: list (of str)
    :param var_name_old: The current name in the expressions.
    :type var_name_old: str
    :param var_name: The new name.
    :type var_name: str
    """
    logging.debug("Update requirements using old var `{}` to `{}`".format(var_name_old, var_name))
    for rid in occurrences:
        requirement = app.db.get_object(Requirement, rid)
        # replace in every formalization
        for idx, formalization in requirement.formalizations.items():
            for key, expression in formalization.expressions_mapping.items():
                if var_name_old not in expression.raw_expression:
                    continue
                new_expression = boogie_parsing.replace_var_in_expression(
                    expression=expression.raw_expression, old_var=var_name_old, new_var=var_name
                )
                requirement.formalizations[idx].expressions_mapping[key].raw_expression = new_expression
                requirement.formalizations[idx].expressions_mapping[key].used_variables.remove(var_name_old)
                requirement.formalizations[idx].expressions_mapping[key].used_variables.add(var_name)
        logging.debug("Updated variables in requirement id: `{}`.".format(requirement.rid))
    app.db.update()


def get_requirements_using_var(requirements: list, var_name: str):
    """Return a list of requirement ids where var_name is used in at least one formalization.

    :param requirements: list of Requirement.
    :param var_name: Variable name to search for.
    :return: List of affected Requirement ids.
    """
    result_rids = []
    for requirement in requirements:  # type: Requirement
        if requirement.uses_var(var_name):
            result_rids.append(requirement.rid)

    return result_rids
