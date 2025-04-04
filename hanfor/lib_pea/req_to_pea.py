from typing import List

import lib_core.boogie_parsing
from lib_core import boogie_parsing
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.pea import PhaseSetsPea
from lib_pea.utils import get_countertrace_parser
from configuration.patterns import PATTERNS

# TODO: re-add after formalisation has been factored out of reqtransformer
# from reqtransformer import Formalization, VariableCollection


def has_variable_with_unknown_type(formalization: "Formalization", variables: dict[str, str]) -> bool:
    for used_variable in formalization.used_variables:
        if variables[used_variable] == "unknown" or variables[used_variable] == "error":
            return True

    return False


def get_pea_from_formalisation(
    req_id: str, formalization: "Formalization", var_collection: "VariableCollection"
) -> List[PhaseSetsPea]:
    if not formalization.scoped_pattern.is_instantiatable():
        return []
    variables = {k: v.type for k, v in var_collection.collection.items()}
    if has_variable_with_unknown_type(formalization, variables) or formalization.type_inference_errors:
        return []

    boogie_parser = boogie_parsing.get_parser_instance()
    scope = formalization.scoped_pattern.scope.name
    pattern = formalization.scoped_pattern.pattern.name

    if len(PATTERNS[pattern]["countertraces"][scope]) <= 0:
        raise ValueError(f"No countertrace given: {scope}, {pattern}")

    expressions = {}
    for k, v in formalization.expressions_mapping.items():
        # Todo: hack to detect empty expressions (why is this necessary now)?
        if not v.raw_expression:
            continue
        tree = boogie_parser.parse(v.raw_expression)
        expressions[k] = BoogiePysmtTransformer(var_collection.collection.values()).transform(tree)

    peas = []
    for i, ct_str in enumerate(PATTERNS[pattern]["countertraces"][scope]):
        ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
        peas.append(build_automaton(ct, f"c_{req_id}_{formalization.id}_{i}_"))
    return peas
