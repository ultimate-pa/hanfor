from __future__ import annotations

import itertools
import os
from copy import copy
from dataclasses import dataclass

import regex
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.validator import PathValidator
from lark.lark import Lark
from prompt_toolkit.validation import ValidationError, Validator
from pysmt.fnode import FNode
from pysmt.shortcuts import And, Equals, Symbol, is_sat, Real, Int, Bool, EqualsOrIff
from pysmt.typing import REAL, INT, BOOL

from req_simulator.counter_trace import CounterTraceTransformer
from req_simulator.phase_event_automaton import PhaseEventAutomaton, build_automaton, Phase, Transition
from req_simulator.scenario import Scenario
from req_simulator.utils import substitute_free_variables

parser = Lark.open('counter_trace_grammar.lark', rel_to=__file__, start='counter_trace', parser='lalr')


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
        time: float
        current_phases: list[Phase]
        clocks: list[dict[str, float]]
        variables: dict[FNode, FNode]
        time_step: float

    def __init__(self, peas: list[PhaseEventAutomaton], scenario: Scenario = None, name: str = 'unnamed') -> None:
        self.name: str = name
        self.peas: list[PhaseEventAutomaton] = peas
        self.scenario: Scenario = scenario

        self.time: float = 0.0
        self.current_phases: list[Phase] = [None] * len(self.peas)
        self.clocks: list[dict[str, float]] = [{clock: 0 for clock in pea.clocks} for pea in self.peas]

        self.variables: dict[FNode, FNode] = {v: None for pea in self.peas for v in pea.counter_trace.extract_variables()}
        self.time_step: float = 1.0

        if self.scenario is not None:
            self.time_step = self.scenario.valuations[0.0].get_duration()
            self.update_variables()

        self.states: list[Simulator.State] = []
        self.save_state()

    @staticmethod
    def load_scenario_from_file(simulator: Simulator, path: str) -> Simulator:
        return Simulator(simulator.peas, Scenario.load_from_file(path))

    def save_scenario_to_file(self, path: str) -> None:
        Scenario.save_to_file(self.scenario, path)

    def update_variables(self, variables: dict[FNode, FNode] = None) -> None:
        if variables is None and self.scenario is not None:
            variables = self.scenario.valuations.get(self.time).values

        if variables is not None:
            self.variables.update((k, v) for k, v in variables.items() if k in self.variables)

    def save_state(self) -> None:
        self.states.append(Simulator.State(
            self.time, copy(self.current_phases), copy(self.clocks), copy(self.variables), self.time_step))

    def load_prev_state(self) -> None:
        if len(self.states) < 2:
            return

        self.states.pop()
        self.time = self.states[-1].time
        self.current_phases = copy(self.states[-1].current_phases)
        self.clocks = copy(self.states[-1].clocks)
        self.variables = copy(self.states[-1].variables)
        self.time_step = self.states[-1].time_step

    def update_clocks(self, i: int, resets: frozenset[str], dry_run: bool = False) -> dict[str, float]:
        clocks = self.clocks[i].copy()

        for k, v in clocks.items():
            clocks[k] = self.time_step if k in resets else v + self.time_step

        if not dry_run:
            self.clocks[i] = clocks

        return clocks

    def build_var_assertions(self) -> FNode:
        return And(EqualsOrIff(substitute_free_variables(k), v) for k, v in self.variables.items() if v is not None)

    def build_clock_assertions(self, clocks: dict[str, float]) -> FNode:
        return And(Equals(Symbol(k, REAL), Real(v)) for k, v in clocks.items())

    def check_guard(self, transition: Transition, clocks: dict[str, float]) -> bool:
        f = And(self.build_var_assertions(), transition.guard, self.build_clock_assertions(clocks))

        return is_sat(f)

    def check_clock_invariant(self, transition: Transition, clocks: dict[str, float]) -> bool:
        f = And(substitute_free_variables(transition.dst.clock_invariant),
                substitute_free_variables(self.build_clock_assertions(clocks)))

        return is_sat(f)

    def calculate_max_time_step(self, transition: Transition, clocks: dict[str, float], time_step: float):
        k, v = transition.dst.get_min_clock_bound()

        if k is not None and v is not None:
            delta = v - clocks[k]
            time_step = time_step if delta <= 0 else min(time_step, delta)

        return time_step

    def check_sat(self) -> list[tuple[Transition]]:
        enabled_transitions = []

        transition_lists = [self.peas[i].get_transitions(self.current_phases[i]) for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

        time_step_max = self.time_step
        for transition_tuple in transition_tuples:
            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                clock_bound = transition.dst.get_min_clock_bound()
                if clock_bound is not None:
                    delta = clock_bound[1] - self.clocks[i][clock_bound[0]]
                    time_step_max = time_step_max if delta <= 0 else min(time_step_max, delta)

        self.time_step = time_step_max

        for transition_tuple in transition_tuples:
            is_enabled = len(transition_tuple) > 0

            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                is_enabled = is_enabled and \
                             self.check_guard(transition, self.clocks[i]) and \
                             self.check_clock_invariant(transition, self.update_clocks(i, transition.resets, True))

            if is_enabled:
                enabled_transitions.append(transition_tuple)

        return enabled_transitions

    def check_sat_old(self) -> list[tuple[Transition]]:
        enabled_transitions = []
        var_assertions = self.build_var_assertions()

        transition_lists = [self.peas[i].get_transitions(self.current_phases[i]) for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

        time_step_max = self.time_step
        for transition_tuple in transition_tuples:
            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]
                for k, v in transition.dst.get_clock_bounds().items():
                    delta = v - self.clocks[i][k]
                    if delta > 0:
                        time_step_max = min(time_step_max, delta)
        self.time_step = time_step_max
        print()

        for transition_tuple in transition_tuples:
            f = var_assertions

            for i in range(len(transition_tuple)):
                transition = transition_tuple[i]

                clocks = self.update_clocks(i, transition.resets, True)

                f = And(f, transition.guard, self.build_clock_assertions(self.clocks[i]),
                        substitute_free_variables(transition.dst.clock_invariant),
                        substitute_free_variables(self.build_clock_assertions(clocks))).simplify()

            sat = is_sat(f)
            print('{x:<8}'.format(x='sat:' if sat else 'unsat:'), f)

            if sat:
                enabled_transitions.append(transition_tuple)

        return enabled_transitions

    def walk_transitions(self, transitions: tuple[Transition]):
        for i in range(len(transitions)):
            self.current_phases[i] = transitions[i].dst
            self.update_clocks(i, transitions[i].resets)

        self.time += self.time_step

        if self.scenario is not None and self.time in self.scenario.valuations:
            self.update_variables(self.scenario.valuations[self.time].values)
            self.time_step = self.scenario.valuations[self.time].end - self.time

        self.save_state()


class TUI:
    def __init__(self, simulator: Simulator):
        self.simulator = simulator

    def simulate(self):
        while True:
            print('\n---')
            for i in range(len(self.simulator.peas)):
                print('phase:',
                      {} if self.simulator.current_phases[i] is None else self.simulator.current_phases[i].sets,
                      '| counter trace:', self.simulator.peas[i].counter_trace, )
            print('clocks:', self.simulator.clocks)
            print('time:', self.simulator.time, '\n')

            for k, v in self.simulator.variables.items():
                print('%s (%s): %s' % (k, k.symbol_type(), v))
            print('time step:', self.simulator.time_step, '\n')

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

        self.simulator.time_step = float(time_step)

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
    # expressions['R'] = GT(Symbol('counter', INT), Int(5))
    # expressions['S'] = Iff(Symbol('is_active'), TRUE())
    expressions['T'] = Real(5)

    ct0 = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
    pea0 = build_automaton(ct0, 'c0_')
    expressions['T'] = Real(10)
    ct1 = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
    pea1 = build_automaton(ct0, 'c1_')

    # cts, peas = [], []
    # for i in range(2):
    #    cts.append(CounterTraceTransformer(expressions).transform(parser.parse(ct_str)))
    #    peas.append(build_automaton(cts[-1], f"c{i}_"))

    simulator = Simulator([pea0, pea1])
    tui = TUI(simulator)
    tui.simulate()

    # phase = list(peas[0].phases.keys())[1]
    # a = phase.get_clock_bounds()
    # print()


if __name__ == '__main__':
    main()
