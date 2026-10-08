import csv
import logging

from flask import Blueprint, render_template, request
from flask_restx import Namespace, Resource

from hanfor_flask import HanforFlask, current_app, nocache
from json_db_connector.json_db import DatabaseKeyError
from lib_core.api_models import VariableRequestModel
from lib_core import boogie_parsing
from lib_core.boogie_parsing import BoogieType
from lib_core.data import (
    Requirement,
    SessionValue,
    Variable,
    VariableCollection,
    replace_prefix,
)
from lib_core.pattern.patterns_basic import APattern
from lib_core.scopes import Scope
from lib_core.utils import (
    delete_variable_everywhere,
    formalizations_to_html,
    generate_file_response,
    generate_req_file_content,
    get_requirements,
    log_request_response,
    rename_variable_everywhere,
)
from requirements.desc_highlighting import (
    changing_variables,
    delete_variables,
    new_variables_regenerate_highlighting,
)
from requirements.subtypes import (
    Conflict,
    InvalidPayload,
    SubtypeNotFound,
    subtype_errors_to_response,
    write_locked,
)

blueprint = Blueprint("variables", __name__, template_folder="templates", url_prefix="/variables")
api_blueprint = Blueprint("api_variables", __name__, url_prefix="/api/var")
api_ns = Namespace("Variables", "Read and change the variables of the session.", path="/variables", ordered=True)


@blueprint.route("", methods=["GET"])
def index():
    return render_template(
        "variables/variables.html",
        available_variable_types=["CONST"] + list(BoogieType.get_valid_type_names()),
        variable_name_regex=Variable.NAME_REGEX,
        query=request.args,
        patterns=APattern().to_frontent_dict(),
    )


@api_ns.route("")
@log_request_response
class ApiVariables(Resource):
    @api_ns.doc(
        description="Gives all variables of the session in the field 'data'. Each variable has its id, name, "
        "type, value, the requirements that use it, and the references to its constraints. Use the query "
        "parameter 'name' to get only the variable with that name, for example to find its id.",
        params={"name": "Optional. Gives only the variable with this name"},
    )
    @api_ns.response(200, "Success")
    @nocache
    def get(self):
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        result = var_collection.get_available_vars_list(used_only=False)
        for entry in result:
            # constraint_refs come from var_collection._constraints, which is rebuilt
            # on every construction by walking Variable.constraints and
            # Requirement.formalizations (is_constraint=True).
            entry["constraint_refs"] = [c.usage_key for c in var_collection._constraints.get(entry["name"], [])]
        name = request.args.get("name")
        if name is not None:
            result = [entry for entry in result if entry["name"] == name]
        return {"data": result}

    @api_ns.doc(
        description="Makes a new variable. The JSON body has 'name', 'type' and, for a CONST, 'value'. "
        "Gives 400 if a field is not valid, and 409 if a variable with the name exists.",
    )
    @api_ns.expect(VariableRequestModel)
    @api_ns.response(201, "Created")
    @api_ns.response(400, "Bad Request")
    @api_ns.response(409, "Conflict")
    @nocache
    @subtype_errors_to_response
    @write_locked
    def post(self):
        body = request.get_json(silent=True) or {}
        variable_name = str(body.get("name", "")).strip()
        variable_type = str(body.get("type", "")).strip()
        variable_value = str(body.get("value", "")).strip()
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )

        try:
            new_variable = Variable(variable_name, variable_type, None)
        except ValueError as e:
            raise InvalidPayload(str(e)) from e
        if var_collection.var_name_exists(variable_name):
            raise Conflict(f"`{variable_name}` is already existing.")
        if variable_type not in ["ENUM_INT", "ENUM_REAL", "REAL", "INT", "BOOL", "CONST"]:
            raise InvalidPayload(f"`{variable_type}` Is not a valid Variable type.")
        if variable_type == "CONST":
            try:
                float(variable_value)
            except ValueError as e:
                raise InvalidPayload("Const value not valid.") from e

        logging.debug(f"Adding new Variable `{variable_name}` to Variable collection.")
        variable = var_collection.add_var(variable_name, new_variable)
        current_app.db.add_object(variable)
        if variable_type == "CONST":
            var_collection.collection[variable_name].value = variable_value
        var_collection.store()
        current_app.db.update()
        if current_app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"]:
            new_variables_regenerate_highlighting({new_variable})
        return {"success": True, "name": variable_name, "id": new_variable.uuid}, 201


