import logging
from dataclasses import dataclass
from typing import List

from pysmt.environment import Environment
from pysmt.fnode import FNode

from json_db_connector.json_db import DatabaseField, DatabaseFieldType
from lib_core import boogie_parsing
from lib_core.data import Requirement, Variable
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer

SOLVER_NAME = "z3"
LOGIC = "UFLIRA"

class DomainCompletenessOutcome:
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    INCOMPLETE_UNCONSTRAINT = "INCOMPLETE_UNCONSTRAINT"

@dataclass
@DatabaseFieldType()
@DatabaseField("var", str)
@DatabaseField("outcome", str)
@DatabaseField("message", str)
class DomainCompletenessCheck:
    var: str
    outcome: str
    message: str

class DomainCompleteness:
    """Checks requirements for domain completeness as stated in the report for Metarequirements"""

    CHECK_ID = "domain_completeness"

    def __init__(self, smt_env: Environment) -> None:
        self._smt_env = smt_env
        self._fmgr = smt_env.formula_manager
        self._parser = boogie_parsing.get_parser_instance()

    def run(self) -> None:
        pass

    def completeness_check(self) -> None:
        pass

    def projection(self, node: FNode, variable: FNode, negation=False) -> FNode:
        if node.is_and():
            children = [self.projection(child, variable, negation) for child in node.args()]
            if negation:
                return self._fmgr.Or(children)
            else:
                return self._fmgr.And(children)
        if node.is_or():
            children = [self.projection(child, variable, negation) for child in node.args()]
            if negation:
                return self._fmgr.And(children)
            else:
                return self._fmgr.Or(children)
        if node.is_not():
            return self.projection(node.arg(0), variable, not negation)
        if node.is_implies():
            return self.projection(self._fmgr.Or(self._fmgr.Not(node.arg(0)), node.arg(1)), variable, negation)
        if variable not in self._smt_env.fvo.get_free_variables(node):
            return self._fmgr.TRUE()
        # atom
        if negation:
            return self._fmgr.Not(node)
        else:
            return node

    def project(self, node: FNode, variable: FNode) -> FNode:
        return self._smt_env.simplifier.simplify(self.projection(node, variable))

    def extract_observables(self, requirements: list[Requirement], smt_transformer: BoogiePysmtTransformer) -> list:
        assumptions = []
        for req in requirements:
            for formalisation in req.formalizations.values():
                if not formalisation.is_pattern_based():
                    continue
                for raw in self.bool_expressions(formalisation):
                    smt_expr = self.parse(smt_transformer, raw, req.rid)
                    if smt_expr is not None:
                        assumptions.append((req.rid, smt_expr))
        return assumptions

    def extract_constraints(self, variables: set[Variable], smt_transformer: BoogiePysmtTransformer) -> List[FNode]:
        assumptions = []
        for var in variables:
            for key, formalisation in var.constraints.items():
                for raw in self.bool_expressions(formalisation):
                    smt_expr = self.parse(smt_transformer, raw, f"{var.name}/{key}")
                    if smt_expr is not None:
                        assumptions.append(self._fmgr.Not(smt_expr) if formalisation.scoped_pattern.pattern.name == "Absence" else smt_expr)
        return assumptions

    def parse(self, smt_transformer: BoogiePysmtTransformer, raw_expression: str, req: str):
        try:
            ast = self._parser.parse(raw_expression)
            return smt_transformer.transform(ast)
        except Exception as e:
            logging.error(
                f"Parsing error in requirement: {req} expression `{raw_expression}`.\n {e}"
            )
            return None

    def bool_expressions(self, formalisation):
        results = []
        expression_types = formalisation.scoped_pattern.get_allowed_types()
        for ident, expression in formalisation.expressions_mapping.items():
            if not expression or not expression.raw_expression or ident not in expression_types:
                # filter out empty expressions and filter out expression not part of this pattern
                continue
            if ident in expression_types and boogie_parsing.BoogieType.real in expression_types[ident]:
                # filter out all expressions that are non-boolean (currently only clock constraints)
                continue
            results.append(expression.raw_expression)
        return results