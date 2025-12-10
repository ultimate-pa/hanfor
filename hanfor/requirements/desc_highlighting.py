import os
import re
from collections import defaultdict
from typing import List, Optional, Any
from jinja2 import Environment, FileSystemLoader
from rapidfuzz import process, fuzz
from itertools import combinations, product
from lib_core.data import Variable
from bisect import bisect_left
from immutabledict import immutabledict

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
highlight_tpl = env.get_template("highlight.html")

highlight_desc_from_req_id = defaultdict(dict)
variable_sets = defaultdict(set)


def get_highlighted_desc(req_id: str) -> dict[str, dict]:
    return highlight_desc_from_req_id[req_id]["highlighted_desc"]


def updated_variables(variables: set[Variable]) -> None:
    """
    Process a set of updated variable objects and trigger regeneration of highlighted
    descriptions for all requirements.
    """
    variable_list = [v.name for v in variables]
    if variable_list:
        generate_all_highlighted_desc(variable_list, None)


def generate_all_highlighted_desc(
    new_variables: List[str], requirements: Optional[immutabledict[int | str, Any]]
) -> None:
    """
    Regenerates highlighted descriptions for all requirements.
    only the new_variables will be reprocessed inside each requirement.
    """
    # Normalize variables and build lookup list
    variable_sets_list = []
    for var in new_variables:
        if var:
            if var not in variable_sets:
                variable_sets[var] = _normalize_variable(var)
            variable_sets_list.append((var, variable_sets[var]))

    # Initialize entries for each requirement
    if requirements:
        for req_id, requirement in requirements.items():
            req_entry = highlight_desc_from_req_id[req_id]

            req_entry["description"] = requirement.description
            req_entry["variable_matches"] = []
            req_entry["highlighted_desc"] = ""

            word_positions = _normalize_and_group_positions_from_desc(requirement.description)
            req_entry["word_positions"] = word_positions
            req_entry["desc_words"] = list(word_positions.keys())
            req_entry["all_word_starts"] = sorted(pos[0] for positions in word_positions.values() for pos in positions)

    # (Re)compute variable matches and generate HTML
    for req_id, req_entry in highlight_desc_from_req_id.items():
        # Compute new variable matches
        new_matches = _highlight_desc_variable(
            req_entry["description"],
            variable_sets_list,
            req_entry["word_positions"],
            req_entry["desc_words"],
            req_entry["all_word_starts"],
        )

        req_entry["variable_matches"].extend(new_matches)
        req_entry["highlighted_desc"] = _generate_html_description(
            req_entry["variable_matches"],
            req_entry["description"],
        )


