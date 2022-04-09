from __future__ import annotations

import itertools
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Tuple

from pysmt.fnode import FNode
from pysmt.shortcuts import And, Equals, Symbol, Real, EqualsOrIff, TRUE, get_model, is_sat
from pysmt.typing import REAL

from req_simulator.phase_event_automaton import PhaseEventAutomaton, Phase, Transition, complete
from req_simulator.scenario import Scenario
from req_simulator.utils import substitute_free_variables, SOLVER_NAME, LOGIC
from reqtransformer import Requirement, Formalization


class Simulator:

    @dataclass
    class SatResult:
        transitions: Tuple[Transition]
        model: dict[FNode, FNode]

    def __init__(self, peas: list[PhaseEventAutomaton], scenario: Scenario = None, name: str = 'unnamed') -> None:
        self.name: str = name
        self.scenario: Scenario = scenario

        self.times: list[float] = [0.0]  # history
        self.time_steps: list[float] = [1.0]  # history

        self.peas: list[PhaseEventAutomaton] = peas
        self.current_phases: list[list[Phase | None]] = [[None] * len(self.peas)]  # history
        self.clocks: list[dict[str, float]] = [{vv: 0.0 for v in self.peas for vv in v.clocks}] # history

        self.sat_results: list[Simulator.SatResult] = []
        #self.enabled_transitions: list[tuple[tuple[Transition], dict[FNode, FNode]]] = []

        self.variables: dict[FNode, list[FNode | None]] = \
            {v: [None] for p in self.peas for v in p.countertrace.extract_variables()}  # history
        self.models: dict[FNode, list[FNode | None]] = {k: [None] for k in self.variables}  # history

        if self.scenario is not None:
            self.time_steps[-1] = self.scenario.valuations[0.0].get_duration()
            self.update_variables()

    def get_times(self) -> list[str]:
        return [str(v) for v in self.times]

    def get_types(self) -> dict[str, str]:
        return {str(k): str(k.symbol_type()) for k in self.variables}

    def get_variables(self) -> dict[str, list[str]]:
        return {str(k): [str(v) for v in vv] for k, vv in self.variables.items()}

    def get_models(self) -> dict[str, list[str]]:
        return {str(k): [str(v) for v in vv] for k, vv in self.models.items()}

    def get_active_dc_phases(self) -> dict[str, list[str]]:
        result = {'complete': [], 'waiting': [], 'exceeded': []}

        if self.current_phases[-1][0] is None:
            return result

        clock_assertions = self.build_clocks_assertion(self.clocks[-1])

        for i, current_phase in enumerate(self.current_phases[-1]):
            prefix = f'{self.peas[i].requirement.rid}_{self.peas[i].formalization.id}_{self.peas[i].countertrace_id}_'

            for v in current_phase.sets.active:
                is_complete = is_sat(And(complete(self.peas[i].countertrace, current_phase.sets, v, 'c_' + prefix),
                                     clock_assertions), solver_name=SOLVER_NAME, logic=LOGIC)

                if is_complete:
                    result['complete'].append(prefix + str(v))
                    continue

                if v not in current_phase.sets.less:
                    result['waiting'].append(prefix + str(v))
                    continue

                result['exceeded'].append(prefix + str(v))

        return result

    '''
    def get_transitions(self):
        results = []

        for transition in self.enabled_transitions:
            model = ' ; '.join([f'{k} = {v}' for k, v in transition[1].items() if self.variables[k][-1] is None])
            results.append(model if model != '' else 'True')

        return results
    '''

    def get_transitions(self):
        results = []

        for sat_result in self.sat_results:
            model = ' ; '.join([f'{k} = {v}' for k, v in sat_result.model.items() if self.variables[k][-1] is None])
            results.append(model if model != '' else 'True')

        return results

    def get_pea_mapping(self) -> dict[Requirement, dict[Formalization, dict[str, PhaseEventAutomaton]]]:
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

    '''
    def build_guard(self, transition: Transition, clocks: dict[str, float]) -> FNode:
        f = And(self.build_var_assertions(), transition.guard, self.build_clocks_assertion(clocks))

        return f

    def build_clock_invariant(self, transition: Transition, clocks: dict[str, float]) -> FNode:
        f = And(substitute_free_variables(transition.dst.clock_invariant),
                substitute_free_variables(self.build_clocks_assertion(clocks)))

        return f
    '''

    def calculate_max_time_step(self, transition: Transition, clocks: dict[str, float], time_step: float):
        k, v = transition.dst.get_min_clock_bound()

        if k is not None and v is not None:
            delta = v - clocks[k]
            time_step = time_step if delta <= 0 else min(time_step, delta)

        return time_step


    def check_sat(self):
        if not self.time_steps[-1] > 0.0:
            raise ValueError('Time step must be greater than zero.')

        primed_vars = {}
        primed_vars_mapping = {}
        for k, v in self.variables.items():
            k_ = substitute_free_variables(k)
            primed_vars[k_] = v[-1]
            primed_vars_mapping[k_] = k

        primed_vars_assert = self.build_variables_assertion(primed_vars)
        clocks_assert = self.build_clocks_assertion(self.clocks[-1])

        inputs = [v.phases[self.current_phases[-1][i]] for i, v in enumerate(self.peas)]

        # Check single elements
        inputs_ = []
        for input in inputs:
            input_ = []

            for e in input:

                updated_clocks = self.update_clocks(self.clocks[-1], e.resets, self.time_steps[-1])
                updated_clocks_assert = self.build_clocks_assertion(updated_clocks)

                sat = is_sat(And(e.guard, primed_vars_assert, clocks_assert), solver_name=SOLVER_NAME, logic=LOGIC) and \
                      is_sat(And(e.dst.clock_invariant, updated_clocks_assert), solver_name=SOLVER_NAME, logic=LOGIC)

                if sat:
                    input_.append(e)

            inputs_.append(input_)

        inputs = inputs_


        # Compute cartesian product with intermediate checks
        #results = []
        results: list[Simulator.SatResult] = []

        for e in inputs[0]:
            model = get_model(e.guard, solver_name=SOLVER_NAME, logic=LOGIC)
            values = model.get_values(primed_vars.keys())
            results.append(Simulator.SatResult((e,), {primed_vars_mapping[k]: v for k, v in values.items()}))
            print()

        for input in inputs[1:]:
            #results_ = []
            results_: list[Simulator.SatResult] = []

            for result in results:
                guards_pre = And(primed_vars_assert, clocks_assert)

                for r in result.transitions:
                    guards_pre = And(guards_pre, r.guard)

                for e in input:
                    guards = And(guards_pre, e.guard)

                    model = get_model(guards, solver_name=SOLVER_NAME, logic=LOGIC)

                    if model is not None:
                        values = model.get_values(primed_vars.keys())
                        result_ = Simulator.SatResult(result.transitions + (e,), {primed_vars_mapping[k]: v for k, v in values.items()})
                        results_.append(result_)

            results = results_

        self.sat_results = results









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
                        self.update_clocks(self.clocks[-1], transition.resets, self.time_steps[-1])))

            model = get_model(f, SOLVER_NAME, LOGIC)

            if model is not None:
                primed_variables = {substitute_free_variables(k): k for k in self.variables}
                model = model.get_values(primed_variables.keys())

                self.sat_results.append((transition_tuple, {v: model[k] for k, v in primed_variables.items()}))

    def step_next(self, enabled_transition_index: int) -> None:
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

        # TODO: fix scenario
        if self.scenario is not None and self.times[-1] in self.scenario.valuations:
            self.update_variables(self.scenario.valuations[self.times[-1]].values)
            self.time_steps[-1] = self.scenario.valuations[self.times[-1]].end - self.times[-1]

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
