from flask import Blueprint, request, render_template
import logging
import json
import datetime
import os


from hanfor_flask import current_app, nocache, HanforFlask
from lib_core.data import Requirement, VariableCollection, SessionValue, RequirementEditHistory, Tag
from lib_core.utils import (
    get_default_pattern_options,
    formalization_html,
    formalizations_to_html,
    default_scope_options,
)
from configuration.defaults import Color
from guesser.Guess import Guess
from guesser.guesser_registerer import REGISTERED_GUESSERS
from configuration.patterns import PATTERNS, VARIABLE_AUTOCOMPLETE_EXTENSION


blueprint = Blueprint("requirements", __name__, template_folder="templates", url_prefix="/")
api_blueprint = Blueprint("api_requirements", __name__, url_prefix="/api/req")


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
    return render_template(
        "index.html", query=request.args, additional_cols=additional_cols, default_cols=default_cols, patterns=PATTERNS
    )


@api_blueprint.route("/colum_defs", methods=["GET"])
@nocache
def table_api():
    result = get_datatable_additional_cols(current_app)
    return result


@api_blueprint.route("/get", methods=["GET"])
@nocache
def api_index():
    rid = request.args.get("id", "")
    requirement = current_app.db.get_object(Requirement, rid)
    var_collection = VariableCollection(current_app)

    result = requirement.to_dict(include_used_vars=True)
    result["formalizations_html"] = formalizations_to_html(current_app, requirement.formalizations)
    result["available_vars"] = var_collection.get_available_var_names_list(used_only=False, exclude_types={"ENUM"})

    result["additional_static_available_vars"] = VARIABLE_AUTOCOMPLETE_EXTENSION

    # Variable highlighting Info
    path = os.path.join(current_app.root_path, "variable_aliasing.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(e)
        data = {}

    # Build variable_mapping with only entries that contain the given rid
    variable_mapping = {
        var: {group: {rid: rids[rid]} for group, rids in groups.items() if rid in rids}
        for var, groups in data.items()
        if any(rid in rids for rids in groups.values())
    }
    result["variable_mapping"] = variable_mapping

    if requirement:
        return result
    return {"success": False, "errormsg": "This is not an api-enpoint."}, 404


@api_blueprint.route("/gets", methods=["GET"])
@nocache
def api_gets():
    result = dict()
    result["data"] = list()
    reqs = current_app.db.get_objects(Requirement)
    result["data"] = [reqs[k].to_dict() for k in sorted(reqs.keys())]
    return result


@api_blueprint.route("/update", methods=["POST"])
@nocache
def api_update():
    # Update a requirement
    rid = request.form.get("id", "")
    requirement = current_app.db.get_object(Requirement, rid)
    error = False
    error_msg = ""

    if requirement:
        logging.debug(f"Updating requirement: {requirement.rid}")

        new_status = request.form.get("status", "")
        if requirement.status != new_status:
            requirement.status = new_status
            add_msg_to_flask_session_log(current_app, f"Set status to {new_status} for requirement", [requirement])
            logging.debug(f"Requirement status set to {requirement.status}")

        new_tag_set = json.loads(request.form.get("tags", ""))
        req_tags = {t.name: c for t, c in requirement.tags.items()}
        if req_tags != new_tag_set:
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
            # do logging
            add_msg_to_flask_session_log(
                current_app, f"Tags: + {added_tags} and - {removed_tags} to requirement", [requirement]
            )
            logging.debug(f"Tags: + {added_tags} and - {removed_tags} to requirement {requirement.rid}")

        # Update formalization.
        if request.form.get("update_formalization") == "true":
            formalizations = json.loads(request.form.get("formalizations", ""))
            logging.debug("Updated Formalizations: {}".format(formalizations))
            try:
                requirement.update_formalizations(formalizations, current_app)
                add_msg_to_flask_session_log(current_app, "Updated requirement formalization", [requirement])
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
            return {"success": False, "errormsg": error_msg}
        else:
            current_app.db.update()
            return requirement.to_dict(), 200


@api_blueprint.route("/multi_update", methods=["POST"])
@nocache
def api_multi_update():
    # Multi Update Tags or Status.
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
        all_tags: dict[str, Tag] = {t.name: t for t in current_app.db.get_objects(Tag).values()}
        requirements = [current_app.db.get_object(Requirement, rid) for rid in rid_list]
        log_msg = f"Update {len(rid_list)} requirements."
        if len(add_tag) > 0:
            log_msg += f"Adding tag `{add_tag}`"
            add_msg_to_flask_session_log(current_app, f"Adding tag `{add_tag}` to requirements.", requirements)
            if add_tag not in all_tags:
                add_tag = Tag(add_tag, Color.BS_INFO.value, False, "")
                current_app.db.add_object(add_tag)
            else:
                add_tag = all_tags[add_tag]
        else:
            add_tag = None
        if len(remove_tag) > 0:
            log_msg += f", removing Tag `{remove_tag}` (is present)"
            add_msg_to_flask_session_log(current_app, f"Removing tag `{remove_tag}` from requirements.", requirements)
            if remove_tag not in all_tags:
                remove_tag = None
            else:
                remove_tag = all_tags[remove_tag]
        else:
            remove_tag = None
        if len(set_status) > 0:
            log_msg += ", set Status=`{}`.".format(set_status)
            add_msg_to_flask_session_log(current_app, f"Set status to `{set_status}` for requirements. ", requirements)
        logging.info(log_msg)

        for requirement in requirements:
            logging.info(f"Updating requirement `{requirement.rid}`")
            if remove_tag and remove_tag in requirement.tags:
                requirement.tags.pop(remove_tag)
            if add_tag and add_tag not in requirement.tags:
                requirement.tags[add_tag] = ""
            if set_status:
                requirement.status = set_status
        current_app.db.update()

    return result


@api_blueprint.route("/new_formalization", methods=["POST"])
@nocache
def api_new_formalization():
    # Add a new empty formalization
    rid = request.form.get("id", "")
    requirement = current_app.db.get_object(Requirement, rid)  # type: Requirement
    formalization_id, formalization = requirement.add_empty_formalization()
    current_app.db.update()
    add_msg_to_flask_session_log(current_app, "Added new Formalization to requirement", [requirement])
    result = get_formalization_template(current_app.config["TEMPLATES_FOLDER"], formalization_id, formalization)
    return result


@api_blueprint.route("/del_formalization", methods=["POST"])
@nocache
def api_del_formalization():
    # Delete a formalization
    result = dict()
    formalization_id = request.form.get("formalization_id", "")
    requirement_id = request.form.get("requirement_id", "")
    requirement = current_app.db.get_object(Requirement, requirement_id)
    requirement.delete_formalization(formalization_id, current_app)
    current_app.db.update()

    add_msg_to_flask_session_log(current_app, "Deleted formalization from requirement", [requirement])
    result["html"] = formalizations_to_html(current_app, requirement.formalizations)
    return result


@api_blueprint.route("/get_available_guesses", methods=["POST"])
@nocache
def api_get_available_guesses():
    # Get available guesses.
    result = {"success": True}
    requirement_id = request.form.get("requirement_id", "")
    requirement = current_app.db.get_object(Requirement, requirement_id)
    if requirement is None:
        result["success"] = False
        result["errormsg"] = "Requirement `{}` not found".format(requirement_id)
    else:
        result["available_guesses"] = list()
        tmp_guesses = list()
        var_collection = VariableCollection(current_app)

        for guesser in REGISTERED_GUESSERS:
            try:
                guesser_instance = guesser(requirement, var_collection, current_app)
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

    return result


@api_blueprint.route("/add_formalization_from_guess", methods=["POST"])
@nocache
def api_add_formalization_from_guess():
    requirement_id = request.form.get("requirement_id", "")
    scope = request.form.get("scope", "")
    pattern = request.form.get("pattern", "")
    mapping = request.form.get("mapping", "")
    mapping = json.loads(mapping)

    # Add an empty Formalization.
    requirement = current_app.db.get_object(Requirement, requirement_id)
    formalization_id, formalization = requirement.add_empty_formalization()
    # Add content to the formalization.
    requirement.update_formalization(
        formalization_id=formalization_id, scope_name=scope, pattern_name=pattern, mapping=mapping, app=current_app
    )
    current_app.db.update()
    add_msg_to_flask_session_log(current_app, "Added formalization guess to requirement", [requirement])

    result = get_formalization_template(
        current_app.config["TEMPLATES_FOLDER"], formalization_id, requirement.formalizations[formalization_id]
    )

    return result


@api_blueprint.route("/multi_add_top_guess", methods=["POST"])
@nocache
def api_multi_add_top_guess():
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

    var_collection = VariableCollection(current_app)
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
                    if len(tmp_guesses) > 0:
                        if type(tmp_guesses[0]) is Guess:
                            top_guesses = [tmp_guesses[0]]
                        elif type(tmp_guesses[0]) is list:
                            top_guesses = tmp_guesses[0]
                        else:
                            raise TypeError("Type: `{}` not supported as guesses".format(type(tmp_guesses[0])))
                        if insert_mode == "override":
                            for f_id in requirement.formalizations.keys():
                                requirement.delete_formalization(f_id, current_app)
                        for score, scoped_pattern, mapping in top_guesses:
                            formalization_id, formalization = requirement.add_empty_formalization()
                            # Add content to the formalization.
                            requirement.update_formalization(
                                formalization_id=formalization_id,
                                scope_name=scoped_pattern.scope.name,
                                pattern_name=scoped_pattern.pattern.name,
                                mapping=mapping,
                                app=current_app,
                            )
                            current_app.db.update()

                except ValueError as e:
                    result["success"] = False
                    result["errormsg"] = "Could not determine a guess: "
                    result["errormsg"] += e.__str__()
    add_msg_to_flask_session_log(current_app, "Added top guess to requirements", requirements)

    return result


def get_formalization_template(templates_folder, formalization_id, formalization):  # TODO wohin damit, HTML generation
    result = {
        "success": True,
        "html": formalization_html(
            templates_folder, formalization_id, default_scope_options, get_default_pattern_options(), formalization
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


def add_msg_to_flask_session_log(
    app: HanforFlask, message: str, req_list: list[Requirement] = None
) -> None:  # TODO nach requirements
    """Add a log message for the frontend_logs.

    :param req_list: A list of affected requirements
    :param app: The flask app
    :param message: Log message string
    """
    app.db.add_object(RequirementEditHistory(datetime.datetime.now(), message, req_list))
