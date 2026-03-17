import logging
from dataclasses import dataclass
from typing import List

from pysmt.fnode import FNode
from pysmt.shortcuts import FALSE, Or, Not, Solver, TRUE, get_free_variables, And, Bool, simplify
from pysmt.walkers import IdentityDagWalker

from json_db_connector.json_db import DatabaseField, DatabaseFieldType
from lib_core import boogie_parsing
from lib_core.data import Requirement, Variable
from lib_core.scopes import Scope
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer

SOLVER_NAME = "z3"
LOGIC = "UFLIRA"


class CompletenessCheckOutcome:
    INCOMPLETE = "INCOMPLETE"
    ENV_VIOLATED = "ENV_VIOLATED"
    INCOMPLETE_UNCONSTRAINT = "INCOMPLETE_UNCONSTRAINT"
    OK = "OK"

    @staticmethod
    def is_negative_result(value: "CompletenessCheckOutcome") -> bool:
        return value in {CompletenessCheckOutcome.INCOMPLETE, CompletenessCheckOutcome.ENV_VIOLATED}


@dataclass
@DatabaseFieldType()
@DatabaseField("var", str)
@DatabaseField("outcome", str)
@DatabaseField("message", str)
class CompletenessCheckResult:
    var: str
    outcome: str
    message: str

    def __str__(self):
        return f"{self.outcome}: in var '{self.var}': {self.message}"


class PoorMansComplete:
    """
    Performs some quick and dirty checks on the requirements: For any variable v in the requirements
    1. is any value of (that is allowed by the constraints of v) mentioned in some observable?
    2. is any value of v mentioned in an observable also allowed by the constraints?
    Note: the check uses all observables mentioned in requirements as they are (except for the universality not pattern)
    thus, there may be no negative formulations in patterns, or this will get unsound.
    """

    CHECK_ID = "poormans_complete"

    def run(self, reqs: list[Requirement], variables: set[Variable]) -> list[CompletenessCheckResult]:
        logging.info("Starting PoorMansComplete Analysis for requirements set...")
        results = []
        smt_transformer = BoogiePysmtTransformer(variables)
        smt_to_vars = {
            smt_transformer.smt_vars[hanfor_var.name]: hanfor_var
            for hanfor_var in variables
            if hanfor_var.name in smt_transformer.smt_vars
        }
        env_full = self.extract_environment_assumption(variables, smt_transformer)
        for target_var, hanfor_var in smt_to_vars.items():
            env_assumptions = simplify(And([t for t in env_full if target_var in get_free_variables(t)]))
            # env_full  # ProjectionWalker(target_var).walk(env_full)
            terms = self.extract_reqs_term(smt_transformer, reqs, target_var)
            results.append(self.check_env_violated(terms, target_var, env_assumptions, hanfor_var))
            results.append(self.check_complete_var(Or(terms), target_var, env_assumptions, hanfor_var))
        logging.info("... finished PoorMansComplete.")
        return results

    @staticmethod
    def check_complete_var(
        term: FNode, target_var: FNode, env_assumption: FNode, hanfor_var: Variable
    ) -> CompletenessCheckResult:
        """Check if all values (under an environment) of a variable are possible in term"""
        with Solver(name=SOLVER_NAME, logic=LOGIC) as solver:
            q_form = And(Not(term), env_assumption)
            is_incomplete = solver.is_sat(q_form)
            if is_incomplete:
                return CompletenessCheckResult(
                    hanfor_var.name,
                    (
                        CompletenessCheckOutcome.INCOMPLETE
                        if target_var in get_free_variables(env_assumption)
                        else CompletenessCheckOutcome.INCOMPLETE_UNCONSTRAINT
                    ),
                    f"{target_var.symbol_name()}: value {solver.get_value(target_var)}  is uncovered.\n"
                    f"Term is: {term.serialize()}\n"
                    f"Environment is: {env_assumption.serialize()}\n",
                )
        # return f"{target_var} is complete: {not is_incomplete}"
        return CompletenessCheckResult(
            hanfor_var.name, CompletenessCheckOutcome.OK, "Any value of the variable is covered by a req"
        )

    def extract_reqs_term(
        self,
        smt_transformer: BoogiePysmtTransformer,
        reqs: list[Requirement],
        target_var: FNode,
        use_projection: bool = True,
    ) -> List[FNode]:
        terms = []
        for req in reqs:
            terms.extend(self.extract_req_terms(smt_transformer, req, target_var))
        if use_projection:
            terms = [ProjectionWalker(target_var).walk(term) for term in terms]
        non_trivial_terms = [t for t in terms if t is not FALSE() and t is not TRUE()]
        return non_trivial_terms

    @staticmethod
    def extract_req_terms(smt_transformer: BoogiePysmtTransformer, req: Requirement, target_var: FNode) -> List[FNode]:
        parser = boogie_parsing.get_parser_instance()
        terms = []
        for _, formalisation in req.formalizations.items():
            expression_types = formalisation.scoped_pattern.get_allowed_types()
            for ident, expression in formalisation.expressions_mapping.items():
                if not expression or not expression.raw_expression or ident not in expression_types:
                    # filter out empty expressions and filter out expression not part of this pattern
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
                terms.append(smt_expr)
        return terms

    @staticmethod
    def extract_environment_assumption(
        variables: set[Variable], smt_transformer: BoogiePysmtTransformer
    ) -> List[FNode]:
        assumptions = []
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
                            assumptions.append(smt_expr)
                        case "Absence":
                            assumptions.append(Not(smt_expr))
        return assumptions

    @staticmethod
    def check_env_violated(
        terms: List[FNode], target_var: FNode, env_assumption: FNode, hanfor_var: Variable
    ) -> CompletenessCheckResult:
        """Check if all values a variable can tanke are inside the environment (if applicable)"""
        if target_var not in get_free_variables(env_assumption):
            return CompletenessCheckResult(
                hanfor_var.name, CompletenessCheckOutcome.OK, f"'{target_var.symbol_name()}' has no env assumptions."
            )
        with Solver(name=SOLVER_NAME, logic=LOGIC) as solver:
            for term in terms:
                if target_var in get_free_variables(env_assumption):
                    a_form = And(term, env_assumption)
                    intersects_environment = solver.is_sat(a_form)
                    if not intersects_environment:
                        return CompletenessCheckResult(
                            hanfor_var.name,
                            CompletenessCheckOutcome.ENV_VIOLATED,
                            f"'{target_var.symbol_name()}': term {term.serialize()} is completely outside of "
                            f"Environment.\nEnvironment is: {env_assumption.serialize()}\n",
                        )
        return CompletenessCheckResult(
            hanfor_var.name, CompletenessCheckOutcome.OK, "Expected values of the variable is inside the environment"
        )


