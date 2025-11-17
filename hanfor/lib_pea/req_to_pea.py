from lib_core import boogie_parsing
from lib_core.data import Formalization, VariableCollection, Requirement
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import Countertrace
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.pea import PhaseSetsPea
from configuration.patterns import APattern


def get_semantics_from_requirement(
    requirement: Requirement, requirements: list[Requirement], var_collection: VariableCollection
) -> dict[str, Countertrace]:
    """Instanciate the semantics of a single requirement.
    All other requirements should be passed in to allow for complexer patterns to be generated"""
    dc_formulas = dict()
    variables = {k: v.type for k, v in var_collection.collection.items()}
    boogie_parser = boogie_parsing.get_parser_instance()
    for formalization in requirement.formalizations.values():
        if not formalization.scoped_pattern.is_instantiatable():
            continue
        if has_variable_with_unknown_type(formalization, variables) or formalization.type_inference_errors:
            continue

        scope = formalization.scoped_pattern.scope.name
        pattern = formalization.scoped_pattern.pattern.name

        expressions = {}
        for k, v in formalization.expressions_mapping.items():
            # Todo: hack to detect empty expressions (why is this necessary now)?
            if not v.raw_expression:
                continue
            tree = boogie_parser.parse(v.raw_expression)
            expressions[k] = BoogiePysmtTransformer(set(var_collection.collection.values())).transform(tree)

        for i, ct in enumerate(
            APattern.get_pattern(pattern).get_instanciated_countertraces(scope, expressions, requirements)
        ):
            dc_formulas[(requirement, formalization, i)] = ct

    return dc_formulas


def get_pea_from_formalisation(countertraces: dict[str, Countertrace]) -> list[PhaseSetsPea]:
    peas = []
    for fid, ct in countertraces.items():
        sfid = f"c_{fid[0].rid}_{fid[1].id}_{fid[2]}_"
        peas.append(build_automaton(ct, sfid))
    return peas


def has_variable_with_unknown_type(formalization: Formalization, variables: dict[str, str]) -> bool:
    for used_variable in formalization.used_variables:
        if not variables[used_variable] or variables[used_variable] == "unknown" or variables[used_variable] == "error":
            return True

    return False
