import json
import logging

from flask import Blueprint, render_template, request
from flask_restx import Namespace, Resource

from config import PATTERNS_GROUP_ORDER
from configuration.defaults import Color
from guesser.Guess import Guess
from guesser.guesser_registerer import REGISTERED_GUESSERS
from hanfor_flask import HanforFlask, current_app, nocache
from json_db_connector.json_db import DatabaseKeyError
from lib_core.api_models import (
    AvailableGuessesModel,
    ColumnDefsModel,
    ErrorMessageModel,
    FormalizationModel,
    RequirementDetailModel,
    RequirementListModel,
    SuccessResponseModel,
)
from lib_core.boogie_parsing import BoogieType
from lib_core.data import (
    Formalization,
    Requirement,
    SessionValue,
    Tag,
    Variable,
    VariableCollection,
)
from lib_core.pattern import APattern
from lib_core.pattern.patterns_functions import VARIABLE_AUTOCOMPLETE_EXTENSION
from lib_core.utils import (
    add_msg_to_flask_session_log,
    default_scope_options,
    formalization_html,
    get_default_pattern_options,
    log_request_response,
    prepare_patterns_for_jinja,
)
from requirements.subtypes import InvalidPayload, SubtypeContext, SubtypeNotFound, subtype_errors_to_response
from requirements.desc_highlighting import (
    get_highlighted_desc,
    highlight_text,
    new_variables_regenerate_highlighting,
    rehighlight_requirement,
)

blueprint = Blueprint("requirements", __name__, template_folder="templates", url_prefix="/")
api_ns = Namespace("Requirements", "Requirements API description", path="/req", ordered=True)


@blueprint.route("", methods=["GET"])
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
    additional_cols = get_datatable_additional_cols(current_app)["col_defs"]
    pattern_groups = prepare_patterns_for_jinja()
    return render_template(
        # TODO: the object refactor will break this - fix later!!
        "requirements/index.html",
        available_variable_types=["CONST"] + list(BoogieType.get_valid_type_names()),
        query=request.args,
        additional_cols=additional_cols,
        default_cols=default_cols,
        pattern_groups=pattern_groups,
        group_order=PATTERNS_GROUP_ORDER,
        patterns=APattern().to_frontent_dict(),
    )


@api_ns.route("/colum_defs")
@log_request_response
class ApiColumnDefs(Resource):
    @api_ns.doc(
        description="Returns additional column definitions " "for the requirements DataTable from CSV field names."
    )
    @api_ns.response(200, "Success", ColumnDefsModel)
    @nocache
    def get(self):
        result = get_datatable_additional_cols(current_app)
        return result


