from __future__ import annotations

import itertools
from collections import defaultdict

from pysmt.fnode import FNode
from pysmt.shortcuts import And, Equals, Symbol, Real, EqualsOrIff, TRUE, get_model
from pysmt.typing import REAL

from req_simulator.phase_event_automaton import PhaseEventAutomaton, Phase, Transition
from req_simulator.scenario import Scenario
from req_simulator.utils import substitute_free_variables, SOLVER_NAME, LOGIC
from reqtransformer import Requirement, Formalization


class Simulator:
    def __init__(self, peas: list[PhaseEventAutomaton], scenario: Scenario = None, name: str = 'unnamed') -> None:
        self.name: str = name
        self.scenario: Scenario = scenario

        self.times: list[float] = [0.0]  # history
        self.time_steps: list[float] = [1.0]  # history

        self.peas: list[PhaseEventAutomaton] = peas
        self.current_phases: list[list[Phase | None]] = [[None] * len(self.peas)]  # history
        self.clocks: list[list[dict[str, float]]] = [
            [{v: 0.0 for v in k.clocks} for k in self.peas]]  # history ? TODO: Geht ein globales clock set?
        self.enabled_transitions: list[tuple[tuple[Transition], dict[FNode, FNode]]] = []

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

    def get_active_dc_phases(self) -> list[str]:
        result = []

        if self.current_phases[-1][0] is None:
            return result

        for i, current_phase in enumerate(self.current_phases[-1]):
            pea = self.peas[i]
            result.extend([f'{pea.requirement.rid}_{pea.formalization.id}_{pea.countertrace_id}_{v}' for v in
                           current_phase.sets.active])

        return result

    def get_transitions(self):
        results = []

        for transition in self.enabled_transitions:
            model = ' ; '.join([f'{k} = {v}' for k, v in transition[1].items() if self.variables[k][-1] is None])
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

            # self.variables.update((k, v) for k, v in variables.items() if k in self.variables)

    def update_clocks(self, i: int, resets: frozenset[str], dry_run: bool = False) -> dict[str, float]:
        clocks = self.clocks[-1][i].copy()

        for k, v in clocks.items():
            clocks[k] = self.time_steps[-1] if k in resets else v + self.time_steps[-1]

        if not dry_run:
            self.clocks[-1][i] = clocks

        return clocks

    def build_var_assertions(self) -> FNode:
        return And(
            EqualsOrIff(substitute_free_variables(k), v[-1]) for k, v in self.variables.items() if v[-1] is not None)

    def build_clock_assertions(self, clocks: dict[str, float]) -> FNode:
        return And(Equals(Symbol(k, REAL), Real(v)) for k, v in clocks.items())

    def build_guard(self, transition: Transition, clocks: dict[str, float]) -> FNode:
        f = And(self.build_var_assertions(), transition.guard, self.build_clock_assertions(clocks))

        return f

    def build_clock_invariant(self, transition: Transition, clocks: dict[str, float]) -> FNode:
        f = And(substitute_free_variables(transition.dst.clock_invariant),
                substitute_free_variables(self.build_clock_assertions(clocks)))

        return f

    def calculate_max_time_step(self, transition: Transition, clocks: dict[str, float], time_step: float):
        k, v = transition.dst.get_min_clock_bound()

        if k is not None and v is not None:
            delta = v - clocks[k]
            time_step = time_step if delta <= 0 else min(time_step, delta)

        return time_step

    def check_sat(self) -> None:
        if not self.time_steps[-1] > 0.0:
            raise ValueError('Time step must be greater that zero.')

        self.enabled_transitions = []

        transition_lists = [self.peas[i].get_transitions(self.current_phases[-1][i]) for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

        time_step_max = self.time_steps[-1]
        for transition_tuple in transition_tuples:
            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                clock_bound = transition.dst.get_min_clock_bound()
                if clock_bound is not None:
                    delta = clock_bound[1] - self.clocks[-1][i][clock_bound[0]]
                    time_step_max = time_step_max if delta <= 0 else min(time_step_max, delta)

        self.time_steps[-1] = time_step_max

        for transition_tuple in transition_tuples:
            f = TRUE()

            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                # TODO: Can be split into two check sat, if it improves performance.
                # In this case, the substitution of clocks can be omitted.
                f = And(f, self.build_guard(transition, self.clocks[-1][i]),
                        self.build_clock_invariant(transition, self.update_clocks(i, transition.resets, True)))

            model = get_model(f, SOLVER_NAME, LOGIC)

            if model is not None:
                primed_variables = {substitute_free_variables(k): k for k in self.variables}
                model = model.get_values(primed_variables.keys())

                self.enabled_transitions.append((transition_tuple, {v: model[k] for k, v in primed_variables.items()}))

    def step_next(self, enabled_transition_index: int) -> None:
        transitions, model = self.enabled_transitions[enabled_transition_index]

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
            v[-1] = model[k]

        for i, transition in enumerate(transitions):
            self.current_phases[-1][i] = transition.dst
            self.update_clocks(i, transition.resets)

        self.enabled_transitions = []
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
