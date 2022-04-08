from __future__ import annotations

import itertools
import os
import re as regex
from collections import defaultdict
from copy import copy
from dataclasses import dataclass

from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.validator import PathValidator
from prompt_toolkit.validation import ValidationError, Validator
from pysmt.fnode import FNode
from pysmt.shortcuts import And, Equals, Symbol, is_sat, Real, Int, Bool, EqualsOrIff, TRUE, get_model
from pysmt.typing import REAL, INT, BOOL

from req_simulator.countertrace import CountertraceTransformer
from req_simulator.phase_event_automaton import PhaseEventAutomaton, build_automaton, Phase, Transition
from req_simulator.scenario import Scenario
from req_simulator.utils import substitute_free_variables, get_countertrace_parser, SOLVER_NAME, LOGIC
from reqtransformer import Requirement, Formalization


class BoolValidator(Validator):
    def validate(self, document):
        ok = regex.match(r'^(0|1)$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid boolean value.',
                cursor_position=len(document.text))


class IntValidator(Validator):
    def validate(self, document):
        ok = regex.match(r'^[+-]?\d+$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid integer value.',
                cursor_position=len(document.text))


class RealValidator(Validator):
    def validate(self, document):
        ok = regex.match(r'^[+-]?\d*[.]?\d+$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid real value.',
                cursor_position=len(document.text))


class TimeStepValidator(Validator):
    def validate(self, document):
        ok = regex.match(r'^[+]?\d*[.]?\d+(?<=[1-9])$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid time step value.',
                cursor_position=len(document.text))


type_validator_mapping = {
    BOOL: BoolValidator(),
    INT: IntValidator(),
    REAL: RealValidator()
}


