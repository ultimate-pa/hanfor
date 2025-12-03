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
from lib_core.data import Requirement, VariableCollection, Variable

from jinja2 import Environment, FileSystemLoader
from rapidfuzz import process, fuzz
from itertools import combinations, permutations, product

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
highlight_tpl = env.get_template("highlight.html")


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
    html_template = html_template.replace("\n", "")

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

    var_collection = VariableCollection(app.db.get_objects(Variable).values(), app.db.get_objects(Requirement).values())
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


def _normalize_variable(var: str) -> set[str]:
    """Normalize a variable name by splitting camelCase, preserving number+letter tokens
    (e.g. "300M"), removing separators, and returning a lowercase set of words.

    :param var: Variable name to normalize
    :type var: str
    :return: Set of normalized lowercase words
    :rtype: set[str]
    """

    var = var.replace("_", " ").replace("-", " ")

    def camel_case_split(match) -> str:
        word = match.group()
        if re.fullmatch(r"\d+[A-Za-z]+", word):
            return word
        return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", word)

    var = re.sub(r"\b\w+\b", camel_case_split, var)
    var = re.sub(r"\s+", " ", var)
    return set(var.lower().strip().split())


def _normalize_and_group_positions_from_desc(desc: str) -> dict[str, list[tuple]]:
    """Extract all words from a description, split camelCase tokens, and map each
    lowercase sub-word to its absolute character positions in the text.

    :param desc: Input description text
    :type desc: str
    :return: Dict mapping each normalized word to a list of (start, end) positions
    :rtype: dict[str, list[tuple]]
    """

    word_positions = defaultdict(list)

    desc = desc.replace("_", " ").replace("-", " ")

    for match in re.finditer(r"\b\w+\b", desc):
        word = match.group()
        start = match.start()
        split_indices = [0] + [m.start() for m in re.finditer(r"(?<=[a-z])(?=[A-Z])", word)] + [len(word)]

        for i in range(len(split_indices) - 1):
            s = split_indices[i]
            e = split_indices[i + 1]
            sub_word = word[s:e].lower()
            word_positions[sub_word].append((start + s, start + e))

    return word_positions


def _words_between(pos1: (int, int), pos2: (int, int), word_positions: dict[str, list[tuple]]) -> int:
    """Count the number of words occurring between two character positions.

    :param pos1: Tuple of (start, end) indices for the first word
    :type pos1: tuple[int, int]
    :param pos2: Tuple of (start, end) indices for the second word
    :type pos2: tuple[int, int]
    :param word_positions: Dictionary mapping words to a list of their (start, end) positions
    :type word_positions: dict[str, list[tuple[int, int]]]
    :return: Number of words found between pos1 and pos2
    :rtype: int
    """

    start, end = pos1[1], pos2[0]
    count = 0
    for positions in word_positions.values():
        for p in positions:
            if start <= p[0] < end:
                count += 1
    return count


def _generate_all_ascending_combinations(
    pos_score_dict: dict, var_word_count: int, threshold: float
) -> list[tuple[int, list[tuple[int, int]]]]:
    """Generate all ascending combinations of variable word positions with scores.

    Ensures that positions are in ascending order (no overlap), applies a missing-word
    penalty, and filters combinations by a minimum score threshold.

    :param pos_score_dict: Dict mapping each word to a list of (position, score) tuples
    :type pos_score_dict: dict
    :param var_word_count: Total number of words in the variable
    :type var_word_count: int
    :param threshold: Minimum score required to keep a combination
    :type threshold: float
    :return: List of tuples (score, positions) for valid combinations
    :rtype: list[tuple[int, list[tuple[int, int]]]]
    """

    combos = []
    for r in range(1, len(pos_score_dict) + 1):
        for group_combo in combinations(list(pos_score_dict.keys()), r):
            for perm in permutations(group_combo):
                group_sets = [pos_score_dict[g] for g in perm]
                for combo in product(*group_sets):
                    positions = [p for (p, _) in combo]
                    scores = [s for (_, s) in combo]

                    ok = True
                    for (a_s, a_e), (b_s, b_e) in zip(positions, positions[1:]):
                        if b_s < a_e:
                            ok = False
                            break
                    if not ok:
                        continue

                    # missing-word penalty
                    missing = (var_word_count - len(positions)) * 20
                    score = (sum(scores) / len(scores)) - missing

                    if score >= threshold:
                        combos.append((score, positions))
    return combos


