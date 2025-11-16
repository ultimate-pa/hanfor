import logging
import re
import os
import html
import shlex
import colorama
from collections import defaultdict
from colorama import Style, Fore
from terminaltables import DoubleTable

from flask import Response

from configuration.patterns import APattern
from lib_core import boogie_parsing
from config import PATTERNS_GROUP_ORDER  # TODO should this be in the config?
from hanfor_flask import HanforFlask
from lib_core.data import Requirement, VariableCollection


default_scope_options = """
    <option value="NONE">None</option>
    <option value="GLOBALLY">Globally</option>
    <option value="BEFORE">Before "{P}"</option>
    <option value="AFTER">After "{P}"</option>
    <option value="BETWEEN">Between "{P}" and "{Q}"</option>
    <option value="AFTER_UNTIL">After "{P}" until "{Q}"</option>
    """


def get_requirements(app: HanforFlask, filter_list=None, invert_filter=False):
    """Load all requirements from session folder and return in a list.
    Orders the requirements based on their position in the CSV used to create the session (pos_in_csv).

    :param app: current app
    :param filter_list: A list of requirement IDs to be included in the result. All if not set.
    :type filter_list: list (of strings)
    :param invert_filter: Exclude filter
    :type invert_filter: bool
    """

    def should_be_in_result(requirement) -> bool:
        if filter_list is None:
            return True
        return (requirement.rid in filter_list) != invert_filter

    requirements = list()
    for req in app.db.get_objects(Requirement).values():
        if should_be_in_result(req):
            logging.debug("Adding {} to results.".format(req.rid))
            requirements.append(req)

    # We want to preserve the order of the generated CSV relative to the origin CSV.
    requirements.sort(key=lambda x: x.pos_in_csv)

    return requirements


def get_default_pattern_options():
    """Parse the pattern config into the dropdown list options for the frontend

    Returns (str): Options for pattern selection in HTML.

    """
    result = '<option value="NotFormalizable">None</option>'
    opt_group_lists = defaultdict(list)
    opt_groups = defaultdict(str)
    # Collect pattern in groups.
    for name, pattern in APattern.get_patterns().items():
        opt_group_lists[pattern.group].append((pattern.order, name, pattern._pattern_text))

    # Sort groups and concatenate pattern options
    for group_name, opt_list in opt_group_lists.items():
        for _, name, pattern in sorted(opt_list):
            option = f'<option value="{name}">{pattern}</option>'
            opt_groups[group_name] += option

    # Enclose pattern options by their groups.
    for group_name in PATTERNS_GROUP_ORDER:
        result += '<optgroup label="{}">'.format(group_name)
        result += opt_groups[group_name]
        result += "</optgroup>"

    return result


def formalization_html(
    templates_folder, formalization_id, scope_options, pattern_options, formalization
):  # TODO wohin damit, HTML generation
    # Load template.
    html_template = ""
    with open(os.path.join(templates_folder, "formalization.html"), mode="r") as f:
        html_template += "\n".join(f.readlines())

    # Set values
    html_template = html_template.replace("__formalization_text__", formalization.get_string())
    html_template = html_template.replace("__formal_id__", "{}".format(formalization_id))
    form_desc = formalization.get_string()
    if len(form_desc) < 10:  # Add hint to open if desc is short.
        form_desc += "... (click to open)"
    html_template = html_template.replace("__formal_desc__", form_desc)

    # Selected scope and pattern:
    if formalization.scoped_pattern is not None:
        scope = formalization.scoped_pattern.get_scope_slug()
        pattern = formalization.scoped_pattern.get_pattern_slug()
        scope_options = scope_options.replace('value="{}"'.format(scope), 'value="{}" selected'.format(scope))
        pattern_options = pattern_options.replace('value="{}"'.format(pattern), 'value="{}" selected'.format(pattern))
    html_template = html_template.replace("__scope_options__", scope_options)
    html_template = html_template.replace("__pattern__options__", pattern_options)

    # Expressions
    for key, value in formalization.expressions_mapping.items():
        html_template = html_template.replace(
            "__expr_{}_content__".format(key), "{}".format(html.escape(str(value.raw_expression)))
        )

    # Unset remaining vars.
    html_template = re.sub(r"__expr_._content__", "", html_template)

    return html_template


