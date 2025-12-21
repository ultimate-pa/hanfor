import logging
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional, Any
from jinja2 import Environment, FileSystemLoader
from rapidfuzz import process, fuzz
from lib_core.data import Variable
from bisect import bisect_left
from immutabledict import immutabledict

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
highlight_tpl = env.get_template("highlight.html")


@dataclass(slots=True)
class VariableMatch:
    start: int
    end: int
    text: str
    variable: str
    score: float


@dataclass(slots=True)
class FragmentMatch:
    score: float
    positions: list[tuple[int, int]]


@dataclass(slots=True)
class RequirementHighlightingData:
    req_id: str
    description: str

    highlighted_desc: str = ""
    variable_matches: list[VariableMatch] = field(default_factory=list)
    variable_fragments_fuzz_matches: dict[str, list[tuple[str, float, int]]] = field(default_factory=dict)

    desc_words_positions: dict[str, list[tuple[int, int]]] = field(default_factory=dict)
    desc_words: list[str] = field(default_factory=list)
    desc_words_starting_pos: list[int] = field(default_factory=list)


requirement_highlighting_data_per_req: dict[str, RequirementHighlightingData] = {}
variable_sets = defaultdict(set)


def get_highlighted_desc(req_id: str) -> str:
    return requirement_highlighting_data_per_req[req_id].highlighted_desc


def delete_variables(variables: list[str]) -> None:
    """
    If a variable is deleted, it is removed from the variable lookup sets and from all
    matches within the requirements. Afterward, a new highlighted string is generated.
    """
    logging.info(f"Updating highlighting after deleting variables: {variables}")
    for variable in variables:
        if variable in variable_sets[variable]:
            variable_sets.pop(variable)
    for req_data in requirement_highlighting_data_per_req.values():
        for match in req_data.variable_matches:
            if match.variable in variables:
                req_data.variable_matches.remove(match)
        req_data.highlighted_desc = _generate_md_description(
            req_data.variable_matches,
            req_data.description,
        )


def changing_variables(variable_name_old: str, variable_name_new: str) -> None:
    """
    If a variable name is changed, the old name is removed from all descriptions,
    and all descriptions are reprocessed with the new name.
    """
    logging.info(f"Changing variable '{variable_name_old}' to '{variable_name_new}'")
    delete_variables([variable_name_old])
    generate_all_highlighted_desc([variable_name_new], None)


def new_variables_regenerate_highlighting(variables: set[Variable]) -> None:
    """
    Process a set of updated variable objects and trigger regeneration of highlighted
    descriptions for all requirements.
    """
    variable_list = [v.name for v in variables]
    logging.info(f"Regenerating highlighting for new variables: {variable_list}")
    if variable_list:
        generate_all_highlighted_desc(variable_list, None)