@api_ns.route("/<string:rid>")
@log_request_response
class ApiRequirementSingle(Resource):
    @api_ns.doc(
        description="Returns full detail for one requirement, including "
        "formalizations, available variables, and next formalization ID.",
        params={"rid": "The requirement ID (e.g. 'SysRS FooXY_42')"},
    )
    @api_ns.response(200, "Success", RequirementDetailModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    def get(self, rid):
        try:
            requirement = current_app.db.get_object(Requirement, rid)
        except DatabaseKeyError:
            return {
                "success": False,
                "errormsg": f"Requirement '{rid}' not found.",
            }, 404
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        result = requirement.to_dict(include_used_vars=True)
        result["available_vars"] = var_collection.get_available_var_names_list(used_only=False, exclude_types={"ENUM"})
        result["additional_static_available_vars"] = VARIABLE_AUTOCOMPLETE_EXTENSION
        if current_app.config.get("FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"):
            result["desc_highlighted"] = get_highlighted_desc(rid, result["desc"])
        else:
            result["desc_highlighted"] = result["desc"]
        result["next_id"] = requirement.next_id()
        return result

    @api_ns.doc(
        description="Partial update - only form fields that are sent are " "changed. Omitted fields remain untouched.",
        params={
            "rid": "The requirement ID",
            "status": "New status value (empty string = no change)",
            "tags": "JSON dict of {tag_name: comment}. Replaces all tags.",
            "update_formalization": "Set 'true' to update formalizations",
            "formalizations": "JSON-encoded formalization data",
            "formalizations_order": "JSON dict of {fid: order} for reordering",
        },
    )
    @api_ns.response(200, "Success", RequirementDetailModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @nocache
    def patch(self, rid):
        try:
            requirement = current_app.db.get_object(Requirement, rid)
        except DatabaseKeyError:
            return {
                "success": False,
                "errormsg": f"Requirement '{rid}' not found.",
            }, 404

        self._update_formalizations_order(requirement, request.form.get("formalizations_order"))
        self._update_status(requirement, request.form.get("status", ""))
        self._update_tags(requirement, request.form.get("tags"))
        self._update_description(requirement, request.form.get("description"))
        error, error_msg = self._update_formalizations(requirement)

        if error:
            logging.error(f"We got an error parsing the expressions: {error_msg}. Omitting requirement update.")
            return {"success": False, "errormsg": error_msg}

        variable_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        requirement.run_type_checks(
            variable_collection,
            SessionValue.get_standard_tags(current_app.db),
        )

        current_app.db.update()
        result = requirement.to_dict()
        if current_app.config.get("FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"):
            result["desc_highlighted"] = rehighlight_requirement(rid, requirement.description)
        else:
            result["desc_highlighted"] = result["desc"]
        return result, 200

    @staticmethod
    def _update_formalizations_order(requirement, order_json):
        if not order_json:
            return
        order_dict = json.loads(order_json)
        # TODO: still a problem with dictionary changing size, but the changes going through
        for idx, formalization in requirement.formalizations.items():
            formalization.order = order_dict.get(str(idx))
            logging.debug(f"Formalizaation of {idx} has order of {formalization.order}")

    @staticmethod
    def _update_status(requirement, new_status):
        if not new_status or requirement.status == new_status:
            return
        requirement.status = new_status
        add_msg_to_flask_session_log(current_app, f"Set status to {new_status} for requirement", [requirement])
        logging.debug(f"Requirement status set to {requirement.status}")

    @staticmethod
    def _update_tags(requirement, tags_json):
        if tags_json is None:
            return
        new_tag_set = json.loads(tags_json)
        req_tags = {t.name: c for t, c in requirement.tags.items()}
        if req_tags == new_tag_set:
            return

        added_tags = new_tag_set.keys() - req_tags.keys()
        all_tags: dict[str, Tag] = {t.name: t for t in current_app.db.get_objects(Tag).values()}
        removed_tags = req_tags.keys() - new_tag_set.keys()
        for tag in removed_tags:
            if tag not in all_tags:
                continue
            requirement.tags.pop(all_tags[tag])
        for tag, comment in new_tag_set.items():
            if tag not in all_tags:
                tag = Tag(tag, Color.BS_INFO.value, False, "")
                current_app.db.add_object(tag)
            else:
                tag = all_tags[tag]
            requirement.tags[tag] = comment
        add_msg_to_flask_session_log(
            current_app,
            f"Tags: + {added_tags} and - {removed_tags} to requirement",
            [requirement],
        )
        logging.debug(f"Tags: + {added_tags} and - {removed_tags} to requirement {requirement.rid}")

    @staticmethod
    def _update_description(requirement, desc_markdown):
        if desc_markdown is None:
            return
        requirement.description = desc_markdown
        add_msg_to_flask_session_log(
            current_app, f"Updated description for requirement", [requirement]
        )

    @staticmethod
    def _update_formalizations(requirement):
        if request.form.get("update_formalization") != "true":
            logging.debug("Skipping formalization update.")
            return False, ""

        formalizations = json.loads(request.form.get("formalizations", ""))
        if request.form.get("update_formalization") != "true":
            logging.debug("Skipping formalization update.")
            return False, ""

        formalizations = json.loads(request.form.get("formalizations", ""))
        logging.debug("Updated Formalizations: {}".format(formalizations))
        variable_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        logging.debug(f"Formalizations: {requirement.formalizations}")

        variable_entries = {k: v for k, v in formalizations.items() if v.get("formalization_type") == "variable"}
        formal_entries = {k: v for k, v in formalizations.items() if v.get("formalization_type") == "formalization"}
        logging.debug(f"Only Formalizations: {formal_entries}")
        logging.debug(f"Only Variables: {variable_entries}")

        if formal_entries:
            try:
                requirement.update_formalizations(
                    formal_entries,
                    SessionValue.get_standard_tags(current_app.db),
                    variable_collection,
                )
                add_msg_to_flask_session_log(current_app, "Updated requirement formalization", [requirement])
                for v in variable_collection.new_vars:
                    current_app.db.add_object(v)
                # Persist is_constraint on each updated formalization.
                for fid_str, entry in formal_entries.items():
                    try:
                        fid = int(fid_str)
                    except (TypeError, ValueError):
                        continue
                    if fid in requirement.formalizations and "is_constraint" in entry:
                        requirement.formalizations[fid].is_constraint = bool(entry.get("is_constraint", False))
            except KeyError as e:
                return (
                    True,
                    f"Could not set formalization: Missing expression/variable for {e}",
                )
            except Exception as e:
                return True, f"Could not parse formalization: `{e}`"

        logging.debug(f"variable_entries: {json.dumps(variable_entries, indent=2)}")
        for fid, entry in variable_entries.items():
            var_name = entry.get("name", "")
            var_type = entry.get("var_type", "")
            var_value = entry.get("const_val", "")
            enumerators = entry.get("enumerators", [])

            logging.debug(
                f"Variable update: fid={fid} name={var_name} type={var_type} "
                f"value={var_value} enumerators={enumerators}"
            )

            if int(fid) in requirement.formalizations:
                var = requirement.formalizations[int(fid)]
                logging.debug(f"Found in formalizations: name={var.name} old_type={var.type}")
                if isinstance(var, Variable):
                    old_name = var.name
                    if old_name != var_name:
                        if variable_collection.var_name_exists(old_name):
                            variable_collection.collection[var_name] = variable_collection.collection.pop(old_name)
                        try:
                            var.set_name(var_name)
                        except ValueError as e:
                            return True, str(e)
                    try:
                        var.set_type(var_type)
                    except ValueError as e:
                        return True, str(e)
                    var.value = var_value
                    logging.debug(f"Updated: name={var.name} type={var.type} value={var.value}")
                else:
                    logging.debug(f"Not a Variable instance, got: {type(var).__name__}")

            success, errormsg, _ = variable_collection.create_enum_variable(var_name, var_type, enumerators)
            if not success:
                return True, errormsg

        return False, ""


@api_ns.route("/<string:rid>/highlight-description")
@log_request_response
class ApiHighlightDescription(Resource):
    @api_ns.doc(description="Server-side variable highlighting for a description text.")
    @nocache
    def post(self, rid):
        body = request.get_json()
        if not body or "description" not in body:
            return {"success": False, "errormsg": "Missing 'description' field."}, 400

        if current_app.config.get("FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"):
            highlighted = highlight_text(body["description"])
        else:
            highlighted = body["description"]

        return {"desc_highlighted": highlighted}


@api_ns.route("/<string:rid>/formalizations")
@log_request_response
class ApiFormalizations(Resource):
    @api_ns.doc(
        description="Returns all formalizations (including variables) for "
        "a requirement, with enumerator data where applicable. "
        "Use ?subtype=formalization|variable to filter by type.",
        params={
            "rid": "The requirement ID",
            "subtype": "Query param: 'formalization' or 'variable'",
        },
    )
    @api_ns.response(200, "Success", [FormalizationModel])
    @nocache
    def get(self, rid):
        requirement = current_app.db.get_object(Requirement, rid)
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        subtype = request.args.get("subtype")
        result = []
        for idx, formalization in requirement.formalizations.items():
            if subtype and formalization.of_type() != subtype:
                continue
            formalization_repr = formalization.to_dict(var_collection=var_collection)
            formalization_repr["formalization_type"] = formalization.of_type()
            formalization_repr["id"] = idx
            formalization_repr["text"] = formalization.get_string()
            formalization_repr["is_constraint"] = formalization.is_constraint

            result.append(formalization_repr)
        return result


@api_ns.route("")
@log_request_response
class ApiRequirementsList(Resource):
    @api_ns.doc(
        description="Returns every requirement in the database "
        "as a sorted flat array. Called by the DataTable on page load."
    )
    @api_ns.response(200, "Success", RequirementListModel)
    @nocache
    def get(self):
        result = dict()
        result["data"] = list()
        reqs = current_app.db.get_objects(Requirement)
        result["data"] = [reqs[k].to_dict() for k in sorted(reqs.keys())]
        return result


@api_ns.route("/<string:rid>/formalizations/<string:fid>")
@api_ns.route("/<string:rid>/formalizations/<int:fid>")
@log_request_response
class ApiFormalizationResource(Resource):
    @api_ns.doc(
        description="Fetches a single formalization by rid and fid. "
        "Use ?subtype=formalization|variable to filter by type.",
        params={
            "rid": "The requirement ID",
            "fid": "The formalization ID",
            "subtype": "Query param: 'formalization' or 'variable'",
        },
    )
    @api_ns.response(200, "Success", FormalizationModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    def get(self, rid, fid):
        subtype = request.args.get("subtype")
        requirement = current_app.db.get_object(Requirement, rid)
        formalization = requirement.formalizations.get(int(fid))
        if not formalization:
            return {"success": False, "errormsg": "Formalization not found."}, 404
        if subtype and formalization.of_type() != subtype:
            return {"success": False, "errormsg": "Subtype mismatch."}, 404
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        result = formalization.to_dict(var_collection=var_collection)
        result["formalization_type"] = formalization.of_type()
        result["id"] = int(fid)
        result["text"] = formalization.get_string()
        return result

    @api_ns.doc(
        description="Removes the formalization with the given ID from " "the requirement and re-runs type inference.",
        params={
            "rid": "The requirement ID",
            "fid": "The formalization ID to delete",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @nocache
    def delete(self, rid, fid):
        logging.debug(f"Deletion formalization ID: {fid}")
        logging.debug(f"Deletion requirement ID: {rid}")
        requirement = current_app.db.get_object(Requirement, rid)
        logging.debug(f"Current: {requirement.formalizations}")
        requirement.delete_formalization(
            int(fid),
            VariableCollection(
                current_app.db.get_objects(Variable).values(),
                current_app.db.get_objects(Requirement).values(),
            ),
        )
        current_app.db.update()
        add_msg_to_flask_session_log(
            current_app,
            "Deleted formalization from requirement",
            [requirement],
        )
        return {"success": True}


@api_ns.route("/<string:rid>/formalizations/<any(formalization,variable):subtype>/<string:fid>")
@log_request_response
class ApiFormalizationStore(Resource):
    @api_ns.doc(
        description="Stores a formalization (real or variable) on a requirement. "
        "Creates the formalization or variable entry and updates "
        "the variable collection.",
        params={
            "rid": "The requirement ID",
            "subtype": "Either 'formalization' or 'variable'",
            "fid": "The formalization ID (integer for formalization, " "temp_id for variable)",
            "data": "JSON-encoded dict with scope, pattern, expression_mapping",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def post(self, rid, subtype, fid):
        data = json.loads(request.form.get("data", ""))
        ctx = SubtypeContext.load(rid)
        requirement = ctx.requirement
        if subtype == "formalization":
            fid = int(fid)
            logging.debug(f"FID: {fid}")

            # Validate before mutating: an incomplete payload must not leave a draft on the requirement.
            missing = [key for key in ("scope", "pattern", "expression_mapping") if key not in data]
            if missing:
                raise InvalidPayload(f"Missing required field(s): {', '.join(missing)}")

            requirement.add_formalization_with_id(Formalization(fid), fid)
            try:
                requirement.update_formalization(
                    fid,
                    data["scope"],
                    data["pattern"],
                    data["expression_mapping"],
                    ctx.variable_collection,
                    ctx.standard_tags,
                )
                add_msg_to_flask_session_log(current_app, "Updated requirement formalization", [requirement])
                for v in ctx.variable_collection.new_vars:
                    current_app.db.add_object(v)
                if current_app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"]:
                    new_variables_regenerate_highlighting(ctx.variable_collection.new_vars)
                # Persist is_constraint on the new formalization.
                if "is_constraint" in data:
                    requirement.formalizations[fid].is_constraint = bool(data["is_constraint"])
                # now rerun the inference checks, expensive, but works (and we don't care)
                requirement.run_type_checks(ctx.variable_collection, ctx.standard_tags)
            except Exception as e:
                # A create that fails must leave nothing behind, including a half applied draft.
                requirement.formalizations.pop(fid, None)
                raise InvalidPayload(f"Could not parse draft: `{e}`") from e

        elif subtype == "variable":
            logging.debug(f"Data set by the variable: {data}")

            try:
                var = Variable(
                    data["name"],
                    data["type"],
                    value=data.get("value"),
                    order=int(data["temp_id"]),
                )
                var.set_type(data["type"])
            except ValueError as e:
                raise InvalidPayload(str(e)) from e

            # The id of a variable is its own, assigned client side; the `fid` path segment is only a hint.
            requirement.add_formalization_with_id(var, int(data["temp_id"]))

            success, errormsg, _ = ctx.variable_collection.create_enum_variable(
                data["name"], data["type"], data.get("enumerators", [])
            )
            if not success:
                raise InvalidPayload(errormsg)

        current_app.db.update()
        return {"success": True}

    @api_ns.doc(
        description="Partially updates a formalization or variable. Only fields "
        "included in the 'data' JSON are changed; omitted fields keep "
        "their existing values. 404 if the fid does not exist.",
        params={
            "rid": "The requirement ID",
            "subtype": "Either 'formalization' or 'variable'",
            "fid": "The formalization ID",
            "data": "JSON-encoded dict with optional fields (scope, pattern, "
            "expression_mapping for formalizations; name, type, value, "
            "enumerators for variables)",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def patch(self, rid, subtype, fid):
        data = json.loads(request.form.get("data", "{}"))
        if not data:
            raise InvalidPayload("No data provided.")

        ctx = SubtypeContext.load(rid)
        requirement = ctx.requirement

        if subtype == "formalization":
            formalization = requirement.formalizations.get(int(fid))
            if not formalization or not isinstance(formalization, Formalization):
                raise SubtypeNotFound("Formalization not found.")

            merged_scope = data.get("scope", formalization.scoped_pattern.scope.name)
            merged_pattern = data.get("pattern", formalization.scoped_pattern.pattern.get_name())
            merged_mapping = {
                **{k: v.raw_expression for k, v in formalization.expressions_mapping.items()},
                **data.get("expression_mapping", {}),
            }

            try:
                requirement.update_formalization(
                    int(fid),
                    merged_scope,
                    merged_pattern,
                    merged_mapping,
                    ctx.variable_collection,
                    ctx.standard_tags,
                )
                for v in ctx.variable_collection.new_vars:
                    current_app.db.add_object(v)
            except KeyError as e:
                raise InvalidPayload(f"Could not update formalization: {e}") from e
            except Exception as e:
                raise InvalidPayload(f"Could not parse formalization: `{e}`") from e

        elif subtype == "variable":
            variable = requirement.formalizations.get(int(fid))
            if not variable or not isinstance(variable, Variable):
                raise SubtypeNotFound("Variable not found.")

            if "name" in data:
                try:
                    variable.set_name(data["name"])
                except ValueError as e:
                    raise InvalidPayload(str(e)) from e
            if "type" in data:
                variable.type = data["type"]
            if "value" in data:
                variable.value = data["value"]
            if "order" in data:
                variable.order = int(data["order"])

            if "enumerators" in data:
                success, errormsg, _ = ctx.variable_collection.create_enum_variable(
                    variable.name, variable.type, data["enumerators"]
                )
                if not success:
                    raise InvalidPayload(errormsg)

        current_app.db.update()
        add_msg_to_flask_session_log(
            current_app,
            f"Patched formalization {fid} of requirement",
            [requirement],
        )
        return {"success": True}

    @api_ns.doc(
        description="Fully replaces a formalization or variable. All required "
        "fields must be present. 404 if the fid does not exist, "
        "400 if required fields are missing.",
        params={
            "rid": "The requirement ID",
            "subtype": "Either 'formalization' or 'variable'",
            "fid": "The formalization ID",
            "data": "JSON-encoded dict. For formalizations: scope, pattern, "
            "expression_mapping (all required). For variables: "
            "name, type (required), value, order, enumerators (optional).",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def put(self, rid, subtype, fid):
        data = json.loads(request.form.get("data", "{}"))
        ctx = SubtypeContext.load(rid)
        requirement = ctx.requirement

        if subtype == "formalization":
            if "scope" not in data or "pattern" not in data or "expression_mapping" not in data:
                raise InvalidPayload("scope, pattern, and expression_mapping are required")

            formalization = requirement.formalizations.get(int(fid))
            if not formalization or not isinstance(formalization, Formalization):
                raise SubtypeNotFound("Formalization not found.")

            try:
                requirement.update_formalization(
                    int(fid),
                    data["scope"],
                    data["pattern"],
                    data["expression_mapping"],
                    ctx.variable_collection,
                    ctx.standard_tags,
                )
                for v in ctx.variable_collection.new_vars:
                    current_app.db.add_object(v)
            except KeyError as e:
                raise InvalidPayload(f"Could not update formalization: {e}") from e
            except Exception as e:
                raise InvalidPayload(f"Could not parse formalization: `{e}`") from e

        elif subtype == "variable":
            if "name" not in data or "type" not in data:
                raise InvalidPayload("name and type are required")

            variable = requirement.formalizations.get(int(fid))
            if not variable or not isinstance(variable, Variable):
                raise SubtypeNotFound("Variable not found.")

            try:
                variable.set_name(data["name"])
            except ValueError as e:
                raise InvalidPayload(str(e)) from e
            variable.type = data["type"]
            variable.value = data.get("value", "")
            variable.order = int(data.get("order", 0))

            if "enumerators" in data:
                success, errormsg, _ = ctx.variable_collection.create_enum_variable(
                    variable.name, variable.type, data["enumerators"]
                )
                if not success:
                    raise InvalidPayload(errormsg)

        current_app.db.update()
        add_msg_to_flask_session_log(
            current_app,
            f"Replaced formalization {fid} of requirement",
            [requirement],
        )
        return {"success": True}


@api_ns.route("/<string:rid>/tags/<string:tag_name>")
@log_request_response
class ApiRequirementTag(Resource):
    @api_ns.doc(
        description="Adds a tag to the requirement. Creates the Tag "
        "object if it doesn't exist. No-op if already present.",
        params={"rid": "The requirement ID", "tag_name": "Name of the tag to add"},
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    def post(self, rid, tag_name):
        try:
            requirement = current_app.db.get_object(Requirement, rid)
        except DatabaseKeyError:
            return {
                "success": False,
                "errormsg": f"Requirement '{rid}' not found.",
            }, 404
        all_tags: dict[str, Tag] = {t.name: t for t in current_app.db.get_objects(Tag).values()}
        if tag_name not in all_tags:
            tag = Tag(tag_name, Color.BS_INFO.value, False, "")
            current_app.db.add_object(tag)
        else:
            tag = all_tags[tag_name]
        if tag not in requirement.tags:
            requirement.tags[tag] = ""
            add_msg_to_flask_session_log(current_app, f"Added tag `{tag_name}` to requirement.", [requirement])
        current_app.db.update()
        return {"success": True}

    @api_ns.doc(
        description="Removes a tag from the requirement. " "No-op if the tag doesn't exist or isn't linked.",
        params={"rid": "The requirement ID", "tag_name": "Name of the tag to remove"},
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    def delete(self, rid, tag_name):
        try:
            requirement = current_app.db.get_object(Requirement, rid)
        except DatabaseKeyError:
            return {
                "success": False,
                "errormsg": f"Requirement '{rid}' not found.",
            }, 404
        all_tags: dict[str, Tag] = {t.name: t for t in current_app.db.get_objects(Tag).values()}
        if tag_name in all_tags and all_tags[tag_name] in requirement.tags:
            requirement.tags.pop(all_tags[tag_name])
            add_msg_to_flask_session_log(
                current_app,
                f"Removed tag `{tag_name}` from requirement.",
                [requirement],
            )
        current_app.db.update()
        return {"success": True}


@api_ns.route("/<string:rid>/guesses")
@log_request_response
class ApiRequirementGuesses(Resource):
    @api_ns.doc(
        description="Runs all registered guessers and returns available "
        "formalization guesses for the given requirement.",
        params={"rid": "The requirement ID"},
    )
    @api_ns.response(200, "Success", AvailableGuessesModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    def get(self, rid):
        requirement = current_app.db.get_object(Requirement, rid)
        if requirement is None:
            return {
                "success": False,
                "errormsg": f"Requirement '{rid}' not found.",
            }, 404

        result = {"available_guesses": []}
        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        tmp_guesses = []

        for guesser in REGISTERED_GUESSERS:
            try:
                guesser_instance = guesser(requirement, var_collection, current_app)
                guesser_instance.guess()
                tmp_guesses += guesser_instance.guesses
            except ValueError as e:
                return {
                    "success": False,
                    "errormsg": f"Could not determine a guess: {e}",
                }, 400

        tmp_guesses = sorted(tmp_guesses, key=Guess.eval_score)
        guesses = []
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

        return result


@api_ns.route("/add_formalization_from_guess")
@log_request_response
class ApiAddFormalizationFromGuess(Resource):
    @api_ns.doc(
        description="Adds an empty formalization, then fills it with "
        "the data from the selected scope, pattern, and mapping.",
        params={
            "requirement_id": "Requirement ID",
            "scope": "Scope name",
            "pattern": "Pattern name",
            "mapping": "JSON-encoded mapping dict",
        },
    )
    @api_ns.response(200, "Success")
    @nocache
    def post(self):
        requirement_id = request.form.get("requirement_id", "")
        scope = request.form.get("scope", "")
        pattern = request.form.get("pattern", "")
        mapping = request.form.get("mapping", "")
        mapping = json.loads(mapping)

        # Add an empty Formalization.
        requirement = current_app.db.get_object(Requirement, requirement_id)
        formalization_id, formalization = requirement.add_empty_formalization()
        # Add content to the formalization.
        variable_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        requirement.update_formalization(
            formalization_id=formalization_id,
            scope_name=scope,
            pattern_name=pattern,
            mapping=mapping,
            variable_collection=variable_collection,
            standard_tags=SessionValue.get_standard_tags(current_app.db),
        )
        for v in variable_collection.new_vars:
            current_app.db.add_object(v)
        current_app.db.update()
        add_msg_to_flask_session_log(current_app, "Added formalization guess to requirement", [requirement])

        result = get_formalization_template(
            current_app.config["TEMPLATES_FOLDER"],
            formalization_id,
            requirement.formalizations[formalization_id],
        )

        return result


@api_ns.route("/multi_add_top_guess")
@log_request_response
class ApiMultiAddTopGuess(Resource):
    @api_ns.doc(
        description="Adds the highest-scored guess to one or more " "requirements. Supports append and override modes.",
        params={
            "selected_ids": "JSON-encoded list of requirement IDs",
            "insert_mode": "'append' or 'override'",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @nocache
    def post(self):
        result = {"success": True}
        requirement_ids = request.form.get("selected_ids", "")
        insert_mode = request.form.get("insert_mode", "append")
        if len(requirement_ids) > 0:
            requirement_ids = json.loads(requirement_ids)
        else:
            result["success"] = False
            result["errormsg"] = "No requirements selected."

        if not result["success"]:
            return result

        var_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        requirements = [current_app.db.get_object(Requirement, rid) for rid in requirement_ids]
        for requirement in requirements:
            if requirement is not None:
                logging.info("Add top guess to requirement `{}`".format(requirement.rid))
                tmp_guesses = list()
                for guesser in REGISTERED_GUESSERS:
                    try:
                        guesser_instance = guesser(requirement, var_collection, current_app)
                        guesser_instance.guess()
                        tmp_guesses += guesser_instance.guesses
                        tmp_guesses = sorted(tmp_guesses, key=Guess.eval_score)
                        variable_collection = VariableCollection(
                            current_app.db.get_objects(Variable).values(),
                            current_app.db.get_objects(Requirement).values(),
                        )
                        if len(tmp_guesses) > 0:
                            if type(tmp_guesses[0]) is Guess:
                                top_guesses = [tmp_guesses[0]]
                            elif type(tmp_guesses[0]) is list:
                                top_guesses = tmp_guesses[0]
                            else:
                                raise TypeError("Type: `{}` not supported as guesses".format(type(tmp_guesses[0])))
                            if insert_mode == "override":
                                for f_id in requirement.formalizations.keys():
                                    requirement.delete_formalization(
                                        f_id,
                                        variable_collection,
                                    )
                            for score, scoped_pattern, mapping in top_guesses:
                                formalization_id, formalization = requirement.add_empty_formalization()
                                # Add content to the formalization.
                                requirement.update_formalization(
                                    formalization_id=formalization_id,
                                    scope_name=scoped_pattern.scope.name,
                                    pattern_name=scoped_pattern.pattern.name,
                                    mapping=mapping,
                                    variable_collection=variable_collection,
                                    standard_tags=SessionValue.get_standard_tags(current_app.db),
                                )
                                for v in variable_collection.new_vars:
                                    current_app.db.add_object(v)
                                current_app.db.update()

                    except ValueError as e:
                        result["success"] = False
                        result["errormsg"] = "Could not determine a guess: "
                        result["errormsg"] += e.__str__()
        add_msg_to_flask_session_log(current_app, "Added top guess to requirements", requirements)

        return result

        return result

def get_formalization_template(templates_folder, formalization_id, formalization):  # TODO wohin damit, HTML generation
    result = {
        "success": True,
        "html": formalization_html(
            templates_folder,
            formalization_id,
            default_scope_options,
            get_default_pattern_options(),
            formalization,
        ),
    }

    return result

def get_datatable_additional_cols(app: HanforFlask):  # TODO nach requirements
    offset = 8  # we have 8 fixed cols.
    result = list()

    for idx, name in enumerate(app.db.get_object(SessionValue, "csv_fieldnames").value):
        result.append(
            {
                "target": idx + offset,
                "csv_name": "csv_data.{}".format(name),
                "table_header_name": "csv: {}".format(name),
            }
        )

    return {"col_defs": result}