def formalizations_to_html(app: HanforFlask, formalizations):  # TODO wohin damit, HTML generation
    result = ""
    for index, formalization in formalizations.items():
        result += formalization_html(
            app.config["TEMPLATES_FOLDER"], index, default_scope_options, get_default_pattern_options(), formalization
        )
    return result


def enable_logging(log_level=logging.ERROR, to_file=False, filename="reqtransformer.log"):
    """Enable Logging.

    :param log_level: Log level
    :type log_level: int
    :param to_file: Whether output should be stored in a file.
    :type to_file: bool
    :param filename: Filename to log to.
    :type filename: str
    """
    if to_file:
        logging.basicConfig(format="%(asctime)s: [%(levelname)s]: %(message)s", filename=filename, level=log_level)
    else:
        logging.basicConfig(format="%(asctime)s: [%(levelname)s]: %(message)s", level=log_level)
    logging.debug("Enabled logging.")


def setup_logging(app: HanforFlask):
    """Initializes logging with settings from the config."""
    if app.config["LOG_LEVEL"] == "DEBUG":
        log_level = logging.DEBUG
    elif app.config["LOG_LEVEL"] == "INFO":
        log_level = logging.INFO
    elif app.config["LOG_LEVEL"] == "WARNING":
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR

    enable_logging(log_level=log_level, to_file=app.config["LOG_TO_FILE"], filename=app.config["LOG_FILE"])


def generate_file_response(content, name, mimetype="text/plain"):
    response = Response(content, mimetype=mimetype)
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{name}"
    return response


def generate_req_file_content(
    app: HanforFlask, filter_list=None, invert_filter=False, variables_only=False
):  # TODO nach tools
    """Generate the content (string) for the ultimate requirements file.
    :param app: Current app.
    :type app: FlaskApp
    :param filter_list: A list of requirement IDs to be included in the result. All if not set.
    :type filter_list: list (of strings)
    :param invert_filter: Exclude filter
    :type invert_filter: bool
    :type invert_filter: bool
    :param variables_only: If true, only variables and no requirements will be included.
    :return: Content for the req file.
    :rtype: str
    """
    logging.info("Generating .req file content for session {}".format(app.config["SESSION_TAG"]))
    # Get requirements
    requirements = get_requirements(app, filter_list=filter_list, invert_filter=invert_filter)

    var_collection = VariableCollection(app)
    available_vars = []
    if filter_list is not None:
        # Filter the available vars to only include the ones actually used by a requirement.
        logging.info("Filtering the .req file to only include {} selected requirements.".format(len(filter_list)))
        logging.debug("Only include req.ids: {}.".format(filter_list))
        target_set = set(filter_list)
        for var in var_collection.get_available_vars_list(sort_by="name"):
            try:
                used_in = var_collection.var_req_mapping[var["name"]]
                if used_in & target_set:
                    available_vars.append(var)
            except Exception:  # noqa
                logging.debug("Ignoring variable `{}`".format(var))
    else:
        available_vars = var_collection.get_available_vars_list(sort_by="name")

    available_vars = [var["name"] for var in available_vars]

    content_list = []
    constants_list = []
    constraints_list = []

    # Parse variables and variable constraints.
    for var in var_collection.collection.values():
        if var.name in available_vars:
            if var.type in ["CONST", "ENUMERATOR_INT", "ENUMERATOR_REAL"]:
                constants_list.append("CONST {} IS {}".format(var.name, var.value))
            else:
                content_list.append(
                    "Input {} IS {}".format(var.name, boogie_parsing.BoogieType.reverse_alias(var.type).name)
                )
            try:
                for index, constraint in var.constraints.items():
                    if constraint.scoped_pattern is None:
                        continue
                    if constraint.scoped_pattern.get_scope_slug().lower() == "none":
                        continue
                    if constraint.scoped_pattern.get_pattern_slug() in ["NotFormalizable", "None"]:
                        continue
                    if len(constraint.get_string()) == 0:
                        continue
                    constraints_list.append(
                        "Constraint_{}_{}: {}".format(re.sub(r"\s+", "_", var.name), index, constraint.get_string())
                    )
            except Exception:
                # TODO: this is not a nice way to solve this
                pass
    content_list.sort()
    constants_list.sort()
    constraints_list.sort()

    content = "\n".join(content_list)
    constants = "\n".join(constants_list)
    constraints = "\n".join(constraints_list)

    if len(constants) > 0:
        content = "\n\n".join([constants, content])
    if len(constraints) > 0:
        content = "\n\n".join([content, constraints])
    content += "\n\n"

    # parse requirement formalizations.
    if not variables_only:
        used_identifiers = set()
        for requirement in requirements:  # type: Requirement
            try:
                for index, formalization in requirement.formalizations.items():
                    identifier = clean_identifier_for_ultimate_parser(requirement.rid, index, used_identifiers)
                    if formalization.scoped_pattern is None:
                        continue
                    if formalization.scoped_pattern.get_scope_slug().lower() == "none":
                        continue
                    if formalization.scoped_pattern.get_pattern_slug() in ["NotFormalizable", "None"]:
                        continue
                    if len(formalization.get_string()) == 0:
                        # Formalization string is empty if expressions are missing or none set. Ignore in output
                        continue
                    content += "{}: {}\n".format(identifier, formalization.get_string())
            except AttributeError:
                continue
    content += "\n"

    return content


