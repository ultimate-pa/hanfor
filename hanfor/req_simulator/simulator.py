from __future__ import annotations

import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple
import logging

from pysmt.fnode import FNode
from pysmt.rewritings import conjunctive_partition
from pysmt.shortcuts import And, Equals, Symbol, Real, EqualsOrIff, get_model, is_sat, FALSE, get_unsat_core, Not, Solver, Or, is_valid, Implies, TRUE
from pysmt.typing import REAL

from z3 import Then, Tactic, With, Goal, Int, Bool
from lib_pea.config import SOLVER_NAME, LOGIC
from lib_pea.countertrace_to_pea import complete
from lib_pea.location import PhaseSetsLocation
from lib_pea.pea import PhaseSetsPea
from lib_pea.transition import PhaseSetsTransition
from req_simulator.scenario import Scenario
from req_simulator.utils import num_zeros
from reqtransformer import Requirement, Formalization

from hanfor.hanfor.lib_pea.countertrace import Countertrace


class Simulator:
    @dataclass
    class SatResult:
        transitions: Tuple[PhaseSetsTransition]
        model: dict[FNode, FNode]
        guard: FNode

    def __init__(
        self, peas: list[PhaseSetsPea], scenario: Scenario = None, name: str = "unnamed", test: bool = False
    ) -> None:
        self.name: str = name
        self.scenario: Scenario = scenario

        self.times: list[float] = [0.0]  # history
        self.time_steps: list[float] = [1.0]  # history

        self.peas: list[PhaseSetsPea] = peas
        self.current_phases: list[list[PhaseSetsLocation | None]] = [[None] * len(self.peas)]  # history
        self.clocks: list[dict[str, float]] = [{vv: 0.0 for v in self.peas for vv in v.clocks}]  # history
        self.sat_results: list[Simulator.SatResult] = []
        self.sat_error: str | None = None
        self.max_results: int = -1

        self.variables: dict[FNode, list[FNode | None]] = {
            v: [None] for p in self.peas for v in p.countertrace.extract_variables()
        }  # history
        self.models: dict[FNode, list[FNode | None]] = {k: [None] for k in self.variables}  # history

        if self.scenario is not None:
            if not test:
                self.scenario.remove_variables(self.scenario.difference(list(self.variables.keys())))

                if len(self.scenario.variables) != len(self.variables):
                    diff = [k for k in self.variables if k not in self.scenario.variables]
                    raise ValueError("Missing variables in scenario: %s" % diff)

            self.time_steps[-1] = self.scenario.times[len(self.times)] - self.scenario.times[len(self.times) - 1]
            for k, v in self.variables.items():
                v[-1] = self.scenario.variables[k][len(self.times)]

    def all_vars_are_None(self) -> bool:
        return len(self.variables) == len([k for k, v in self.variables.items() if v[-1] is None])

    def get_cartesian_size(self) -> str:
        return str(math.prod(len(self.peas[i].transitions[v]) for i, v in enumerate(self.current_phases[-1])))

    def get_times(self) -> list[str]:
        return [str(v) for v in self.times]

    def get_types(self) -> dict[str, str]:
        return {str(k): str(k.symbol_type()) for k in self.variables}

    def get_variables(self) -> dict[str, list[str]]:
        return {str(k): [str(v_) for v_ in v] for k, v in self.variables.items()}

    def get_scenario(self) -> dict[str, any] | None:
        if self.scenario is None:
            return None

        return {
            "times": [str(v) for v in self.scenario.times],
            "variables": {str(k): [str(v_) for v_ in v] for k, v in self.scenario.variables.items()},
        }

    def get_models(self) -> dict[str, list[str]]:
        return {str(k): [str(v_) for v_ in v] for k, v in self.models.items()}

    def get_active_dc_phases(self) -> dict[str, list[str]]:
        result = {"complete": [], "waiting": [], "exceeded": []}

        if self.current_phases[-1][0] is None:
            return result

        clock_assertions = self.build_clocks_assertion(self.clocks[-1])

        for i, current_phase in enumerate(self.current_phases[-1]):
            prefix = f"{self.peas[i].requirement.rid}_{self.peas[i].formalization.id}_{self.peas[i].countertrace_id}_"

            for v in current_phase.label.active:
                is_complete = is_sat(
                    And(complete(self.peas[i].countertrace, current_phase.label, v, "c_" + prefix), clock_assertions),
                    solver_name=SOLVER_NAME,
                    logic=LOGIC,
                )

                if is_complete:
                    result["complete"].append(prefix + str(v))
                    continue

                if v not in current_phase.label.less:
                    result["waiting"].append(prefix + str(v))
                    continue

                result["exceeded"].append(prefix + str(v))

        return result

    def get_transitions(self):
        results = []

        for sat_result in self.sat_results:
            model = "; ".join([f"{k} = {v}" for k, v in sat_result.model.items() if self.variables[k][-1] is None])
            results.append(model if model != "" else "True")

        return results

    def get_pea_mapping(self) -> dict[Requirement, dict[Formalization, dict[str, PhaseSetsPea]]]:
        result = defaultdict(lambda: defaultdict(dict))

        for pea in self.peas:
            result[pea.requirement][pea.formalization][pea.countertrace_id] = pea

        return result

    @staticmethod
    def load_scenario_from_file(simulator: Simulator, path: str) -> Simulator:
        return Simulator(simulator.peas, Scenario.load_from_file(path))

    def save_scenario_to_file(self, path: str) -> None:
        Scenario.save_to_file(self.scenario, path)

    def update_variables(self, variables: dict[FNode, FNode] = None) -> None:
        # TODO: fix scenario
        if variables is None and self.scenario is not None:
            variables = self.scenario.valuations.get(self.times[-1]).values

        if variables is not None:
            for k, v in variables.items():
                self.variables[k][-1] = v

    @staticmethod
    def update_clocks(clocks: dict[str, float], resets: frozenset[str], time_step: float) -> dict[str, float]:
        result = clocks.copy()

        for k, v in result.items():
            result[k] = time_step if k in resets else v + time_step

        return result

    @staticmethod
    def build_variables_assertion(variables: dict[FNode, FNode]) -> FNode:
        return And(EqualsOrIff(k, v) for k, v in variables.items() if v is not None)

    @staticmethod
    def build_clocks_assertion(clocks: dict[str, float]) -> FNode:
        return And(Equals(Symbol(k, REAL), Real(v)) for k, v in clocks.items())

    """
    def build_guard(self, transition: Transition, clocks: dict[str, float]) -> FNode:
        f = And(self.build_var_assertions(), transition.guard, self.build_clocks_assertion(clocks))

        return f

    def build_clock_invariant(self, transition: Transition, clocks: dict[str, float]) -> FNode:
        f = And(substitute_free_variables(transition.dst.clock_invariant),
                substitute_free_variables(self.build_clocks_assertion(clocks)))

        return f
    """

    def calculate_max_time_step(self, transition: PhaseSetsTransition, clocks: dict[str, float], time_step: float):
        k, v = transition.dst.get_min_clock_bound()

        if k is not None and v is not None:
            delta = v - clocks[k]
            time_step = time_step if delta <= 0 else min(time_step, delta)

        return time_step

    def compute_max_duration(self, transition) -> float:
        result = self.time_steps[-1]

        # transitions_list = [v.phases[self.current_phases[-1][i]] for i, v in enumerate(self.peas)]

        # for transitions in transitions_list:
        # for transition in transitions:
        min_bound = transition.dst.get_min_clock_bound()

        if min_bound is None:
            return result

        clock, bound, is_lt_bound = min_bound
        diff = bound - self.clocks[-1][clock]
        result_ = bound if clock in transition.resets else round(diff, num_zeros(diff) + 1)

        # if is_lt_bound:
        #    num_zeros = -math.floor(math.log10(result_)) - 1
        #    result_ = result_ - 0.1 if result_ >= 1 else round(result_ - pow(10, -num_zeros - 1), num_zeros + 1)

        # if result_ < result:
        #    result = result_

        return min(result_, result)

    def pre_check(
        self, phases: list[PhaseSetsLocation], var_asserts: FNode, clock_asserts: FNode
    ) -> list[list[PhaseSetsTransition]]:
        result = []

        for i, transitions in enumerate(phases):
            result_ = []
            last_fail = None

            for e in transitions:
                # Check the guard with var and clock asserts.
                if not is_sat(And(e.guard, var_asserts, clock_asserts), solver_name=SOLVER_NAME, logic=LOGIC):
                    last_fail = And(e.guard, var_asserts, clock_asserts)
                    continue

                # Compute duration to the closest bound, update clocks and build clock asserts.
                self.time_steps[-1] = self.compute_max_duration(e)
                updated_clocks = self.update_clocks(self.clocks[-1], e.resets, self.time_steps[-1])
                updated_clocks_assert = self.build_clocks_assertion(updated_clocks)

                # Check the clock invariant of p'. (special case: last non-true phase has bound type '<=')
                if not is_sat(And(e.dst.clock_invariant, updated_clocks_assert), solver_name=SOLVER_NAME, logic=LOGIC):
                    continue

                result_.append(e)

            # Check whether at least one transition is enabled.
            # If not store an error message.
            if len(result_) <= 0:
                reason = ""
                if len(transitions) <= 0:
                    reason += "inconsistency"
                else:
                    unsat_core = get_unsat_core(conjunctive_partition(last_fail))
                    unsat_core = "Unknown" if not unsat_core else "\n" + ", ".join([f.serialize() for f in unsat_core])
                    reason += "unrealizable input, " + unsat_core

                # reason = 'inconsistency' if len(transitions) <= 0 else \
                #    'unrealizable input, ' + get_unsat_core(conjunctive_partition(last_fail))

                self.sat_error = "Requirement violation: %s, Formalization: %s, Countertrace: %s\nReason: %s" % (
                    self.peas[i].requirement.rid,
                    self.peas[i].formalization.id,
                    self.peas[i].countertrace_id,
                    reason,
                )

                break

            result.append(result_)

        return result

    def check_sat(self) -> bool:
        self.sat_results = []
        self.sat_error = None

        if not self.time_steps[-1] > 0.0:
            self.sat_error = "Time step must be greater than zero."
            # raise ValueError('Time step must be greater than zero.')
            return False

        # primed_vars = {}
        # primed_vars_mapping = {}
        # for k, v in self.variables.items():
        #    k_ = substitute_free_variables(k)
        #    primed_vars[k_] = v[-1]
        #    primed_vars_mapping[k_] = k

        # var_asserts = self.build_variables_assertion(primed_vars)

        # self.time_steps[-1] = self.calculate_chop_point()

        var_asserts = self.build_variables_assertion({k: v[-1] for k, v in self.variables.items()})
        clock_asserts = self.build_clocks_assertion(self.clocks[-1])

        inputs = self.pre_check(
            [v.transitions[self.current_phases[-1][i]] for i, v in enumerate(self.peas)], var_asserts, clock_asserts
        )

        if self.sat_error is not None:
            return False

        self.sat_results = self.cartesian_check(inputs, var_asserts, clock_asserts)
        return len(self.sat_results) != 0

        # Compute cartesian product with intermediate checks
        results: list[Simulator.SatResult] = []

        for e in inputs[0]:
            model = get_model(e.guard, solver_name=SOLVER_NAME, logic=LOGIC)
            values = model.get_values(self.variables.keys())
            values.update({k: v[-1] for k, v in self.variables.items() if v[-1] is not None})

            if e.src is not None:
                results.append(
                    Simulator.SatResult(
                        (e,),
                        values,
                        And(var_asserts, clock_asserts, e.guard).simplify(),
                        # (e,), {primed_vars_mapping[k]: v for k, v in values.items()}, And(var_asserts, clock_asserts, e.guard).simplify()
                    )
                )
            else:
                results.append(
                    Simulator.SatResult(
                        (e,),
                        values,
                        And(var_asserts, e.guard).simplify(),
                        # (e,), {primed_vars_mapping[k]: v for k, v in values.items()}, And(var_asserts, e.guard).simplify()
                    )
                )

        for i, input in enumerate(inputs[1:]):
            results_: list[Simulator.SatResult] = []
            last_fail = None

            for result in results:

                for e in input:
                    guard = And(result.guard, e.guard).simplify()

                    if guard == FALSE():
                        last_fail = guard
                        continue

                    if i < len(inputs[1:]) - 1:
                        sat = is_sat(guard, solver_name=SOLVER_NAME, logic=LOGIC)

                        if sat:
                            results_.append(Simulator.SatResult(result.transitions + (e,), None, guard))

                    else:
                        model = get_model(guard, solver_name=SOLVER_NAME, logic=LOGIC)

                        if model is not None:
                            values = model.get_values(self.variables.keys())
                            values.update({k: v[-1] for k, v in self.variables.items() if v[-1] is not None})
                            # values = model.get_values(primed_vars.keys())
                            # values = {primed_vars_mapping[k]: v for k, v in values.items()}
                            results_.append(Simulator.SatResult(result.transitions + (e,), values, guard))

            results = results_

            if len(results) == 0:
                self.sat_error = "Requirement violation: %s, Formalization: %s, Countertrace: %s\nReason: %s" % (
                    self.peas[i].requirement.self.peas[i],
                    self.peas[i].formalization.id,
                    self.peas[i].countertrace_id,
                    get_unsat_core(conjunctive_partition(last_fail)),
                )
                return False

        self.sat_results = results

        return True

    def cartesian_check(
        self,
        phases: list[list[PhaseSetsTransition]],
        var_asserts,
        clock_asserts,
        i: int = 0,
        guard=None,
        trs=(),
        max_results=20,
        num_transitions=1,
    ) -> list[SatResult]:

        # Terminate if tuple of transitions is complete.
        if i >= len(phases):
            # model = get_model(guard, solver_name=SOLVER_NAME, logic=LOGIC)
            model = get_model(And(guard, var_asserts, clock_asserts), solver_name=SOLVER_NAME, logic=LOGIC)
            values = model.get_values(self.variables.keys())
            values.update({k: v[-1] for k, v in self.variables.items() if v[-1] is not None})

            return [Simulator.SatResult(trs, values, None)]

        result = []
        num_transitions *= len(phases[i])

        for transition in phases[i]:
            # Check conjunction of guards including the one of this transition with var and clock asserts.
            guard_ = And(guard, transition.guard) if guard is not None else And(transition.guard)

            if not is_sat(And(guard_, var_asserts, clock_asserts), solver_name=SOLVER_NAME, logic=LOGIC):
                self.last_fail = guard_
                continue

            # Call again to check transitions of next location.
            result.extend(
                self.cartesian_check(
                    phases, var_asserts, clock_asserts, i + 1, guard_, trs + (transition,), max_results, num_transitions
                )
            )

            if self.max_results > 0 and num_transitions >= self.max_results and len(result) >= 1:
                break

        # Check whether at least one transition is enabled.
        # If not store an error message.
        if i == 0 and len(result) == 0:
            reason = ""

            if is_sat(And(self.last_fail, clock_asserts)):
                reason += "unrealizable input"
            else:
                reason += "inconsistency" if self.current_phases[-1][0] == None else "rt-inconsistency"

            unsat_core = get_unsat_core(conjunctive_partition(self.last_fail))
            unsat_core = "Unknown" if not unsat_core else "\n" + ", ".join([f.serialize() for f in unsat_core])

            self.sat_error = "Requirement violation: %s, Formalization: %s, Countertrace: %s\nReason: %s, %s" % (
                self.peas[i].requirement.rid,
                self.peas[i].formalization.id,
                self.peas[i].countertrace_id,
                reason,
                unsat_core,
            )

        return result

    """
    def check_sat_old(self) -> None:
        if not self.time_steps[-1] > 0.0:
            raise ValueError('Time step must be greater than zero.')

        self.sat_results = []

        transition_lists = [self.peas[i].get_transitions(self.current_phases[-1][i]) for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

        time_step_max = self.time_steps[-1]
        for transition_tuple in transition_tuples:
            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                clock_bound = transition.dst.get_min_clock_bound()
                if clock_bound is not None:
                    delta = clock_bound[1] - self.clocks[-1][clock_bound[0]]
                    time_step_max = time_step_max if delta <= 0 else min(time_step_max, delta)

        self.time_steps[-1] = time_step_max

        for transition_tuple in transition_tuples:
            f = TRUE()

            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                # TODO: Can be split into two check sat, if it improves performance.
                # In this case, the substitution of clocks can be omitted.
                f = And(f, self.build_guard(transition, self.clocks[-1]),
                        self.build_clock_invariant(transition,
                                                   self.update_clocks(self.clocks[-1], transition.resets,
                                                                      self.time_steps[-1])))

            model = get_model(f, SOLVER_NAME, LOGIC)

            if model is not None:
                primed_variables = {substitute_free_variables(k): k for k in self.variables}
                model = model.get_values(primed_variables.keys())

                self.sat_results.append((transition_tuple, {v: model[k] for k, v in primed_variables.items()}))
    """

    def step_next(self, enabled_transition_index: int) -> None:
        if self.scenario is not None and self.times[-1] >= self.scenario.times[-1]:
            raise ValueError("Scenario end reached.")

        if self.time_steps[-1] < 1e-5:
            raise ValueError("Timestep is too small.")

        sat_result = self.sat_results[enabled_transition_index]

        # Save state
        self.times.append(self.times[-1])
        self.time_steps.append(self.time_steps[-1])
        self.current_phases.append(self.current_phases[-1].copy())
        self.clocks.append(self.clocks[-1].copy())

        for k, v in self.models.items():
            v.append(v[-1])

        for k, v in self.variables.items():
            v.append(v[-1])

        # step
        for k, v in self.models.items():
            v[-1] = sat_result.model[k]

        resets = frozenset()
        for i, transition in enumerate(sat_result.transitions):
            self.current_phases[-1][i] = transition.dst
            resets |= transition.resets

        self.clocks[-1] = self.update_clocks(self.clocks[-1], resets, self.time_steps[-1])

        self.sat_results = []
        self.times[-1] += self.time_steps[-1]

        if self.scenario is None:
            return

        configuration = self.scenario.get_configuration(self.times[-1])

        if configuration is None:
            return

        self.time_steps[-1] = configuration.time - self.times[-1]

        for k, v in self.variables.items():
            v[-1] = configuration.variables[k]

    def step_back(self) -> bool:
        if len(self.times) < 2:
            return False

        self.times.pop()
        self.time_steps.pop()
        self.current_phases.pop()
        self.clocks.pop()

        for k, v in self.models.items():
            v.pop()

        for k, v in self.variables.items():
            v.pop()

        return True

    def variable_constraints(self):
        # TODO: Do not modify existing member variables ;-)
        print("Called function variable constraints ...")

    def recursive_varibales(self, formula, list):
        if formula.is_constant() or formula.is_symbol() or formula.is_not and len(formula.args()) == 1:
            list.append(formula)
        else:
            for var in formula.args():
                self.recursive_varibales(var, list)
        return list


    def exit_condition(self, requirement):
        # Generate and return the DNF of the exit condition
        return self.simplify(Not(requirement.countertrace.dc_phases[-2].invariant))



    def divide_formula(self, formula):
        if formula.is_or():
            # Recursively divide each operand
            return [operand for arg in formula.args() for operand in self.divide_formula(arg)]
        else:
            # Base case: return the formula itself
            return [formula]


    import copy


    def rebuild_formula(self, list_requirements):
        """Rebuild the formula dynamically from the remaining requirements"""
        if not list_requirements:
            return TRUE  # or an appropriate base formula
        formula = self.exit_condition(list_requirements[0])
        for k in range(1, len(list_requirements)):
            formula = And(self.exit_condition(list_requirements[k]), formula)
        return formula

    def get_minimal_sets(self, rtis):
        # Iterate through rtis list from the last to the first
        rti1 = len(rtis) - 1
        while rti1 >= 0:
            rti2 = len(rtis) - 1
            while rti2 > rti1:
                csvCheck = True
                # Check if all elements of rtis[rti1] are present in rtis[rti2]
                for k in range(len(rtis[rti1])):
                    variabel_check = False
                    for l in range(len(rtis[rti2])):
                        #if rtis[rti1][k].requirement.pos_in_csv == rtis[rti2][l].requirement.pos_in_csv:
                        if rtis[rti1][k].countertrace== rtis[rti2][l].countertrace:
                            variabel_check = True
                            break  # If found, no need to continue inner loop
                    if not variabel_check:
                        csvCheck = False
                        break  # If one element is missing, break early
                # If csvCheck is true, remove the larger set (rti2)
                if csvCheck:
                    rtis.pop(rti2)
                rti2 -= 1
            rti1 -= 1
        return rtis

    def simplify (self, f: FNode) -> FNode:
        solver_z3 = Solver(name="z3")
        #tactic = Then(Tactic('simplify'),Tactic('ctx-solver-simplify'))
        #tactic = Then(Tactic('simplify'), Tactic('ctx-solver-simplify'), Tactic('propagate-ineqs'))
        # tactic = Then(Tactic('simplify'), Tactic('propagate-values'), Tactic('ctx-simplify'))
        #tactic1 = Tactic('ctx-solver-simplify')
        #tactic1 = Tactic("simplify")
        #tactic = Tactic('solve-eqs')
        tactic3 = Then(With(Tactic("simplify"), elim_and=True), Tactic("propagate-values"))
        #juhu = solver_z3.converter.convert(f)
        #opop = tactic1(juhu)
        #result = tactic1(solver_z3.converter.convert(f)).as_expr()
        ruru = tactic3(solver_z3.converter.convert(f)).as_expr()
        t2 =  Tactic("propagate-values")
        result = solver_z3.converter.back(ruru)

        result = t2(solver_z3.converter.convert(result)).as_expr()
        result = solver_z3.converter.back(result)
        return result

    def get_Value_list(self, listSTingle, sortedList):
        for req in listSTingle:
            variables_new_req_val = self.recursive_varibales(self.exit_condition(req), [])
            for var in variables_new_req_val:
                found = False
                for listItem in sortedList:
                    if listItem[0] == var:
                        listItem[1].append(req)
                        found = True
                        continue
                if not found:
                    sortedList.append([var,[req]])
        return sortedList


    def getLists(self, listSingle, soretdList):
        for req in listSingle:
            variables_new_req_val = self.recursive_varibales(self.exit_condition(req), [])
            for var in variables_new_req_val:
                variables_new_req = var.get_free_variables()
                found = False
                for list_variable in soretdList:
                    if variables_new_req == list_variable[0]:
                        found = True
                        if '!' in str(var):
                            list_variable[2].append(req)
                        else:
                            list_variable[1].append(req)

                if not found:
                    if '!' in str(var):
                        soretdList.append([variables_new_req, [],[req]])
                    else:
                        soretdList.append([variables_new_req, [req],[]])

        return soretdList

    def single_rtis(self, sorted_list, rtis):
        for list in sorted_list:
            if len(sorted_list[1]) != 0 and len(sorted_list[2]) != 0:
                for positive in list[1]:
                    for negative in list[2]:
                        rtis.append([positive, negative])
        return rtis



    def chain_rtis(self, chain_reqs_2, sortedLists_singles, list_reqs, possible_rtis, chain_rtis, depth):

        exit_condition = self.simplify(self.rebuild_formula(list_reqs))

        if len(list_reqs) == depth:
            variables = self.recursive_varibales(exit_condition, [])
            for var in variables:
                if Not(var) in variables:
                    variables.remove(var)
                    variables.remove(Not(var))
            variables = list(set(variables))
            selected_lists = [listi for listi in sortedLists_singles if Not(listi[0]) in variables]
            reqs = [listi[1] for listi in selected_lists]
            combinations = list(itertools.product(*reqs))
            logging.debug("try to fill with singles")
            #list_reqs have to have length depth to check for singles to fill
            rti_with_those_chains = False
            if rti_with_those_chains == False:


                for combo in combinations:
                    rti = list_reqs.copy()
                    if len(combo) == len(variables):

                        for c in combo:
                            rti.append(c)
                        possible_rtis.append(rti)
        if len(list_reqs)< depth:
            for chain in chain_reqs_2:
                logging.debug("try to add new chain req")
                if chain not in list_reqs:
                    for i in list_reqs:
                        logging.debug(str(i.countertrace))
                    logging.debug("NEW: "+ str(chain.countertrace))

                    if not is_sat(And(exit_condition, self.exit_condition(chain))) and len(list_reqs) == depth:
                        rti = list_reqs.copy()
                        possible_rtis.append(rti)
                        logging.debug("rti found")
                        print("rti found")

                    else:
                        new_rti = True

                        if new_rti:
                            variables_new_req = self.exit_condition(chain).get_free_variables()
                            variables_list = exit_condition.get_free_variables()
                            # If there are common variables and the formula is not valid
                            if len(set(variables_list).intersection(set(variables_new_req))) > 0:
                                formula_check_new_req = Implies(self.simplify(exit_condition),self.exit_condition(chain))
                                if not is_valid(formula_check_new_req):
                                    new_list = list_reqs.copy()
                                    new_list.append(chain)
                                    # Recursive call to check further requirements
                                    logging.debug("Adding worked" + str( formula_check_new_req))

                                    self.chain_rtis(chain_reqs_2, sortedLists_singles, new_list, possible_rtis, chain_rtis, depth)

        return possible_rtis





    def inconsistency_pre_check(self):
        # TODO: Do not modify existing member variables ;-)
        print("Called function inconsistency pre check ...")
        counter = 0
        possible_rtis = []

        chain_reqs = []
        simple_reqs = []
        sortedLists_singles = []

        #devide rtis in two groups
        for pea in self.peas:
            if self.exit_condition(pea).is_or():
                chain_reqs.append(pea) #exit condition has a or --> it is a chain req
            else:
                simple_reqs.append(pea) #exit-condition has no or --> it's a single
        #get Lists per variable
        sortedLists_singles = self.getLists(simple_reqs, sortedLists_singles)
        #find rtis with set size 2
        possible_rtis = self.single_rtis(sortedLists_singles, possible_rtis)
        chain_reqs.sort(key=lambda x: len(x.formalization.used_variables), reverse=True)
        sortedLists_singles_value = self.get_Value_list(simple_reqs, [])
        logging.debug("CHAIN REQS")
        chain_rtis = []
        logging.debug(f"chain_reqs before depth loop: {chain_reqs}")
        #look recursively but with incrysing depth to find "easy rtis" first
        for depth in range(1, 3):
            print("---------------------------------")
            print(depth)
            logging.debug(f"Depth {depth}: chain_reqs: {chain_reqs}")
            new_chain_reqs = chain_reqs.copy()
            logging.debug(f"New chain_reqs after copy: {new_chain_reqs}")
            # reset new_chain_reqs for each depth
            while len(new_chain_reqs) > 0:
                #start search with chain req
                chain = new_chain_reqs[0]
                logging.debug("NEW CHAIN REQ START --------------------")
                print("NEW CHAIN REQ --------------------")
                print(str(chain.countertrace))
                logging.debug(str(chain.countertrace))
                possible_rtis = self.chain_rtis(new_chain_reqs, sortedLists_singles_value, [chain], possible_rtis,
                                                chain_rtis, depth)
                new_chain_reqs.remove(chain) # if a chain found all rtis delete it for this depth




        possible_rtis.sort(key=len)
        #delete not minimal sets
        possible_rtis = self.get_minimal_sets(possible_rtis)




        for i in possible_rtis:
            print("POSSIBLE RTIS:")
            for k in i:
                print(k.countertrace , " - ExitCondition: ", self.exit_condition(k))
            print("------------------------------------")









