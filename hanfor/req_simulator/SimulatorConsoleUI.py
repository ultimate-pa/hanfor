from __future__ import annotations

import os
import re as regex

from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.validator import PathValidator
from prompt_toolkit.validation import ValidationError, Validator
from pysmt.shortcuts import Symbol, Real, Int, Bool
from pysmt.typing import REAL, INT, BOOL

from req_simulator.countertrace import CountertraceTransformer
from req_simulator.phase_event_automaton import build_automaton
from req_simulator.simulator import Simulator
from req_simulator.utils import get_countertrace_parser


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
            print('clocks:', self.simulator.clocks[-1])
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
            self.simulator.step_next(transitions)
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