def clean_identifier_for_ultimate_parser(req_id: str, formalisation_id: int, used_identifiers: set[str]) -> str:
    """Clean slug to be sound for ultimate parser.

    :param req_id: The requirement id to be cleaned.
    :param formalisation_id: The formalisation id to be cleaned.
    :param used_identifiers: Set of already used identifiers.
    :return: (identifier, used_slugs) save_slug a save to use form of slug. save_slug added to used_slugs.
    """
    # Replace any occurrence of [whitespace, `.`, `-`] with `_`
    base_identifier = re.sub(r"[\s+.-]+", "_", req_id.strip())

    # Resolve illegal start by prepending the slug with ID_ in case it does not start with a letter.
    base_identifier = re.sub(r"^([^a-zA-Z])", r"ID_\1", base_identifier)

    def create_identifier(base: str, extension: int, base_suffix: int = -1):
        if base_suffix == -1:
            return "{}_{}".format(base, extension)
        return "{}_{}_{}".format(base, base_suffix, extension)

    identifier = create_identifier(base_identifier, formalisation_id)

    # Resolve duplicates
    # search for the first free suffix.
    if identifier in used_identifiers:
        suffix = 1

        while create_identifier(base_identifier, formalisation_id, suffix) in used_identifiers:
            suffix += 1
        identifier = create_identifier(base_identifier, formalisation_id, suffix)

    used_identifiers.add(identifier)

    return identifier


def get_filenames_from_dir(input_dir):
    """Returns the list of filepaths for all files in input_dir.

    :param input_dir: Location of the input directory
    :type input_dir: str
    :return: List of file locations [<input_dir>/<filename>, ...]
    :rtype: list
    """
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]


def choice(choices: list[str], default: str) -> str:
    """Asks the user which string he wants from a list of strings.
    Returns the selected string.

    :param choices: List of choices (one choice is a string)
    :param default: One element from the choices list.
    :return: The choice selected by the user.
    """
    idx = 0
    data = list()
    colorama.init()
    default_idx = 0
    for c in choices:
        if c == default:
            data.append(
                [
                    "{}-> {}{}".format(Fore.GREEN, idx, Style.RESET_ALL),
                    "{}{}{}".format(Fore.GREEN, c, Style.RESET_ALL),
                ]
            )
            default_idx = idx
        else:
            data.append([idx, c])
        idx = idx + 1

    table = DoubleTable(data, title="Choices")
    table.inner_heading_row_border = False
    print(table.table)

    while True:
        input_msg = "{}[Choice or Enter for {} -> default ({}){}]> {}".format(
            Fore.LIGHTBLUE_EX, Fore.GREEN, default_idx, Fore.LIGHTBLUE_EX, Style.RESET_ALL
        )
        print(input_msg, end="")
        last_in = input()

        if len(last_in) == 0:
            return choices[default_idx]

        c, *args = shlex.split(last_in)
        if len(args) > 0:
            print("What did you mean?")
            continue

        try:
            c = int(c)
        except ValueError:
            print('Illegal choice "' + str(c) + '", choose again')
            continue

        if 0 <= c < idx:
            return choices[c]

        print('Illegal choice "' + str(c) + '", choose again')
