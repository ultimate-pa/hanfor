import json
import logging
import threading
from contextlib import contextmanager

from flask import Blueprint, render_template, request
from flask_restx import Namespace, Resource

from config import PATTERNS_GROUP_ORDER
from configuration.defaults import Color
from guesser.Guess import Guess
from guesser.guesser_registerer import REGISTERED_GUESSERS
from hanfor_flask import HanforFlask, current_app, nocache
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
    log_request_response,
    prepare_patterns_for_jinja,
)
from requirements.subtypes import (
    SUBTYPES,
    InvalidPayload,
    SubtypeContext,
    SubtypeError,
    SubtypeHandler,
    SubtypeNotFound,
    subtype_errors_to_response,
)
from requirements.desc_highlighting import (
    get_highlighted_desc,
    highlight_text,
    rehighlight_requirement,
)

blueprint = Blueprint("requirements", __name__, template_folder="templates", url_prefix="/")
api_ns = Namespace("Requirements", "Requirements API description", path="/req", ordered=True)
_SUBTYPE_WRITE_LOCK = threading.Lock()


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
        variable_name_regex=Variable.NAME_REGEX,
        query=request.args,
        additional_cols=additional_cols,
        default_cols=default_cols,
        pattern_groups=pattern_groups,
        group_order=PATTERNS_GROUP_ORDER,
        patterns=APattern().to_frontent_dict(),
    )