def _normalize_variable(var: str) -> set[str]:
    """
    Normalize a variable name by splitting camelCase, preserving number+letter tokens
    (e.g. "300M"), removing separators, and returning a lowercase set of words.
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


def _words_between(pos1, pos2, all_word_starts, max_gap):
    i1 = bisect_left(all_word_starts, pos1[0])
    i2 = bisect_left(all_word_starts, pos2[0])
    return (i2 - i1) <= max_gap


def _generate_combinations(
    pos_score_dict: dict[str, list[tuple[tuple[int, int], float]]],
    var_fragments: set[str],
    max_gap: int,
    threshold: float,
    all_word_starts: list[int],
):
    """
    Generate all ascending combinations of variable word positions with scores.
    Applies a missing-word penalty and filters combinations by a minimum score threshold.
    """
    # Flatten all hits and sort by start position
    all_hits = []
    for f, lst in pos_score_dict.items():
        for span, score in lst:
            all_hits.append((f, span, score, span[0]))
    all_hits.sort(key=lambda x: x[3])

    combos = []
    n = len(all_hits)

    # Create sliding windows over sorted hits
    for i in range(n):
        base_f, base_span, base_score, base_pos = all_hits[i]
        for j in range(i, n):
            f2, span2, score2, pos2 = all_hits[j]

            # Stop if the window exceeds the max_gap
            if not _words_between(base_span, span2, all_word_starts, max_gap):
                break

            window = all_hits[i : j + 1]

            # Group hits by fragment within the window
            grouped = {}
            for f, span, score, pos in window:
                grouped.setdefault(f, []).append((span, score))
            fragments_present = list(grouped.keys())

            # Prepare choices per fragment
            choices_per_fragment = [[(f, span, score) for (span, score) in grouped[f]] for f in fragments_present]

            # Generate all combinations of 1...N fragments
            for r in range(1, len(choices_per_fragment) + 1):
                for fragment_indices in combinations(range(len(choices_per_fragment)), r):
                    selected_lists = [choices_per_fragment[idx] for idx in fragment_indices]
                    for product_choice in product(*selected_lists):

                        # Calculate score with penalty for missing fragments
                        used_fragments = {p[0] for p in product_choice}
                        missing = var_fragments - used_fragments
                        punishment = len(missing) * (-20)
                        avg_score = sum(p[2] for p in product_choice) / len(product_choice)
                        final_score = avg_score + punishment

                        # Keep combination if above threshold
                        if final_score >= threshold:
                            positions = [span for (frag, span, score) in product_choice]
                            combos.append((final_score, positions))

    return combos


def _filter_combos(
    combos: list[tuple[float, list[tuple[int, int]]]]
) -> list[tuple[float, int, int, list[tuple[int, int]]]]:
    """Filter combinations remove overlapping lower-score segments,
    and select final segments with start and end positions.
    """
    gap_filtered = []
    for score, positions in combos:
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
    desc: str,
    variable_fragments_list: list[tuple[str, set]],
    word_positions: dict[str, list[tuple]],
    desc_words: list[str],
    all_word_starts: list[int],
    threshold: int = 70,
    max_gap: int = 1,
    min_coverage: float = 0.55,
) -> list[tuple[int, int, str, str, float]]:
    """Find positions of variable matches in a description using fuzzy matching and camelCase splitting."""
    final_matches = []

    for var, variable_fragments in variable_fragments_list:
        # Fuzzy match all pieces of the variable
        sored_matches = {}
        for fragment in variable_fragments:
            matches = list(process.extract_iter(query=fragment, choices=desc_words, scorer=fuzz.ratio, score_cutoff=80))
            if matches:
                sored_matches[fragment] = [
                    {"score": score, "pos": word_positions[word_desc]} for word_desc, score, _ in matches
                ]

        # Skip variable_sets with insufficient coverage
        if not sored_matches or len(sored_matches) / len(variable_fragments) < min_coverage:
            continue

        # Build a global mapping: span -> best score
        span_to_best = defaultdict(int)
        for lst in sored_matches.values():
            for e in lst:
                for p in e["pos"]:
                    span_to_best[p] = max(span_to_best[p], e["score"])

        # Build position-score dictionary per fragment, keeping only the best score for each span
        pos_score_dict = {}
        for fragment, lst in sored_matches.items():
            filtered = []
            for e in lst:
                for p in e["pos"]:
                    if span_to_best[p] == e["score"]:  # keep only the highest score
                        filtered.append((p, e["score"]))
            if filtered:
                pos_score_dict[fragment] = filtered

        # Generate all ascending combinations and filter them
        combos = _generate_combinations(pos_score_dict, variable_fragments, max_gap, threshold, all_word_starts)
        selected = _filter_combos(combos)

        # Add matches for this variable
        for score, start, end, _ in selected:
            matched_text = desc[start:end]
            final_matches.append((start, end, matched_text, var, score))
    return final_matches


def _generate_html_description(final_matches: list[tuple[int, int, str, str, float]], desc) -> str:
    """
    Generate HTML-highlighted description from matched intervals.
    This function sorts matches by score and length, resolves overlaps, and applies
    highlighting using a template.
    """

    # Sort intervals by score (desc), length (desc), start position (asc)
    final_matches.sort(key=lambda x: (-x[4], -(x[1] - x[0]), x[0]))
    kept_intervals = []

    # Combine similar variable_sets if intervals are exactly the same
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
