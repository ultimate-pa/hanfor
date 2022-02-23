from __future__ import annotations

import itertools
import os
from dataclasses import dataclass

import regex
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.validator import PathValidator
from lark.lark import Lark
from prompt_toolkit.validation import ValidationError, Validator
from pysmt.fnode import FNode
from pysmt.shortcuts import get_free_variables, And, Iff, Equals, Symbol, is_sat, Real, Int, Bool
from pysmt.typing import REAL, INT, BOOL

from req_simulator.Scenario import Scenario
from req_simulator.counter_trace import CounterTrace, CounterTraceTransformer
from req_simulator.phase_event_automaton import PhaseEventAutomaton, build_automaton, Phase, Transition
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


@dataclass(frozen=True)
class SavePoint:
    current_phases: list[Phase]
    clocks: list[dict[str, float]]
    variables: dict[FNode, FNode]
    time_step: float


class Simulator:
    def __init__(self, cts: list[CounterTrace], peas: list[PhaseEventAutomaton]) -> None:
        self.cts: list[CounterTrace] = cts
        self.peas: list[PhaseEventAutomaton] = peas
        self.scenario: Scenario = None
        self.reset()

    def reset(self):
        self.current_phases: list[Phase] = [None] * len(self.peas)
        self.clocks: list[dict[str, float]] = [{clock: 0 for clock in pea.clocks} for pea in self.peas]
        self.variables: dict[FNode, FNode] = self.extract_variables_from_ct()
        self.time_step: float = 1.0
        self.time: float = 0.0
        self.save_points: list[SavePoint] = []
        self.create_save_point()

    def set_scenario(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self.reset()
        self.update_variables(self.scenario.values[self.time])

        if self.scenario is not None:
            if self.time in self.scenario.values:
                keys = list(self.scenario.values)
                index = keys.index(self.time)
                next_time = keys[index + 1] if index + 1 < len(keys) else 0
                self.time_step = abs(next_time - self.time)

    def load_scenario_from_file(self, path: str) -> None:
        self.set_scenario(Scenario.load_from_file(path))

    def save_scenario_to_file(self, path: str) -> None:
        Scenario.save_to_file(self.scenario, path)

    def update_variables(self, variables: dict[FNode, FNode]) -> None:
        for k, v in variables.items():
            if k in self.variables:
                self.variables[k] = v

    def extract_variables_from_ct(self) -> dict[FNode, FNode]:
        variables = {}
        for ct in self.cts:
            for dc_phase in ct.dc_phases:
                for variable in get_free_variables(dc_phase.invariant):
                    variables[variable] = None
                    # variables[Symbol(variable.symbol_name() + '_', variable.symbol_type())] = TRUE()
        return variables

    def create_save_point(self) -> None:
        self.save_points.append(SavePoint(
            self.current_phases.copy(), self.clocks.copy(), self.variables.copy(), self.time_step))

    def remove_last_save_point(self) -> None:
        if len(self.save_points) < 2:
            return

        self.save_points.pop()
        self.current_phases = self.save_points[-1].current_phases.copy()
        self.clocks = self.save_points[-1].clocks.copy()
        self.variables = self.save_points[-1].variables.copy()
        self.time_step = self.save_points[-1].time_step

    def update_clocks(self, i: int, resets: frozenset[str], dry_run: bool = False) -> dict[str, float]:
        clocks = self.clocks[i].copy()

        for k, v in clocks.items():
            clocks[k] = self.time_step if k in resets else v + self.time_step

        if not dry_run:
            self.clocks[i] = clocks

        return clocks

    def build_var_assertions(self) -> FNode:
        return And(Iff(substitute_free_variables(k), v) for k, v in self.variables.items() if v is not None)

    def build_clock_assertions(self, clocks: dict[str, float]) -> FNode:
        return And(Equals(Symbol(k, REAL), Real(v)) for k, v in clocks.items())

    def check_sat(self) -> list[tuple[Transition]]:
        enabled_transitions = []
        var_assertions = self.build_var_assertions()

        transition_lists = [[t for t in self.peas[i].phases[self.current_phases[i]]] for i in range(len(self.peas))]
        transition_tuples = list(itertools.product(*transition_lists))

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

        self.create_save_point()
        self.time += self.time_step

        if self.scenario is not None:
            if self.time in self.scenario.values:
                self.update_variables(self.scenario.values[self.time])

                keys = list(self.scenario.values)
                index = keys.index(self.time)
                next_time = keys[index + 1] if index + 1 < len(keys) else 0
                self.time_step = abs(next_time - self.time)


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

    # ct0 = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
    # pea0 = build_automaton(ct0, 'c0_')
    # ct1 = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
    # pea1 = build_automaton(ct0, 'c1_')

    cts, peas = [], []
    for i in range(2):
        cts.append(CounterTraceTransformer(expressions).transform(parser.parse(ct_str)))
        peas.append(build_automaton(cts[-1], f"c{i}_"))

    simulator = Simulator(cts, peas)

    while True:
        print('\n---')
        for i in range(len(simulator.peas)):
            print('phase:', {} if simulator.current_phases[i] is None else simulator.current_phases[i].sets,
                  '| counter trace:', simulator.cts[i], )
        print('clocks:', simulator.clocks, '\n')

        for k, v in simulator.variables.items():
            print('%s (%s): %s' % (k, k.symbol_type(), v))
        print('time step:', simulator.time_step, '\n')

        action = inquirer.select(
            message='Choose an action.',
            choices=[
                Choice(0, 'Continue simulation'),
                Choice(1, 'Change variable'),
                Choice(2, 'Change time step'),
                Choice(3, 'Load scenario'),
                Choice(4, 'Save scenario'),
                Choice(5, 'Go back'),
                Choice(6, 'Exit')
            ]
        ).execute()

        if action == 6:
            return 0

        if action == 5:
            simulator.remove_last_save_point()

        if action == 4:
            home_path = "/" if os.name == "posix" else "C:\\"
            path = inquirer.filepath(
                message="Enter path to save:",
                default=home_path,
            ).execute()

            simulator.save_scenario_to_file(path)

        if action == 3:
            home_path = "/" if os.name == "posix" else "C:\\"
            path = inquirer.filepath(
                message="Enter file to load:",
                default=home_path,
                validate=PathValidator(is_file=True, message='Input is not a valid file'),
            ).execute()

            simulator.load_scenario_from_file(path)

        if action == 2:
            time_step = inquirer.text(
                message='Enter a value.',
                validate=TimeStepValidator(),
            ).execute()

            simulator.time_step = float(time_step)

        if action == 1:
            variable = inquirer.select(
                message='Choose a variable.',
                choices=simulator.variables
            ).execute()

            value = inquirer.text(
                message='Enter a value.',
                filter=lambda result:
                Bool(bool(int(result))) if variable.symbol_type() is BOOL else \
                    Int(int(result)) if variable.symbol_type() is INT else Real(float(result)),
                validate=type_validator_mapping[variable.symbol_type()],
            ).execute()

            simulator.variables[variable] = value

        if action == 0:
            enabled_transitions = simulator.check_sat()

            transitions = inquirer.select(
                message='Choose a transition.',
                choices=[
                    *enabled_transitions,
                    Choice(None, 'Exit')
                ],
                default=0
            ).execute()

            if transitions:
                simulator.walk_transitions(transitions)
            else:
                return 0


if __name__ == '__main__':
    main()
