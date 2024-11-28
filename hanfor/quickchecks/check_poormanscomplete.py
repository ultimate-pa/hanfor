import logging

from pysmt.fnode import FNode
from pysmt.rewritings import CNFizer
from pysmt.shortcuts import FALSE, Or, Not, Exists, Solver, TRUE, get_free_variables, And, Bool
from pysmt.walkers import IdentityDagWalker

import boogie_parsing
from reqtransformer import Requirement, Variable
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer

SOLVER_NAME = "z3"
LOGIC = "UFLIRA"


class PoorMansComplete:

    def __call__(self, reqs: list[Requirement], vars: list[Variable]):
        logging.info("Starting PoorMansComplete Analysis for requirements set.")
        result = ""
        smt_transformer = BoogiePysmtTransformer({v.name: v for v in vars})
        for _, target_var in smt_transformer.smt_vars.items():
            term = self.extract_reqs_term(smt_transformer, reqs, target_var)
            term = FalseTermAbsorber().walk(term)
            result += self.check_complete_var(term, target_var)
        return result

    def check_complete_var(self, term: FNode, target_var: FNode):
        result = ""
        with Solver(name=SOLVER_NAME, logic=LOGIC) as solver:
            q_form = Not(term)
            is_incomplete = solver.is_sat(q_form)
            if is_incomplete:
                logging.info(
                    f"INCOMPLETE '{target_var.symbol_name()}', Value    {solver.get_value(target_var)}  is uncovered.\n"
                    f"{term}"
                )
        # return f"{target_var} is complete: {not is_incomplete}"
        return result

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
                if not expression.raw_expression:
                    # filter out empty expressions
                    continue
                if ident in expression_types and boogie_parsing.BoogieType.real in expression_types[ident]:
                    # filter out all expressions that are non-boolean (currently only clock constraints)
                    continue
                try:
                    ast = parser.parse(expression.raw_expression)
                except Exception as e:
                    logging.error(
                        f"Parsing error in requirement: {req.rid} expression {expression.raw_expression}.\n {e}"
                    )
                smt_expr = smt_transformer.transform(ast)
                if target_var not in get_free_variables(smt_expr):
                    continue
                term = Or(term, smt_expr)
        term = ProjectionWalker(target_var).walk(term)
        return term


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