def _load_variable(vid) -> Variable:
    try:
        return current_app.db.get_object(Variable, str(vid))
    except DatabaseKeyError as e:
        raise SubtypeNotFound(f"Variable `{vid}` not found.") from e


@api_ns.route("/<uuid:vid>")
@log_request_response
class ApiVariable(Resource):
    @api_ns.doc(
        description="Deletes the variable everywhere: in the variable list and in the requirement that "
        "defines it. Gives 404 if the variable is not found, and 409 if a requirement or a constraint "
        "uses it.",
        params={"vid": "The id (uuid) of the variable"},
    )
    @api_ns.response(200, "Success")
    @api_ns.response(404, "Not Found")
    @api_ns.response(409, "Conflict")
    @nocache
    @subtype_errors_to_response
    @write_locked
    def delete(self, vid):
        name = _load_variable(vid).name
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        logging.debug(f"Deleting `{name}`")
        if delete_variable_everywhere(var_collection, name) is None:
            raise Conflict(f"Variable `{name}` is used and thus cannot be deleted.")
        if current_app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"]:
            delete_variables([name])
        var_collection.store()
        current_app.db.update()
        return {"success": True}

    @api_ns.doc(
        description="Changes the variable. The JSON body has the new values: 'name', 'type', 'const_val', "
        "'belongs_to_enum', 'enumerators', and 'constraints' with 'updated_constraints': true. A field that is "
        "not in the body keeps its value. Gives 404 if the variable is not found, and 400 if the change is not "
        "valid.",
        params={"vid": "The id (uuid) of the variable"},
    )
    @api_ns.response(200, "Success")
    @api_ns.response(400, "Bad Request")
    @api_ns.response(404, "Not Found")
    @nocache
    @subtype_errors_to_response
    @write_locked
    def patch(self, vid):
        name = _load_variable(vid).name
        result = update_variable_in_collection(current_app, {**(request.get_json(silent=True) or {}), "name_old": name})
        if not result["success"]:
            return result, 400
        return result


@api_ns.route("/<uuid:vid>/enumerators")
@log_request_response
class ApiVariableEnumerators(Resource):
    @api_ns.doc(
        description="Gives the enumerators of the ENUM variable in the field 'enumerators', as a list of "
        "[name, value, id] triples sorted by value. Gives 404 if the variable is not found.",
        params={"vid": "The id (uuid) of the ENUM variable"},
    )
    @api_ns.response(200, "Success")
    @api_ns.response(404, "Not Found")
    @nocache
    @subtype_errors_to_response
    def get(self, vid):
        name = _load_variable(vid).name
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        enumerators = var_collection.get_enumerators(name)
        enum_results = [(enumerator.name, enumerator.value, enumerator.uuid) for enumerator in enumerators]
        try:
            enum_results.sort(key=lambda x: float(x[1]))
        except Exception as e:
            logging.info(f"Cloud not sort ENUMERATORS: {e}")
        return {"success": True, "enumerators": enum_results}


@api_ns.route("/export", endpoint="variables_export")
@log_request_response
class ApiVariablesExport(Resource):
    @api_ns.doc(
        description="Get a .req file that contains all variables of the session and their constraints. "
        "The file contains no requirements."
    )
    @api_ns.response(200, "Success")
    @nocache
    def get(self):
        content = generate_req_file_content(current_app, variables_only=True)
        name = "{}_variables_only.req".format(current_app.config["CSV_INPUT_FILE"][:-4])
        return generate_file_response(content, name)