def _filter_combos(
    combos: list[tuple[float, list[tuple[int, int]]]], max_gap: int, word_positions: dict[str, list[tuple]]
) -> list[tuple[float, int, int, list[tuple[int, int]]]]:
    """Filter combinations by maximum word gap, remove overlapping lower-score segments,
    and select final segments with start and end positions.

    :param combos: List of (score, positions) tuples
    :type combos: list[tuple[float, list[tuple[int,int]]]]
    :param max_gap: Maximum number of words allowed between consecutive positions
    :type max_gap: int
    :param word_positions: Dictionary of word -> list of (start, end) positions in description
    :type word_positions: dict[str, list[tuple[int,int]]]
    :return: List of (score, start, end, positions) for filtered combinations
    :rtype: list[tuple[float, int, int, list[tuple[int,int]]]]
    """

    gap_filtered = []
    for score, positions in combos:
        if len(positions) <= 1:
            gap_filtered.append((score, positions))
            continue

        ok = True
        for p1, p2 in zip(positions, positions[1:]):
            if _words_between(p1, p2, word_positions) > max_gap:
                ok = False
                break

        if ok:
            gap_filtered.append((score, positions))

    # Remove overlapping if lower score
    gap_filtered = sorted(gap_filtered, key=lambda x: -x[0])
    cleaned = []
    for score, positions in gap_filtered:
        overlap = False
        for _, k_pos in cleaned:
            for s1, e1 in positions:
                for s2, e2 in k_pos:
                    if not (e1 <= s2 or s1 >= e2):
                        overlap = True
                        break
                if overlap:
                    break
            if overlap:
                break
        if not overlap:
            cleaned.append((score, positions))

    # Select segments for this variable
    selected = []
    for score, positions in cleaned:
        start = min(p[0] for p in positions)
        end = max(p[1] for p in positions)
        selected.append((score, start, end, positions))

    return selected


def highlight_desc_variable(
    desc: str, variables: list[str], threshold: int = 70, max_gap: int = 1, min_coverage: float = 0.55
) -> str:
    """Highlight variable names in a description using fuzzy matching,
    camelCase splitting, and gap/overlap handling.

    :param desc: Description text to search in
    :type desc: str
    :param variables: List of variable names to highlight
    :type variables: list[str]
    :param threshold: Minimum score for a match to be considered
    :type threshold: int
    :param max_gap: Maximum number of words allowed between parts of a variable
    :type max_gap: int
    :param min_coverage: Minimum fraction of variable words that must be matched
    :type min_coverage: float
    :return: HTML string with highlighted variable matches
    :rtype: str
    """

    # Normalize description and build word positions
    word_positions = _normalize_and_group_positions_from_desc(desc)
    desc_words = list(word_positions.keys())
    final_matches = []

    for var in variables:
        words = _normalize_variable(var)

        # Fuzzy match all pieces of the variable
        var_dict = {}
        for word_var in words:
            matches = list(process.extract_iter(query=word_var, choices=desc_words, scorer=fuzz.ratio, score_cutoff=80))
            if matches:
                var_dict[word_var] = [
                    {"score": score, "pos": word_positions[word_desc]} for word_desc, score, _ in matches
                ]

        # Skip variables with insufficient coverage
        if not var_dict or len(var_dict) / len(words) < min_coverage:
            continue

        # Build position-score dictionary
        pos_score_dict = {v: [(p, e["score"]) for e in lst for p in e["pos"]] for v, lst in var_dict.items()}

        # Generate all ascending combinations and filter them
        var_word_count = len(words)
        combos = _generate_all_ascending_combinations(pos_score_dict, var_word_count, threshold)
        selected = _filter_combos(combos, max_gap, word_positions)

        # Add matches for this variable
        for score, start, end, _ in selected:
            matched_text = desc[start:end]
            final_matches.append((start, end, matched_text, var, score))

    # Remove overlaps between different variables
    final_matches.sort(key=lambda x: (-x[4], x[0], x[1]))
    result, occupied = [], []
    for start, end, matched_text, var, score in final_matches:
        if not any(not (end <= os or start >= oe) for os, oe in occupied):
            result.append((start, end, matched_text, var, score))
            occupied.append((start, end))
    result.sort(key=lambda x: x[0])

    # Build HTML output
    out, last = [], 0
    for s, e, matched_text, var, score in result:
        out.append(desc[last:s])
        out.append(highlight_tpl.render(text=matched_text, var=var, score=score))
        last = e
    out.append(desc[last:])

    return "".join(out)
