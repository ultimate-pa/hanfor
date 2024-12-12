import functools
import logging
from dataclasses import dataclass
from enum import Enum

from pysmt.fnode import FNode
from pysmt.shortcuts import FALSE, Or, Not, Solver, TRUE, get_free_variables, And, Bool, simplify, Exists
from pysmt.walkers import IdentityDagWalker

import boogie_parsing
from reqtransformer import Requirement, Variable, Scope
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer

SOLVER_NAME = "z3"
LOGIC = "UFLIRA"


class CompletenessCheckOutcome(Enum):
    INCOMPLETE = "INCOMPLETE"
    ENV_VIOLATED = "ENV_VIOLATED"
    OK = "OK"


@dataclass
class CompletenessCheckResult:
    var: Variable
    outcome: CompletenessCheckOutcome
    message: str

    def __str__(self):
        return f"{self.outcome}: in var '{self.var.name}': {self.message}"


class PoorMansComplete:

    def run(self, reqs: list[Requirement], variables: set[Variable]) -> list[CompletenessCheckResult]:
        logging.info("Starting PoorMansComplete Analysis for requirements set...")
        results = []
        smt_transformer = BoogiePysmtTransformer(variables)
        smt_to_vars = {
            smt_transformer.smt_vars[hanfor_var.name]: hanfor_var
            for hanfor_var in variables
            if hanfor_var.name in smt_transformer.smt_vars
        }
        env_assumptions = self.extract_environment_assumption(variables, smt_transformer)
        for target_var, hanfor_var in smt_to_vars.items():
            term = self.extract_reqs_term(smt_transformer, reqs, target_var)
            term = FalseTermAbsorber().walk(term)
            results.append(self.check_env_violated(term, target_var, env_assumptions, hanfor_var))
            results.append(self.check_complete_var(term, target_var, env_assumptions, hanfor_var))
        logging.info("... finished PoorMansComplete.")
        return results

    def check_env_violated(
        self, term: FNode, target_var: FNode, env_assumption: FNode, hanfor_var: Variable
    ) -> CompletenessCheckResult:
        if target_var not in get_free_variables(env_assumption):
            return CompletenessCheckResult(
                hanfor_var, CompletenessCheckOutcome.OK, f"'{target_var.symbol_name()}' has no env assumptions."
            )
        with Solver(name=SOLVER_NAME, logic=LOGIC) as solver:
            if target_var in get_free_variables(env_assumption):
                a_form = And(term, Not(env_assumption))
                free = [v for v in get_free_variables(a_form) if v != target_var]
                outside_environment = solver.is_sat(Exists(free, a_form))
                if outside_environment:
                    return CompletenessCheckResult(
                        hanfor_var,
                        CompletenessCheckOutcome.ENV_VIOLATED,
                        f"'{target_var.symbol_name()}': value {solver.get_value(target_var)} is outside of Environment.\n"
                        f"Term is: {term}\n"
                        f"Environment is: {env_assumption}\n",
                    )
        return CompletenessCheckResult(hanfor_var, CompletenessCheckOutcome.OK, "")

    def check_complete_var(
        self, term: FNode, target_var: FNode, env_assumption: FNode, hanfor_var: Variable
    ) -> CompletenessCheckResult:
        if target_var not in get_free_variables(term):
            return CompletenessCheckResult(
                hanfor_var, CompletenessCheckOutcome.OK, f"'{target_var.symbol_name()}' is unused."
            )
        with Solver(name=SOLVER_NAME, logic=LOGIC) as solver:
            q_form = And(Not(term), env_assumption)
            free = [v for v in get_free_variables(q_form) if v != target_var]
            is_incomplete = solver.is_sat(Exists(free, q_form))
            if is_incomplete:
                return CompletenessCheckResult(
                    hanfor_var,
                    CompletenessCheckOutcome.INCOMPLETE,
                    f"{target_var.symbol_name()}: value {solver.get_value(target_var)}  is uncovered.\n"
                    f"Term is: {term}\n"
                    f"Environment is: {env_assumption}\n",
                )
        # return f"{target_var} is complete: {not is_incomplete}"
        return CompletenessCheckResult(hanfor_var, CompletenessCheckOutcome.OK, "")

    def extract_reqs_term(
        self,
        smt_transformer: BoogiePysmtTransformer,
        reqs: list[Requirement],
        target_var: FNode,
    ) -> FNode:
        term = FALSE()
        for req in reqs:
            req_term = self.extract_req_term(smt_transformer, req, target_var)
            if req_term is FALSE() or req_term is TRUE():
                continue
            term = Or(term, req_term)
        return term

    def extract_req_term(self, smt_transformer: BoogiePysmtTransformer, req: Requirement, target_var: FNode) -> FNode:
        parser = boogie_parsing.get_parser_instance()
        term = FALSE()
        for _, formalisation in req.formalizations.items():
            expression_types = formalisation.scoped_pattern.get_allowed_types()
            for ident, expression in formalisation.expressions_mapping.items():
                if not expression or not expression.raw_expression:
                    # filter out empty expressions
                    continue
                if ident in expression_types and boogie_parsing.BoogieType.real in expression_types[ident]:
                    # filter out all expressions that are non-boolean (currently only clock constraints)
                    continue
                try:
                    # TODO move parsing and  subsequent caching into the expressions
                    ast = parser.parse(expression.raw_expression)
                    smt_expr = smt_transformer.transform(ast)
                except Exception as e:
                    logging.error(
                        f"Parsing error in requirement: {req.rid} expression `{expression.raw_expression}`.\n {e}"
                    )
                    continue
                if target_var not in get_free_variables(smt_expr):
                    continue
                term = Or(term, smt_expr)
        term = ProjectionWalker(target_var).walk(term)
        return term

    def extract_environment_assumption(self, variables: set[Variable], smt_transformer: BoogiePysmtTransformer):
        term = TRUE()
        parser = boogie_parsing.get_parser_instance()
        for var in variables:
            for k, f in var.constraints.items():
                expression_types = f.scoped_pattern.get_allowed_types()
                for ident, expression in f.expressions_mapping.items():
                    if not expression or not expression.raw_expression:
                        # filter out empty expressions
                        continue
                    if ident in expression_types and boogie_parsing.BoogieType.real in expression_types[ident]:
                        # filter out all expressions that are non-boolean (currently only clock constraints)
                        continue
                    try:
                        ast = parser.parse(expression.raw_expression)
                        smt_expr = smt_transformer.transform(ast)
                    except Exception as e:
                        logging.error(
                            f"Parsing error in constraint: {var.name} expression {expression.raw_expression}.\n {e}"
                        )
                        continue
                    # TODO puh, unsure on how to handle non invariant pattern at this point
                    if f.scoped_pattern.scope != Scope.GLOBALLY:
                        logging.warning(
                            f"Variable {var.name} constraint {k} is not an Absence or Universality pattern... skipping."
                        )
                        continue
                    match f.scoped_pattern.pattern.name:
                        case "Universality":
                            term = And(term, smt_expr)
                        case "Absence":
                            term = And(term, Not(smt_expr))
        return simplify(term)


class ProjectionWalker(IdentityDagWalker):
    def __init__(self, variable):
        super().__init__()
        self.variable = variable

    def walk_and(self, formula, args, **kwargs):
        relevant_args = [f for f in args if self.variable in get_free_variables(f)]
        return And(relevant_args) if relevant_args else Bool(True)

    def walk_or(self, formula, args, **kwargs):
        relevant_args = [f for f in args if self.variable in get_free_variables(f)]
        return Or(relevant_args) if relevant_args else Bool(True)

    def walk_not(self, formula, args, **kwargs):
        arg = args[0]
        if self.variable in get_free_variables(arg):
            return Not(arg)
        return Bool(True)

    def walk_atom(self, formula, **kwargs):
        if self.variable in get_free_variables(formula):
            return formula
        return Bool(True)


class FalseTermAbsorber(IdentityDagWalker):

    def walk_or(self, formula, args, **kwargs):
        # Simplify `false | x` to `x` and eliminate `false`
        non_false_args = [arg for arg in args if not arg.is_false()]
        if not non_false_args:
            return FALSE()
        elif len(non_false_args) == 1:
            return non_false_args[0]
        return Or(non_false_args)