@api_ns.route("/import")
@log_request_response
class ApiVariablesImport(Resource):
    @api_ns.doc(
        description="Add the variables from a CSV text to the session. "
        'Send a JSON body with the key "csv". '
        "The CSV must have the columns name, enum_name, description, type, value and constraint. "
        "The import skips a row if the name is empty or invalid, or if the variable exists."
    )
    @api_ns.response(200, "Success")
    @api_ns.response(400, "Bad Request")
    @nocache
    @subtype_errors_to_response
    @write_locked
    def post(self):
        variables_csv_str = (request.get_json(silent=True) or {}).get("csv", "")
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )

        dict_reader = csv.DictReader(variables_csv_str.splitlines())
        variables = list(dict_reader)

        missing_fieldnames = {
            "name",
            "enum_name",
            "description",
            "type",
            "value",
            "constraint",
        }.difference(dict_reader.fieldnames or [])
        if len(missing_fieldnames) > 0:
            raise InvalidPayload(f"Import failed due to missing fieldnames: {missing_fieldnames}.")

        for variable in variables:
            if variable["name"] == "" or var_collection.var_name_exists(variable["name"]):
                continue
            try:
                current_app.db.add_object(var_collection.add_var(variable["name"]))
            except ValueError as e:
                logging.warning(f"Skipping CSV import for invalid variable name: {e}")
                continue
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
                    SessionValue.get_standard_tags(current_app.db),
                )

        var_collection.store()
        current_app.db.update()
        return {"success": True}


@api_blueprint.route("/get_constraints_html", methods=["POST"])
@nocache
def api_get_constraints_html():
    result = {
        "success": True,
        "errormsg": "",
        "html": '<p class="no-constraints-placeholder">No constraints set.</p>',
        "type_inference_errors": dict(),
    }
    var_name = request.form.get("name", "").strip()
    var_collection = VariableCollection(
        current_app.db.get_objects(Variable).values(),
        current_app.db.get_objects(Requirement).values(),
    )
    var = var_collection.collection.get(var_name)
    if var is None:
        return result
    # `var.constraints` is the source of truth for variable-owned constraints.
    formalizations = dict(var.constraints)
    if formalizations:
        result["html"] = formalizations_to_html(current_app, formalizations)
        result["type_inference_errors"] = {fid: f.type_inference_errors for fid, f in formalizations.items()}
    return result


@api_blueprint.route("/new_constraint", methods=["POST"])
@nocache
def api_new_constraint():
    result = {"success": True, "errormsg": ""}
    var_name = request.form.get("name", "").strip()

    var_collection = VariableCollection(
        current_app.db.get_objects(Variable).values(),
        current_app.db.get_objects(Requirement).values(),
    )
    cid = var_collection.add_new_constraint(var_name=var_name)
    var_collection.store()
    current_app.db.update()
    form = var_collection.collection[var_name].constraints[cid]
    result["html"] = formalizations_to_html(current_app, {cid: form})
    return result


@api_blueprint.route("/del_constraint", methods=["POST"])
@nocache
def api_del_constraint():
    result = {"success": True, "errormsg": ""}
    var_name = request.form.get("name", "").strip()
    constraint_id = int(request.form.get("constraint_id", "").strip())

    var_collection = VariableCollection(
        current_app.db.get_objects(Variable).values(),
        current_app.db.get_objects(Requirement).values(),
    )
    var_collection.del_constraint(var_name=var_name, constraint_id=constraint_id)
    var_collection.collection[var_name].reload_constraints_type_inference_errors(
        var_collection, SessionValue.get_standard_tags(current_app.db)
    )
    var_collection.store()
    current_app.db.update()
    result["html"] = formalizations_to_html(current_app, var_collection.collection[var_name].get_constraints())
    return result