class ProjectionWalker(IdentityDagWalker):
    def __init__(self, variable):
        super().__init__()
        self.parents = {}
        self.variable = variable

    def walk(self, formula, **kwargs):
        for arg in formula.args():
            self.parents[arg] = formula
            self.walk(arg, **kwargs)
        return super().walk(formula, **kwargs)

    def walk_and(self, formula, args, **kwargs):
        relevant_args = [f for f in args if self.variable in get_free_variables(f)]
        if relevant_args:
            return And(relevant_args)
        return self.__get_neutral_parent(formula)

    def walk_or(self, formula, args, **kwargs):
        relevant_args = [f for f in args if self.variable in get_free_variables(f)]
        if relevant_args:
            return Or(relevant_args)
        return self.__get_neutral_parent(formula)

    def __get_neutral_parent(self, formula):
        # if this leaf is empty, return the neutral element of the parent operator
        if formula not in self.parents:
            return Bool(True)
        par = self.parents[formula]
        if par.is_and():
            return Bool(True)
        elif par.is_not():
            return self.__get_neutral_parent(par)
        else:
            # TODO: figure out which nodes are there additionally (e.g. implication, just braces)
            return Bool(True)

    def walk_not(self, formula, args, **kwargs):
        arg = args[0]
        if self.variable in get_free_variables(arg):
            return Not(arg)
        return self.__get_neutral_parent(formula)

    def walk_atom(self, formula, **kwargs):
        if self.variable in get_free_variables(formula):
            return formula
        return self.__get_neutral_parent(formula)