@api_ns.route("/column-defs")
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
    @subtype_errors_to_response
    def get(self, rid):
        requirement = SubtypeContext.load(rid).requirement
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
        return result

    @api_ns.doc(
        description="Changes only the fields in the JSON body. The other fields keep their values. "
        "To change a formalization or a variable, use /<rid>/formalizations/<fid>.",
        params={
            "rid": "The requirement ID",
            "status": "Body field: the new status. An empty string makes no change",
            "description": "Body field: the new description",
            "tags": "Body field: a dict of {tag_name: comment}. It replaces all tags",
            "formalizations_order": "Body field: a dict of {fid: order}",
        },
    )
    @api_ns.response(200, "Success", RequirementDetailModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def patch(self, rid):
        requirement = SubtypeContext.load(rid).requirement

        body = request.get_json(silent=True) or {}
        self._update_formalizations_order(requirement, body.get("formalizations_order"))
        self._update_status(requirement, body.get("status", ""))
        self._update_tags(requirement, body.get("tags"))
        self._update_description(requirement, body.get("description"))

        standard_tags = SessionValue.get_standard_tags(current_app.db)
        requirement.recompute_formalization_tags(standard_tags)
        variable_collection = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )
        requirement.run_type_checks(variable_collection, standard_tags)

        current_app.db.update()
        result = requirement.to_dict()
        if current_app.config.get("FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"):
            result["desc_highlighted"] = rehighlight_requirement(rid, requirement.description)
        else:
            result["desc_highlighted"] = result["desc"]
        return result, 200

    @staticmethod
    def _update_formalizations_order(requirement, order_dict):
        if not order_dict:
            return
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
    def _update_tags(requirement, new_tag_set):
        if new_tag_set is None:
            return
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
        add_msg_to_flask_session_log(current_app, f"Updated description for requirement", [requirement])


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
        "Use ?subtype=formalization | variable to filter by type.",
        params={
            "rid": "The requirement ID",
            "subtype": "Query param: 'formalization' or 'variable'",
        },
    )
    @api_ns.response(200, "Success", [FormalizationModel])
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def get(self, rid):
        ctx = SubtypeContext.load(rid)
        subtype = request.args.get("subtype")
        return [
            SUBTYPES[element.of_type()].handler.serialize(ctx, fid)
            for fid, element in ctx.requirement.formalizations.items()
            if not subtype or element.of_type() == subtype
        ]


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
    @subtype_errors_to_response
    def get(self, rid, fid):
        ctx = SubtypeContext.load(rid)
        subtype = request.args.get("subtype")
        if subtype and subtype not in SUBTYPES:
            raise SubtypeNotFound(f"Unknown subtype '{subtype}'.")
        handler = SUBTYPES[subtype].handler if subtype else SubtypeHandler.handler_for(ctx, fid)
        return handler.serialize(ctx, fid)

    @api_ns.doc(
        description="Changes only the fields in 'data' of the formalization or variable. The other fields "
        "keep their values. The server finds the subtype from the element. Gives 404 if the ID is not found.",
        params={
            "rid": "The requirement ID",
            "fid": "The formalization ID",
            "data": "A JSON dict. All fields are optional. For a formalization: scope, pattern, "
            "expression_mapping. For a variable: name, type, value, order, enumerators",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def patch(self, rid, fid):
        data = _request_data()
        if not data:
            raise InvalidPayload("No data provided.")
        with _subtype_write(rid, f"Patched formalization {fid} of requirement") as ctx:
            SubtypeHandler.handler_for(ctx, fid).patch(ctx, fid, data)
        return {"success": True}

    @api_ns.doc(
        description="Replaces all fields of the formalization or variable. 'data' must have all the "
        "required fields. The server finds the subtype from the element. Gives 404 if the ID is not found, "
        "and 400 if a required field is missing.",
        params={
            "rid": "The requirement ID",
            "fid": "The formalization ID",
            "data": "A JSON dict. For a formalization: scope, pattern, expression_mapping (all required). "
            "For a variable: name, type (required), value, order, enumerators (optional)",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def put(self, rid, fid):
        data = _request_data()
        with _subtype_write(rid, f"Replaced formalization {fid} of requirement") as ctx:
            SubtypeHandler.handler_for(ctx, fid).replace(ctx, fid, data)
        return {"success": True}

    @api_ns.doc(
        description="Deletes the formalization or variable and calculates the formalization tags again. "
        "Gives 404 if the ID is not found.",
        params={
            "rid": "The requirement ID",
            "fid": "The formalization ID",
        },
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def delete(self, rid, fid):
        with _subtype_write(rid, f"Deleted formalization {fid} from requirement") as ctx:
            SubtypeHandler.handler_for(ctx, fid).delete(ctx, fid)
        return {"success": True}


@contextmanager
def _subtype_write(rid: str, log_message: str):
    """
    Manager for the writing context in requirements, with the block before the yield running on start
    of the `with` block, yielding then returns the ctx to the block for it to be used `as` a variable
    and then then the code after running after the with ends normally, allowing us to minimize code needed
    """
    with _SUBTYPE_WRITE_LOCK:
        ctx = SubtypeContext.load(rid)
        yield ctx
        current_app.db.update()
        add_msg_to_flask_session_log(current_app, log_message, [ctx.requirement])


def _request_data() -> dict:
    """
    The `data` form field, parsed. Absent or empty is an empty dict, never a 500 from `json.loads`.
    A helper to make code more readable
    """
    return json.loads(request.form.get("data") or "{}")


@api_ns.route(f"/<string:rid>/formalizations/<any({','.join(SUBTYPES)}):subtype>")
@log_request_response
class ApiFormalizationStoreBatch(Resource):
    @api_ns.doc(
        description="Creates several formalizations or variables on a requirement in one write. "
        "Drafts that fail are skipped (for now) the others are still created.",
        params={
            "rid": "The requirement ID",
            "subtype": f"One of {', '.join(SUBTYPES)}",
            "data": "A JSON list of drafts. Each draft has a temp_id and the fields of the subtype",
        },
    )
    @api_ns.response(201, "Created", SuccessResponseModel)
    @api_ns.response(400, "Bad Request", ErrorMessageModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def post(self, rid, subtype):
        drafts = json.loads(request.form.get("data") or "[]")
        handler = SUBTYPES[subtype].handler
        ids, errors = {}, {}
        with _subtype_write(rid, f"Created {subtype} drafts of requirement") as ctx:
            for draft in drafts:
                try:
                    ids[draft["temp_id"]] = handler.create(ctx, draft["temp_id"], draft)
                except SubtypeError as e:
                    errors[draft["temp_id"]] = str(e)
        if errors:
            errormsg = "; ".join(f"{k}: {v}" for k, v in errors.items())
            return {"success": False, "ids": ids, "errors": errors, "errormsg": errormsg}, 400
        return {"success": True, "ids": ids}, 201


@api_ns.route("/<string:rid>/tags/<string:tag_name>")
@log_request_response
class ApiRequirementTag(Resource):
    @api_ns.doc(
        description="Adds the tag to the requirement. If the tag does not exist, the server makes it. "
        "If the requirement has the tag, nothing changes. A second request gives the same result.",
        params={"rid": "The requirement ID", "tag_name": "The name of the tag to add"},
    )
    @api_ns.response(200, "Success", SuccessResponseModel)
    @api_ns.response(404, "Not Found", ErrorMessageModel)
    @nocache
    @subtype_errors_to_response
    def put(self, rid, tag_name):
        requirement = SubtypeContext.load(rid).requirement
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
    @subtype_errors_to_response
    def delete(self, rid, tag_name):
        requirement = SubtypeContext.load(rid).requirement
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
    @subtype_errors_to_response
    def get(self, rid):
        requirement = SubtypeContext.load(rid).requirement

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
