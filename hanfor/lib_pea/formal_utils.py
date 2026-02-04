from typing import TYPE_CHECKING

from pysmt.fnode import FNode

from lib_core import boogie_parsing
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import Countertrace

if TYPE_CHECKING:
    from lib_core.data import Requirement, VariableCollection, Formalization


def get_expression_mapping_smt(f: "Formalization", vc: "VariableCollection") -> dict[str, FNode]:
    expressions = {}

    for k, v in f.expressions_mapping.items():
        # Todo: hack to detect empty expressions (why is this necessary now)?
        if not v.raw_expression:
            continue
        expressions[k] = get_smt_expression(f, vc, k)

    return expressions


def get_smt_expression(f: "Formalization", vc: "VariableCollection", letter: str) -> FNode:
    boogie_parser = boogie_parsing.get_parser_instance()
    tree = boogie_parser.parse(f.expressions_mapping[letter].raw_expression)
    return BoogiePysmtTransformer(set(vc.collection.values())).transform(tree)


def get_semantics_from_requirement(
    requirement: "Requirement", requirements: list["Requirement"], var_collection: "VariableCollection"
) -> dict[tuple["Formalization", int], Countertrace]:
    """Instanciate the semantics of a single requirement.
    All other requirements should be passed in to allow for complexer patterns to be generated"""
    dc_formulas = dict()
    variables = {k: v.type for k, v in var_collection.collection.items()}
    for formalization in requirement.formalizations.values():
        if not formalization.scoped_pattern.is_instantiatable():
            continue
        if has_variable_with_unknown_type(formalization, variables) or formalization.type_inference_errors:
            continue

        scope = formalization.scoped_pattern.scope.name
        pattern = formalization.scoped_pattern.pattern.get_patternish()

        other_formalisations = [f for r in requirements for f in r.formalizations.values() if f is not formalization]
        for i, ct in enumerate(
            pattern.get_instanciated_countertraces(scope, formalization, other_formalisations, var_collection)
        ):
            dc_formulas[(formalization, i)] = ct

    return dc_formulas


def has_variable_with_unknown_type(formalization: "Formalization", variables: dict[str, str]) -> bool:
    for used_variable in formalization.used_variables:
        if not variables[used_variable] or variables[used_variable] == "unknown" or variables[used_variable] == "error":
            return True

    return False
