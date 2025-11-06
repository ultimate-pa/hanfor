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


import re
from itertools import permutations
from fuzzywuzzy import fuzz


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

    print(result["available_vars"])
    print(result["desc"])
    result["desc"] = desc_var_highlighter_html(result["desc"], result["available_vars"])

    result["additional_static_available_vars"] = VARIABLE_AUTOCOMPLETE_EXTENSION
    if requirement:
        return result
    return {"success": False, "errormsg": "This is not an api-enpoint."}, 404


def desc_var_highlighter_html(desc: str, variables: list[str], threshold: int = 60) -> str:
    """Highlight variable mentions in a text with fuzzy matching and click-to-copy functionality."""

    def camel_to_words(var: str) -> str:
        var = var.replace("_", " ")
        return re.sub(r"(?<!^)(?=[A-Z])", " ", var).lower().strip()

    def generate_variants(words: str) -> list[str]:
        # Generate all permutations of the variable words if 3 or fewer words
        tokens = words.split()
        return [" ".join(p) for p in permutations(tokens)] if len(tokens) <= 3 else [words]

    def make_clickable_html(text: str, var: str, score: int) -> str:
        """Return HTML for a highlighted variable with click-to-copy tooltip."""
        return (
            f"<b style='cursor:pointer;' title='{var} [{score}]' onclick=\""
            f"navigator.clipboard.writeText('{var}');"
            f"let tip=document.createElement('span');"
            f"tip.innerText='Copied!';"
            f"tip.style.position='absolute';"
            f"tip.style.background='yellow';"
            f"tip.style.padding='2px 4px';"
            f"tip.style.borderRadius='3px';"
            f"tip.style.zIndex='9999';"
            f"document.body.appendChild(tip);"
            f"let rect=this.getBoundingClientRect();"
            f"tip.style.left=rect.left+'px';"
            f"tip.style.top=(rect.top-25)+'px';"
            f"setTimeout(()=>tip.remove(),1000);"
            f'">{text} <i>[{var}:{score}]</i></b>'
        )

    # Tokenize description text
    word_iter = list(re.finditer(r"\b\w+\b", desc))
    words = [m.group(0) for m in word_iter]
    spans = [(m.start(), m.end()) for m in word_iter]
    n_words = len(words)

    candidate_spans = []

    for var in variables:
        for variant in generate_variants(camel_to_words(var)):
            variant_tokens = variant.split()
            min_window = 1
            max_window = len(variant_tokens) + 2
            best_score = 0
            best_span = None

            # Slide window over text to find best fuzzy match
            for window_size in range(min_window, max_window + 1):
                for i in range(n_words - window_size + 1):
                    start, end = spans[i][0], spans[i + window_size - 1][1]
                    span_text = desc[start:end]
                    span_tokens = [w.lower() for w in words[i : i + window_size]]

                    score = fuzz.token_set_ratio(variant.lower(), span_text.lower())

                    # Penalize missing tokens
                    missing_tokens = [
                        t for t in variant_tokens if not any(fuzz.ratio(t, st) >= 90 for st in span_tokens)
                    ]
                    punish = len(missing_tokens) * 20
                    score -= punish
                    score = max(score, 0)

                    if score > best_score:
                        best_score = score
                        best_span = (start, end, span_text, score, window_size)

            if best_span and best_score >= threshold:
                candidate_spans.append((best_span[0], best_span[1], best_span[2], var, int(round(best_span[3]))))

    # Greedy selection of non-overlapping spans
    candidate_spans.sort(key=lambda x: (-x[4], x[0]))
    chosen = []
    occupied = [False] * (len(desc) + 1)
    for s, e, txt, var, score in candidate_spans:
        if any(occupied[s:e]):
            continue
        chosen.append((s, e, txt, var, score))
        for pos in range(s, e):
            occupied[pos] = True

    # Build final HTML with highlighted spans
    chosen.sort(key=lambda x: x[0])
    out = []
    last = 0
    for s, e, txt, var, score in chosen:
        out.append(desc[last:s])
        out.append(make_clickable_html(txt, var, score))
        last = e
    out.append(desc[last:])

    return "".join(out)


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
    formalization_data = json.loads(request.form.get("formalization", ""))
    if len(formalization_data) != 0:
        requirement.update_formalization(
            formalization_id,
            scope_name=formalization_data["scope"],
            pattern_name=formalization_data["pattern"],
            mapping=formalization_data["expression_mapping"],
            app=current_app,
        )
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