def update_variable_in_collection(app: HanforFlask, data: dict) -> dict:
    """Update a single variable. `data` is the JSON body plus `name_old` from the path.
    A field that is not in `data` keeps its stored value:
        name -> the new name of the var.
        name_old -> the name of the var before.
        type -> the new type of the var.
        const_val -> the new value of the var.
        belongs_to_enum -> the new ENUM parent of an ENUMERATOR.
        enumerators -> The dict of enumerators

    :param app: the running flask app
    :param data: The fields of the update
    :return: Dictionary containing changed data and request status information.
    """
    var_collection = VariableCollection(
        current_app.db.get_objects(Variable).values(),
        current_app.db.get_objects(Requirement).values(),
    )
    var_name_old = str(data.get("name_old") or "").strip()
    current = var_collection.collection[var_name_old]
    var_type_old = current.type or ""
    var_const_val_old = str(current.value or "")
    belongs_to_enum_old = current.belongs_to_enum or ""

    def new_value(key: str, old: str) -> str:
        return old if data.get(key) is None else str(data[key]).strip()

    var_name = new_value("name", var_name_old)
    var_type = new_value("type", var_type_old)
    var_const_val = new_value("const_val", var_const_val_old)
    belongs_to_enum = new_value("belongs_to_enum", belongs_to_enum_old)
    enumerators = data.get("enumerators")
    updated_constraints = data.get("updated_constraints") is True
    result = {
        "success": True,
        "has_changes": False,
        "type_changed": False,
        "name_changed": False,
        "rebuild_table": False,
        "data": {
            "name": var_name,
            "type": var_type,
            "used_by": sorted(var_collection.var_req_mapping.get(var_name_old, [])),
            "const_val": var_const_val,
        },
    }

    # Check for changes
    if (
        var_type_old != var_type
        or var_name_old != var_name
        or var_const_val_old != var_const_val
        or updated_constraints
        or belongs_to_enum != belongs_to_enum_old
    ):
        logging.info(f"Update Variable `{var_name_old}`")
        result["has_changes"] = True
        reload_type_inference = False

        # Update type.
        if var_type_old != var_type:
            logging.info(f"Change type from `{var_type_old}` to `{var_type}`.")
            try:
                var_collection.collection[var_name_old].belongs_to_enum = belongs_to_enum
                var_collection.set_type(var_name_old, var_type)
            except (TypeError, ValueError) as e:
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
        if updated_constraints:
            constraints = data.get("constraints") or {}
            logging.debug("Update Variable Constraints")
            try:
                var_collection = var_collection.collection[var_name_old].update_constraints(
                    constraints,
                    var_collection,
                    SessionValue.get_standard_tags(current_app.db),
                )
                result["rebuild_table"] = True
                app.db.update()
            except KeyError as e:
                result["success"] = False
                result["errormsg"] = f"Could not set constraint: Missing expression/variable for {e}"
            except Exception as e:
                result["success"] = False
                result["errormsg"] = f"Could not parse formalization: `{e}`"
        else:
            logging.debug("Skipping variable Constraints update.")

        # update name.
        if var_name_old != var_name:
            logging.debug("Change name of var `{}` to `{}`".format(var_name_old, var_name))
            #  new name exists means the two vars are merged into one which needs a complete rebuild.
            if var_name in var_collection:
                if var_collection.collection[var_name_old].type != var_collection.collection[var_name].type:
                    result["success"] = False
                    result["errormsg"] = "To merge two variables the types must be identical. {} != {}".format(
                        var_collection.collection[var_name_old].type,
                        var_collection.collection[var_name].type,
                    )
                    return result
                logging.debug("`{}` is an existing var name. Merging the two vars. ".format(var_name))
                result["rebuild_table"] = True
                reload_type_inference = True

            # renames the var, its enumerators and every expression naming any of them.
            try:
                rename_variable_everywhere(var_collection, var_name_old, var_name)
            except (KeyError, ValueError) as e:
                result = {"success": False, "errormsg": str(e)}
                return result

            if current_app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"]:
                changing_variables(var_name_old, var_name)
            result["name_changed"] = True

        # Change ENUM parent.
        if belongs_to_enum != belongs_to_enum_old and var_type in [
            "ENUMERATOR_INT",
            "ENUMERATOR_REAL",
        ]:
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
            try:
                var_collection.rename(var_name, new_enumerator_name, app)
            except ValueError as e:
                result = {"success": False, "errormsg": str(e)}
                return result

        logging.info("Store updated variables.")
        var_collection.store()
        app.db.update()
        logging.info("Update derived types by parsing affected formalizations.")
        if reload_type_inference and var_name in var_collection.var_req_mapping:
            for rid in var_collection.var_req_mapping[var_name]:
                if app.db.key_in_table(Requirement, rid):
                    requirement = app.db.get_object(Requirement, rid)
                    requirement.run_type_checks(var_collection, SessionValue.get_standard_tags(app.db))
            app.db.update()

    if enumerators is None:
        return result
    try:
        success, errormsg, _ = var_collection.create_enum_variable(var_name, var_type, enumerators)
    except ValueError as e:
        result = {"success": False, "errormsg": str(e)}
        return result
    if not success:
        result = {"success": False, "errormsg": errormsg}
        return result

    return result


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
