from pysmt.environment import Environment
from pysmt.fnode import FNode
from z3 import Symbol


def pattern_cases(smt_env: Environment, name) -> tuple[dict[str, FNode], str, str]:
    """Returns test data in the form:
    - Dict of expressions
    - Ct formula to be tested
    - expected result (also as a ct formula)"""
    fmgr = smt_env.formula_manager
    tmgr = smt_env.type_manager
    match name:
        case "false":
            return {"P": fmgr.FALSE()}, "⌈P⌉;true", "⌈FALSE⌉;True"
        case "true":
            return {}, "true;true", "True;True"
        case "true_lower_bound_empty":
            return {"T": fmgr.Symbol("T", tmgr.REAL())}, "true ∧ ℓ >₀ T;true", "True ∧ ℓ >₀ T;True"
        case "true_lower_bound":
            return {"T": fmgr.Symbol("T", tmgr.REAL())}, "true ∧ ℓ > T;true", "True ∧ ℓ > T;True"
        case "absence_globally":
            return {"R": fmgr.Symbol("R")}, "true;⌈R⌉;true", "True;⌈R⌉;True"
        case "absence_before":
            return (
                {"P": fmgr.Symbol("P"), "R": fmgr.Symbol("R")},
                "⌈!P⌉;⌈(!P && R)⌉;true",
                "⌈(! P)⌉;⌈((! P) & R)⌉;True",
            )
        case "absence_after":
            return {"P": fmgr.Symbol("P"), "R": fmgr.Symbol("R")}, "true;⌈P⌉;true;⌈R⌉;true", "True;⌈P⌉;True;⌈R⌉;True"
        case "absence_between":
            return (
                {"P": fmgr.Symbol("P"), "Q": fmgr.Symbol("Q"), "R": fmgr.Symbol("R")},
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
                "True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & R)⌉;⌈(! Q)⌉;⌈Q⌉;True",
            )
        case "absence_after_until":
            return (
                {"P": fmgr.Symbol("P"), "Q": fmgr.Symbol("Q"), "R": fmgr.Symbol("R")},
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true",
                "True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & R)⌉;True",
            )
        case "duration_bound_l_globally":
            return (
                {"R": fmgr.Symbol("R"), "T": fmgr.Symbol("T", tmgr.REAL())},
                "true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true",
                "True;⌈(! R)⌉;⌈R⌉ ∧ ℓ < T;⌈(! R)⌉;True",
            )
        case "duration_bound_l_before":
            return (
                {"P": fmgr.Symbol("P"), "R": fmgr.Symbol("R"), "T": fmgr.Symbol("T", tmgr.REAL())},
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < T;⌈(!P && !R)⌉;true",
                "⌈(! P)⌉;⌈((! P) & (! R))⌉;⌈((! P) & R)⌉ ∧ ℓ < T;⌈((! P) & (! R))⌉;True",
            )
        case "duration_bound_l_after":
            return (
                {"P": fmgr.Symbol("P"), "R": fmgr.Symbol("R"), "T": fmgr.Symbol("T", tmgr.REAL())},
                "true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < T;⌈!R⌉;true",
                "True;⌈P⌉;True;⌈(! R)⌉;⌈R⌉ ∧ ℓ < T;⌈(! R)⌉;True",
            )
        case "duration_bound_l_between":
            return (
                {
                    "P": fmgr.Symbol("P"),
                    "Q": fmgr.Symbol("Q"),
                    "R": fmgr.Symbol("R"),
                    "T": fmgr.Symbol("T", tmgr.REAL()),
                },
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < T;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true",
                "True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & (! R))⌉;⌈((! Q) & R)⌉ ∧ ℓ < T;⌈((! Q) & (! R))⌉;⌈(! Q)⌉;⌈Q⌉;True",
            )
        case "duration_bound_l_after_until":
            return (
                {
                    "P": fmgr.Symbol("P"),
                    "Q": fmgr.Symbol("Q"),
                    "R": fmgr.Symbol("R"),
                    "T": fmgr.Symbol("T", tmgr.REAL()),
                },
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < T;⌈(!Q && !R)⌉;true",
                "True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & (! R))⌉;⌈((! Q) & R)⌉ ∧ ℓ < T;⌈((! Q) & (! R))⌉;True",
            )
        case "duration_bound_u_globally":
            return (
                {"R": fmgr.Symbol("R"), "T": fmgr.Symbol("T", tmgr.REAL())},
                "true;⌈R⌉ ∧ ℓ ≥ T;true",
                "True;⌈R⌉ ∧ ℓ ≥ T;True",
            )
        case "response_delay_globally":
            return (
                {"R": fmgr.Symbol("R"), "S": fmgr.Symbol("S"), "T": fmgr.Symbol("T", tmgr.REAL())},
                "true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true",
                "True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True",
            )
        case "response_delay_before":
            return (
                {
                    "P": fmgr.Symbol("P"),
                    "R": fmgr.Symbol("R"),
                    "S": fmgr.Symbol("S"),
                    "T": fmgr.Symbol("T", tmgr.REAL()),
                },
                "⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true",
                "⌈(! P)⌉;⌈((! P) & (R & (! S)))⌉;⌈((! P) & (! S))⌉ ∧ ℓ > T;True",
            )
        case "response_delay_after":
            return (
                {
                    "P": fmgr.Symbol("P"),
                    "R": fmgr.Symbol("R"),
                    "S": fmgr.Symbol("S"),
                    "T": fmgr.Symbol("T", tmgr.REAL()),
                },
                "true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true",
                "True;⌈P⌉;True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True",
            )
        case "response_delay_between":
            return (
                {
                    "P": fmgr.Symbol("P"),
                    "Q": fmgr.Symbol("Q"),
                    "R": fmgr.Symbol("R"),
                    "S": fmgr.Symbol("S"),
                    "T": fmgr.Symbol("T", tmgr.REAL()),
                },
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true",
                "True;⌈(P & (! Q))⌉;⌈(! Q)⌉;⌈((! Q) & (R & (! S)))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;⌈(! Q)⌉;⌈Q⌉;True",
            )
        case "response_delay_after_until":
            return (
                {
                    "P": fmgr.Symbol("P"),
                    "Q": fmgr.Symbol("Q"),
                    "R": fmgr.Symbol("R"),
                    "S": fmgr.Symbol("S"),
                    "T": fmgr.Symbol("T", tmgr.REAL()),
                },
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true",
                "True;⌈P⌉;⌈(! Q)⌉;⌈((! Q) & (R & (! S)))⌉;⌈((! Q) & (! S))⌉ ∧ ℓ > T;True",
            )
        case "universality_globally":
            return (
                {
                    "P": fmgr.And(
                        fmgr.Equals(fmgr.Symbol("int", tmgr.INT()), fmgr.Int(1)),
                        fmgr.Equals(fmgr.Symbol("real", tmgr.REAL()), fmgr.Real(1.0)),
                    )
                },
                "true;⌈P⌉;true",
                "True;⌈((int = 1) & (real = 1.0))⌉;True",
            )
    raise NotImplementedError(f"Testcase {name} not existing")
