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

    class RtiPea:
        def __init__(self, pea: PhaseSetsPea, exit_condition: FNode, chain_req: bool, start_req: bool,
                     exit_variables: list):
            self.pea = pea #the fiven pea from the req
            self.exit_condition = exit_condition #the exit condition (NOt(phase n-1))
            self.chain_req = chain_req # Bool
            self.start_req = start_req # Bool, if req has time bounds
            self.exit_variables = exit_variables #variables from thr exit_condition


    def inconsistency_pre_check(self):
        # TODO: Do not modify existing member variables ;-)
        print("Called function inconsistency pre check ...")
        # get all Peas with required: exit condition
        peas_exit_conditinon = []  # list with all peas with attributes needed for pre-check
        peas_dict = {}
        rtis = []  # list with all possible rtis
        # first get all attributes from peas like countertrace, chain reqs etc
        peas_exit_conditinon = self.get_pea_attribute(peas_exit_conditinon)
        # sort the peas into a dict based on their attributes to have a faster access later
        peas_dict = self.sort_peas(peas_exit_conditinon, peas_dict)
        chain_reqs = []
        # get all chain reqs in an extra list
        chain_reqs = self.get_chain_req_list(chain_reqs, peas_dict, peas_exit_conditinon)

        rtis = self.get_pair_rtis(peas_dict, rtis)
        help = peas_dict
        # go through all chain reqs, start with smallest depth
        for depth in range(1, 3):
            copy_chain_reqs = chain_reqs.copy()
            while len(copy_chain_reqs) > 0:
                self.chain_check(copy_chain_reqs[0], copy_chain_reqs, depth, peas_dict, [copy_chain_reqs[0]], rtis)
                copy_chain_reqs.pop(0)
        help = rtis
        rtis = self.get_minimal_sets(rtis)
        for rti in rtis:
            print("----------")
            for req in rti:
                print(req.pea.countertrace)

    def get_chain_req_list(self, chain_reqs, peas_dict, peas_exit_conditinon):
        chain_reqs = [pea for pea in peas_exit_conditinon if pea.chain_req]

        chain_reqs.sort(key=lambda x: len(x.exit_variables), reverse=True)
        return chain_reqs

    def chain_check(self, chain_req, other_chain_reqs, depth, peas_dict, possible_rti, rtis):
        #if the number of chainreqs == depth of check -> check if they are a rti by themself
        if len(possible_rti) == depth:
            if self.rti_check(possible_rti):
                rtis.append(possible_rti)
            else:
                #try to fill with singles
                self.fill_chain_with_singles(chain_req, other_chain_reqs, depth, peas_dict, possible_rti, rtis)
        elif len(possible_rti) < depth:
            #add another matching chainreq to check
            for other_req in other_chain_reqs:
                if other_req not in possible_rti:
                    formula_already = self.rebuild_formula(possible_rti)
                    formula_check_new_req = Implies(self.simplify(formula_already), self.exit_condition(other_req.pea))
                    variables_old = formula_already.get_free_variables()
                    variables_new_req = other_req.exit_condition.get_free_variables()
                    if len(set(variables_old).intersection(set(variables_new_req))) > 0:
                        if not is_valid(formula_check_new_req):
                            new_list = possible_rti + [other_req]
                            # Recursive call to check further requirements
                            logging.debug("Adding worked" + str(formula_check_new_req))
                            self.chain_check(chain_req, other_chain_reqs, depth, peas_dict, new_list.copy(), rtis)

    def fill_chain_with_singles(self, chain_req, other_chain_reqs, depth, peas_dict, possible_rti, rtis):
        # list with chain reqs, fill with singles(no chain reqs) for rti
        formula = self.rebuild_formula(possible_rti)
        variables = self.recursive_varibales(formula, [])
        variables = list(set(variables))
        for var in variables:
            if Not(var) in variables:
                variables.remove(var)
                variables.remove(Not(var))
        list_with_singles = possible_rti.copy()
        selected_lists = []
        for var in variables:
            varhelp = var
            if "!" in str(var):
                varhelp = var._content.args[0]
            if varhelp in peas_dict:
                if peas_dict[varhelp]["type_variable"] == "Bool":

                    if "!" in str(var):
                        selected_lists.append((peas_dict[varhelp]["peas_positive"]))
                    else:
                        selected_lists.append(((peas_dict[var]["peas_negative"])))
                else:
                    selected_lists.append(peas_dict[var]["peas"])
            else:
                return

        combinations = list(itertools.product(*selected_lists))
        for combo in combinations:
            list_from_combo = possible_rti + list(combo)
            rtis.append(list_from_combo)
        #     list_from_combo = possible_rti + list(combo)
        #     if(self.rti_check(list_from_combo)):
        #         rtis.append(list_from_combo)

    def recursive_varibales(self, formula, list):
        if formula.is_constant() or formula.is_symbol() or formula.is_not and len(formula.args()) == 1:
            list.append(formula)
        else:
            for var in formula.args():
                self.recursive_varibales(var, list)
        return list

    def rti_check(self, requirements):
        # check if set of reqs can cause an rti
        starter_in_set = False
        # one of the reqs has to be starter req (time bound)
        for req in requirements:
            if req.start_req:
                starter_in_set = True
                break
        if not starter_in_set:
            return False
        # formmula has to be not sat
        if is_sat(self.rebuild_formula(requirements)):
            return False

        return True

    def get_pair_rtis(self, peas_dict: dict, rtis: list):
        # first serach for rtis with 2 reqs without chain reqs
        for variable in peas_dict:
            if peas_dict[variable]["type_variable"] is "Bool":
                for positive in peas_dict[variable]["peas_positive"]:
                    for negative in peas_dict[variable]["peas_negative"]:
                        if self.rti_check([positive, negative]):
                            rtis.append([positive, negative])
            else:
                for pea1 in peas_dict[variable]["peas"]:
                    for pea2 in peas_dict[variable]["peas"]:
                        if self.rti_check([pea1, pea2]):
                            rtis.append([pea1, pea2])

        return rtis

    def rebuild_formula(self, list_requirements):
        """Rebuild the formula dynamically from the remaining requirements"""
        if not list_requirements:
            return TRUE  # or an appropriate base formula
        formula = self.exit_condition(list_requirements[0].pea)
        for k in range(1, len(list_requirements)):
            formula = And(self.exit_condition(list_requirements[k].pea), formula)
        return self.simplify(formula)

    def exit_condition(self, requirement):
        # Generate and return the DNF of the exit condition
        return self.simplify(Not(requirement.countertrace.dc_phases[-2].invariant))

    def get_pea_attribute(self, peas_exit_condition):
        # get all attributes needed for pre_check
        for pea in self.peas:
            exit_condition = self.exit_condition(pea)
            is_start_req = False
            if len(pea.clocks) > 0:
                is_start_req = True  # start req -> is timed, one of them is needed for an rti
            is_chain_req = False
            if exit_condition.is_or():
                is_chain_req = True  # chain req if exit-Condition has a or (||) in it
            variables = self.recursive_varibales(exit_condition, [])
            i = 0
            while i < len(variables):
                try:
                    test = float(str(variables[i]).replace("(", "").replace(")", ""))
                    variables.pop(i)
                except ValueError:
                    i += 1

            peas_exit_condition.append(
                self.RtiPea(pea, exit_condition, is_chain_req, is_start_req, variables))
        return peas_exit_condition

    def sort_peas(self, peas_exit_condition: list[RtiPea], peas_dict) -> dict:
        # Sort the peas based on their exit conditions and the variables in tehre and the type of it
        for pea in peas_exit_condition:
            if not pea.chain_req:
                for variable in pea.exit_condition.get_free_variables():
                    if variable._content.payload[1].name is "Bool":
                        if ("! " + str(variable)) in str(pea.exit_condition):
                            if not variable in peas_dict.keys():
                                peas_dict[variable] = {"variable": variable, "type_variable": "Bool", "peas_positive": [],
                                                       "peas_negative": [pea]}

                            else:
                                peas_dict[variable]["peas_negative"].append(pea)
                        else:
                            if not variable in peas_dict.keys():
                                peas_dict[variable] = {"variable": variable, "type_variable": "Bool",
                                                       "peas_positive": [pea], "peas_negative": []}

                            else:
                                peas_dict[variable]["peas_positive"].append(pea)


                    else:
                        if not variable in peas_dict.keys():
                            peas_dict[variable] = {"variable": variable, "type_variable": "Int", "peas": [pea]}

                        else:
                            peas_dict[variable]["peas"].append(pea)

        return peas_dict
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
                        # if rtis[rti1][k].requirement.pos_in_csv == rtis[rti2][l].requirement.pos_in_csv:
                        if rtis[rti1][k].pea.countertrace == rtis[rti2][l].pea.countertrace:
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