def generate_all_highlighted_desc(
    new_variables: List[str], requirements: Optional[immutabledict[int | str, Any]]
) -> None:
    """
    Regenerates highlighted descriptions for all requirements.
    only the new_variables will be reprocessed inside each requirement.
    """
    logging.info("Generating highlighted descriptions for requirements...")
    # Normalize variables and build lookup list
    variable_sets_list = []
    for var in new_variables:
        if var:
            if var not in variable_sets:
                norm = _normalize_variable(var)
                if not norm:
                    continue
                variable_sets[var] = norm
            variable_sets_list.append((var, variable_sets[var]))

    # Initialize entries for each requirement
    if requirements:
        logging.info("Initialize each requirement...")
        for req_id, requirement in requirements.items():
            word_positions = _normalize_and_group_positions_from_desc(requirement.description)

            requirement_highlighting_data_per_req[req_id] = RequirementHighlightingData(
                req_id=req_id,
                description=requirement.description,
                desc_words_positions=word_positions,
                desc_words=list(word_positions.keys()),
                desc_words_starting_pos=sorted(pos[0] for positions in word_positions.values() for pos in positions),
            )

    all_req_data = list(requirement_highlighting_data_per_req.values())
    total = len(all_req_data)
    step = max(total // 5, 1)

    # (Re)compute variable matches and generate HTML
    for idx, req_data in enumerate(all_req_data, start=1):
        new_matches = _highlight_desc_variable(
            req_data,
            variable_sets_list,
        )

        req_data.variable_matches.extend(new_matches)
        req_data.highlighted_desc = _generate_md_description(
            req_data.variable_matches,
            req_data.description,
        )

        if idx % step == 0 or idx == total:
            percent = int(idx / total * 100)
            logging.info(f"Processed {idx}/{total} requirements ({percent}%)")


def _normalize_variable(var: str) -> set[str]:
    """
    Normalize a variable name by splitting camelCase, preserving number+letter tokens
    (e.g. "300M"), removing separators, and returning a lowercase set of words.
    """
    var = var.replace("_", " ").replace("-", " ")

    def camel_case_split(match) -> str:
        word = match.group()
        if re.fullmatch(r"\d+[A-Za-z]{1,2}", word):
            return word
        return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", word)

    var = re.sub(r"\b\w+\b", camel_case_split, var)
    var = re.sub(r"\s+", " ", var)
    return {token for token in var.lower().strip().split() if len(token) > 2}


def _normalize_and_group_positions_from_desc(desc: str) -> dict[str, list[tuple[int, int]]]:
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
            if len(sub_word) > 2:
                word_positions[sub_word].append((start + s, start + e))
    return word_positions


def _words_between(pos1: int, pos2: int, all_word_starts: list[int], max_gap: int):
    i1 = bisect_left(all_word_starts, pos1)
    i2 = bisect_left(all_word_starts, pos2)
    return (i2 - i1) <= max_gap


def _generate_combinations(
    pos_score_dict: dict[str, list[tuple[tuple[int, int], float]]],
    var_fragments: set[str],
    max_gap: int,
    threshold: float,
    min_coverage: float,
    all_word_starts: list[int],
):
    """
    Generate all ascending combinations of variable word positions with scores.
    Applies a missing-word penalty and filters combinations by a minimum score threshold.
    """
    combos = []
    # all_word_hits_sorted -> [(position_in_desc, variable_fragment, score)]
    all_word_hits_sorted: list[tuple[tuple[int, int], float, str]] = []
    for variable_fragment, list_pos_score in pos_score_dict.items():
        for position_in_desc, score in list_pos_score:
            all_word_hits_sorted.append((position_in_desc, score, variable_fragment))
    # Sort by start, end, then score desc
    all_word_hits_sorted.sort(key=lambda x: (x[0][0], x[0][1], -x[1]))

    min_count_words = len(var_fragments) * min_coverage

    # Build linear combo starting at index i
    for i in range(len(all_word_hits_sorted)):
        combo = []
        fragments_used = set()

        for position_in_desc, score, variable_fragment in all_word_hits_sorted[i:]:
            if len(combo) > 0:
                if position_in_desc[0] == combo[-1][0][0]:
                    continue
                if not _words_between(combo[-1][0][0], position_in_desc[0], all_word_starts, max_gap):
                    break
            if variable_fragment not in fragments_used:
                fragments_used.add(variable_fragment)
            combo.append((position_in_desc, score))

        # punishment for missing words and evaluate if usefull combo
        missing = var_fragments - fragments_used
        punishment = len(missing) * (-20)
        avg_score = sum(p[1] for p in combo) / len(combo)
        final_score = avg_score + punishment

        if len(combo) < min_count_words:
            continue
        if final_score < threshold:
            continue

        positions = [pos for (pos, score) in combo]
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
    req_data: RequirementHighlightingData,
    variable_fragments_list: list[tuple[str, set]],
    threshold: int = 70,
    max_gap: int = 1,
    min_coverage: float = 0.55,
) -> list[VariableMatch]:
    """Find positions of variable matches in a description using fuzzy matching and camelCase splitting."""

    final_matches = []

    # Cashing fuzzy output for equal fragments to minimize work
    all_fragments = {fragment for _, variable_fragments in variable_fragments_list for fragment in variable_fragments}
    for variable_fragment in all_fragments:
        req_data.variable_fragments_fuzz_matches[variable_fragment] = list(
            process.extract_iter(
                query=variable_fragment, choices=req_data.desc_words, scorer=fuzz.ratio, score_cutoff=80
            )
        )

    # get all positions
    for var, variable_fragments in variable_fragments_list:
        scored_matches: dict[str, list[FragmentMatch]] = {}
        for fragment in variable_fragments:
            matches = req_data.variable_fragments_fuzz_matches.get(fragment, [])
            scored_matches[fragment] = [
                FragmentMatch(
                    score=score,
                    positions=req_data.desc_words_positions[word_desc],
                )
                for word_desc, score, _ in matches
            ]

        # Skip variable_sets with insufficient coverage
        if not scored_matches or len(scored_matches) / len(variable_fragments) < min_coverage:
            continue

        # Build a global mapping: span -> best score
        span_to_best: dict[tuple[int, int], float] = defaultdict(float)
        for matches in scored_matches.values():
            for match in matches:
                for span in match.positions:
                    span_to_best[span] = max(span_to_best[span], match.score)

        # Build position-score dictionary per fragment, keeping only the best score for each span
        pos_score_dict: dict[str, list[tuple[tuple[int, int], float]]] = {}

        for fragment, matches in scored_matches.items():
            best_positions = [
                (span, match.score)
                for match in matches
                for span in match.positions
                if span_to_best[span] == match.score
            ]

            if best_positions:
                pos_score_dict[fragment] = best_positions

        # Generate all ascending combinations and filter them
        combos = _generate_combinations(
            pos_score_dict, variable_fragments, max_gap, threshold, min_coverage, req_data.desc_words_starting_pos
        )
        selected = _filter_combos(combos)

        # Add matches for this variable
        for score, start, end, _ in selected:
            matched_text = req_data.description[start:end]
            final_matches.append(
                VariableMatch(
                    start=start,
                    end=end,
                    text=matched_text,
                    variable=var,
                    score=score,
                )
            )

    return final_matches


def _generate_md_description(final_matches: list[VariableMatch], desc) -> str:
    """
    Generate Markdown-compatible description with embedded HTML for variable highlighting.
    """

    # Sort intervals by score (desc), length (desc), start position (asc)
    final_matches.sort(key=lambda x: (-x.score, -(x.end - x.start), x.start))

    kept_intervals = []

    # Combine similar variable_sets if intervals are exactly the same
    for match in final_matches:
        start = match.start
        end = match.end
        var = match.variable
        score = match.score

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
                if score > main_score or (score == main_score and (end - start) > main_len):
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
    return "".join(out)
