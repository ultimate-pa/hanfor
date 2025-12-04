import os
import re
from collections import defaultdict
from typing import List, Dict, Optional
from jinja2 import Environment, FileSystemLoader
from rapidfuzz import process, fuzz
from itertools import combinations, permutations, product
from hanfor_flask import current_app
from lib_core.data import Requirement, VariableCollection, Variable

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
highlight_tpl = env.get_template("highlight.html")

highlight_desc_from_req_id = defaultdict(dict)


def updated_variables(variables: set) -> None:
    """
    Process a set of updated variable objects and trigger regeneration of highlighted
    descriptions for all requirements.

    :param variables: Set of variable objects that contain a `.name` attribute
    :type variables: set
    """
    variable_list = [v.name for v in variables]

    if variable_list:
        generate_all_highlighted_desc(variable_list)


def generate_all_highlighted_desc(new_variables: Optional[List[str]] = None) -> None:
    """
    Regenerates highlighted descriptions for all requirements.
    If a list of updated variable names is provided, only these variables will
    be reprocessed inside each requirement.

    :param new_variables: Optional list of updated variable names
    :type new_variables: list[str] | None
    """
    reqs = current_app.db.get_objects(Requirement)
    req_ids = [reqs[k].to_dict()["id"] for k in sorted(reqs.keys())]
    for req_id in req_ids:
        get_highlighted_desc(req_id, new_variables)


def get_highlighted_desc(req_id: str, variables: Optional[List[str]] = None) -> Dict[str, Dict]:
    """
    Retrieves / generates / updates the highlighted description for the given requirement.

    - On first call: builds all variable matches for the requirement.
    - On update calls: only new/changed variable names are reprocessed and merged.

    :param req_id: ID of the requirement to highlight
    :type req_id: str
    :param variables: Optional list of variable names to update
    :type variables: list[str] | None
    :return: Highlight result with matches and generated HTML
    :rtype: dict[str, dict]
    """
    req = current_app.db.get_object(Requirement, req_id).to_dict()

    # First initialization
    if req_id not in highlight_desc_from_req_id:
        highlight_desc_from_req_id[req_id] = {}

        all_vars = VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        ).get_available_var_names_list(used_only=False)

        matches = _highlight_desc_variable(req["desc"], all_vars)
        highlight_desc_from_req_id[req_id]["variable_matches"] = matches
        highlight_desc_from_req_id[req_id]["highlighted_desc"] = generate_html_description(
            matches,
            req["desc"],
        )

    # Update existing
    else:
        if variables:
            new_matches = _highlight_desc_variable(req["desc"], variables)

            if new_matches:
                highlight_desc_from_req_id[req_id]["variable_matches"].extend(new_matches)
                highlight_desc_from_req_id[req_id]["highlighted_desc"] = generate_html_description(
                    highlight_desc_from_req_id[req_id]["variable_matches"],
                    req["desc"],
                )

    return highlight_desc_from_req_id[req_id]["highlighted_desc"]


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


def _highlight_desc_variable(
    desc: str, variables: list[str], threshold: int = 70, max_gap: int = 1, min_coverage: float = 0.55
) -> list[tuple[int, int, str, str, float]]:
    """Find positions of variable matches in a description using fuzzy matching and camelCase splitting.

    :param desc: Description text to search in
    :param variables: List of variable names to highlight
    :param threshold: Minimum fuzzy match score for a word to be considered
    :param max_gap: Maximum number of words allowed between parts of a variable
    :param min_coverage: Minimum fraction of variable words that must be matched
    :return: List of tuples: (start_index, end_index, matched_text, variable_name, score)
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
    return final_matches


def generate_html_description(final_matches: list[tuple[int, int, str, str, float]], desc) -> str:
    """Generate HTML-highlighted description from matched intervals.

    This function sorts matches by score and length, resolves overlaps, and applies
    highlighting using a template.

    :param final_matches: List of tuples from `_highlight_desc_variable`
    :param desc: Original description text
    :return: HTML string with highlighted variables
    """

    # Sort intervals by score (desc), length (desc), start position (asc)
    final_matches.sort(key=lambda x: (-x[4], -(x[1] - x[0]), x[0]))
    kept_intervals = []

    # Combine similar variables if intervals are exactly the same
    for start, end, matched_text, var, score in final_matches:
        overlapping = []
        for i, (s2, e2, _) in enumerate(kept_intervals):
            if start < e2 and end > s2:
                overlapping.append((i, s2, e2))

        if not overlapping:
            kept_intervals.append((start, end, [(var, score)]))
        else:
            merged = False
            for i, s2, e2 in overlapping:
                if start == s2 and end == e2:
                    kept_intervals[i][2].append((var, score))
                    merged = True
                    break
            if merged:
                continue

            # Partial overlap -> keep only the best (score, length)
            for i, s2, e2 in overlapping:
                main_vars = kept_intervals[i][2]
                main_score = main_vars[0][1]
                main_len = e2 - s2
                curr_len = end - start
                if score > main_score or (score == main_score and curr_len > main_len):
                    kept_intervals[i] = (start, end, [(var, score)])

    # Build output
    out, last = [], 0
    for s, e, vars_info in sorted(kept_intervals):
        out.append(desc[last:s])
        vars_info.sort(key=lambda x: -x[1])
        main_var, main_score = vars_info[0]
        extra_vars = vars_info[1:]

        out.append(
            highlight_tpl.render(text=desc[s:e], main_var=main_var, main_score=main_score, extra_vars=extra_vars)
        )
        last = e

    out.append(desc[last:])
    html_result = "".join(out)
    return html_result