class Simulator:
    @dataclass
    class State:
        clocks: list[dict[str, float]]

    def __init__(self, peas: list[PhaseEventAutomaton], scenario: Scenario = None, name: str = 'unnamed') -> None:
        self.name: str = name
        self.scenario: Scenario = scenario

        self.times: list[float] = [0.0]
        self.time_steps: list[float] = [1.0]

        self.peas: list[PhaseEventAutomaton] = peas
        self.current_phases: list[list[Phase | None]] = [[None] * len(self.peas)]
        self.clocks: list[dict[str, float]] = [{clock: 0.0 for clock in pea.clocks} for pea in self.peas]
        self.enabled_transitions: list[tuple] = []

        self.variables: dict[FNode, list[FNode | None]] = \
            {v: [None] for p in self.peas for v in p.countertrace.extract_variables()}
        self.models: dict[FNode, list[FNode | None]] = {k: [None] for k in self.variables}

        if self.scenario is not None:
            self.time_steps[-1] = self.scenario.valuations[0.0].get_duration()
            self.update_variables()

        self.states: list[Simulator.State] = []
        self.save_state()

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
            results.append(
                ' ; '.join([f'{k} = {v}' for k, v in transition[1].items() if self.variables[k][-1] is None]))

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

    def save_state(self) -> None:
        self.states.append(Simulator.State(copy(self.clocks)))

    def load_prev_state(self) -> bool:
        if len(self.states) < 2:
            return False

        self.states.pop()
        self.clocks = copy(self.states[-1].clocks)

        for k, v in self.models.items():
            v.pop()

        return True

    def update_clocks(self, i: int, resets: frozenset[str], dry_run: bool = False) -> dict[str, float]:
        clocks = self.clocks[i].copy()

        for k, v in clocks.items():
            clocks[k] = self.time_steps[-1] if k in resets else v + self.time_steps[-1]

        if not dry_run:
            self.clocks[i] = clocks

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
        enabled_transitions = []

        transition_lists = [self.peas[i].get_transitions(self.current_phases[-1][i]) for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

        time_step_max = self.time_steps[-1]
        for transition_tuple in transition_tuples:
            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                clock_bound = transition.dst.get_min_clock_bound()
                if clock_bound is not None:
                    delta = clock_bound[1] - self.clocks[i][clock_bound[0]]
                    time_step_max = time_step_max if delta <= 0 else min(time_step_max, delta)

        self.time_steps[-1] = time_step_max

        for transition_tuple in transition_tuples:
            f = TRUE()

            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                # TODO: Can be split into two check sat, if it improves performance.
                # In this case, the substitution of clocks can be omitted.
                f = And(f, self.build_guard(transition, self.clocks[i]),
                        self.build_clock_invariant(transition, self.update_clocks(i, transition.resets, True)))

            model = get_model(f, SOLVER_NAME, LOGIC)

            if model is not None:
                variable_mapping = {substitute_free_variables(k): k for k in self.variables}
                partial = model.get_values(variable_mapping.keys())

                enabled_transitions.append((transition_tuple, {v: partial[k] for k, v in variable_mapping.items()}))

        self.enabled_transitions = enabled_transitions

    def check_sat_old(self) -> list[tuple[Transition]]:
        enabled_transitions = []
        var_assertions = self.build_var_assertions()

        transition_lists = [self.peas[i].get_transitions(self.current_phases[-1][i]) for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

        time_step_max = self.time_steps[-1]
        for transition_tuple in transition_tuples:
            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]
                for k, v in transition.dst.get_clock_bounds().items():
                    delta = v - self.clocks[i][k]
                    if delta > 0:
                        time_step_max = min(time_step_max, delta)
        self.time_steps[-1] = time_step_max
        print()

        for transition_tuple in transition_tuples:
            f = var_assertions

            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                clocks = self.update_clocks(i, transition.resets, True)

                f = And(f, transition.guard, self.build_clock_assertions(self.clocks[i]),
                        substitute_free_variables(transition.dst.clock_invariant),
                        substitute_free_variables(self.build_clock_assertions(clocks))).simplify()

            sat = is_sat(f, SOLVER_NAME)
            print('{x:<8}'.format(x='sat:' if sat else 'unsat:'), f)

            if sat:
                enabled_transitions.append(transition_tuple)

        self.enabled_transitions = enabled_transitions

        return enabled_transitions

    def walk_transitions(self, transitions: tuple[Transition], model: dict[FNode, FNode]):
        for i in range(len(transitions)):
            self.current_phases[-1][i] = transitions[i].dst
            self.update_clocks(i, transitions[i].resets)

        self.times[-1] += self.time_steps[-1]

        # TODO: fix scenario
        if self.scenario is not None and self.times[-1] in self.scenario.valuations:
            self.update_variables(self.scenario.valuations[self.times[-1]].values)
            self.time_steps[-1] = self.scenario.valuations[self.times[-1]].end - self.times[-1]

        for k, v in model.items():
            self.models[k].append(v)

        for k, v in self.variables.items():
            self.variables[k].append(self.variables[k][-1])

        self.save_state()


class TUI:
    def __init__(self, simulator: Simulator):
        self.simulator = simulator

    def simulate(self):
        while True:
            print('\n---')
            for i in range(len(self.simulator.peas)):
                print('phase:',
                      {} if self.simulator.current_phases[-1][i] is None else self.simulator.current_phases[-1][i].sets,
                      '| counter trace:', self.simulator.peas[i].countertrace, )
            print('clocks:', self.simulator.clocks)
            print('time:', self.simulator.times[-1], '\n')

            for k, v in self.simulator.variables.items():
                print('%s (%s): %s' % (k, k.symbol_type(), v[-1]))
            print('time step:', self.simulator.time_steps[-1], '\n')

            action = inquirer.select(
                message='Choose an action.',
                choices=[
                    Choice('Continue simulation'),
                    Choice('Change variable'),
                    Choice('Change time step'),
                    Choice('Load scenario'),
                    Choice('Save scenario'),
                    Choice('Go back'),
                    Choice('Exit')
                ]
            ).execute()

            if action == 'Continue simulation':
                self.continue_simulation()

            if action == 'Change variable':
                self.change_variable()

            if action == 'Change time step':
                self.change_timestep()

            if action == 'Load scenario':
                self.load_scenario()

            if action == 'Save scenario':
                self.save_scenario()

            if action == 'Go back':
                self.go_back()

            if action == 'Exit':
                self.exit()

    def continue_simulation(self):
        enabled_transitions = self.simulator.check_sat()

        transitions = inquirer.select(
            message='Choose a transition.',
            choices=[
                *enabled_transitions,
                Choice(None, 'Exit')
            ],
            default=0
        ).execute()

        if transitions:
            self.simulator.walk_transitions(transitions)
        else:
            return 0

    def change_variable(self):
        variable = inquirer.select(
            message='Choose a variable.',
            choices=self.simulator.variables
        ).execute()

        value = inquirer.text(
            message='Enter a value.',
            filter=lambda result:
            Bool(bool(int(result))) if variable.symbol_type() is BOOL else \
                Int(int(result)) if variable.symbol_type() is INT else Real(float(result)),
            validate=type_validator_mapping[variable.symbol_type()],
        ).execute()

        self.simulator.variables[variable] = value

    def change_timestep(self):
        time_step = inquirer.text(
            message='Enter a value.',
            validate=RealValidator(),
        ).execute()

        self.simulator.time_steps[-1] = float(time_step)

    def load_scenario(self):
        home_path = "/" if os.name == "posix" else "C:\\"
        path = inquirer.filepath(
            message="Enter file to load:",
            default=home_path,
            validate=PathValidator(is_file=True, message='Input is not a valid file'),
        ).execute()

        self.simulator = Simulator.load_scenario_from_file(self.simulator, path)

    def save_scenario(self):
        home_path = "/" if os.name == "posix" else "C:\\"
        path = inquirer.filepath(
            message="Enter path to save:",
            default=home_path,
        ).execute()

        self.simulator.save_scenario_to_file(path)

    def go_back(self):
        self.simulator.load_prev_state()

    def exit(self):
        exit()


def main() -> int:
    testcases = {
        'response_delay_globally':
            ({'R': Symbol('R'), 'S': Symbol('S'), 'T': Symbol('T', REAL)},
             'true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true',
             'True;⌈(R & (! S))⌉;⌈(! S)⌉ ∧ ℓ > T;True')}

    expressions, ct_str, _ = testcases['response_delay_globally']
    expressions['T'] = Real(5)

    ct0 = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
    pea0 = build_automaton(ct0, 'c0_')
    expressions['T'] = Real(10)
    ct1 = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
    pea1 = build_automaton(ct0, 'c1_')

    simulator = Simulator([pea0, pea1])
    tui = TUI(simulator)
    tui.simulate()


if __name__ == '__main__':
    main()
