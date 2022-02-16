from __future__ import annotations

import itertools
from dataclasses import dataclass

import regex
from InquirerPy import inquirer
from InquirerPy.base import Choice
from lark.lark import Lark
from prompt_toolkit.validation import ValidationError, Validator
from pysmt.fnode import FNode
from pysmt.shortcuts import get_free_variables, And, Iff, Equals, Symbol, is_sat, FALSE, TRUE, Real, substitute
from pysmt.typing import REAL

from tests.test_simulator.test_counter_trace import testcases
from .counter_trace import CounterTrace, CounterTraceTransformer
from .phase_event_automaton import PhaseEventAutomaton, build_automaton, Phase

parser = Lark.open('counter_trace_grammar.lark', rel_to=__file__, start='counter_trace', parser='lalr')


class BoolValidator(Validator):
    def validate(self, document):
        ok = regex.match('^(0|1)$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid boolean value.',
                cursor_position=len(document.text))


class TimeStepValidator(Validator):
    def validate(self, document):
        ok = regex.match('^(\d*.?\d+(?<=[1-9]))$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid time step value.',
                cursor_position=len(document.text))


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
        self.current_phases: list[Phase] = [None for i in self.peas]

        self.clocks: list[dict[str, float]] = [{clock: 0 for clock in pea.clocks} for pea in self.peas]

        self.variables: dict[FNode, FNode] = self.get_variables()
        self.time_step: float = 1.0

        self.save_points: list[SavePoint] = []
        self.create_save_point()

    def get_variables(self) -> dict[FNode, FNode]:
        variables = {}
        for ct in self.cts:
            for dc_phase in ct.dc_phases:
                for variable in get_free_variables(dc_phase.invariant):
                    variables[Symbol(variable.symbol_name() + '_', variable.symbol_type())] = TRUE()
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

    def substitute_free_variables(self, fnode: FNode, suffix: str = "_"):
        symbols = fnode.get_free_variables()
        subs = {s: Symbol(s.symbol_name() + suffix, s.symbol_type()) for s in symbols}
        result = substitute(fnode, subs)
        return result

    def build_var_assertions(self) -> FNode:
        return And(Iff(k, v) for k, v in self.variables.items())

    def build_clock_assertions(self, clocks: dict[str, float]) -> FNode:
        return And(Equals(Symbol(k, REAL), Real(v)) for k, v in clocks.items())

    def check_sat(self):
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
                        self.substitute_free_variables(transition.dst.clock_invariant),
                        self.substitute_free_variables(self.build_clock_assertions(clocks))).simplify()

            sat = is_sat(f)
            print('{x:<8}'.format(x='sat:' if sat else 'unsat:'), f)

            if sat:
                enabled_transitions.append(transition_tuple)

        return enabled_transitions


def main() -> int:
    expressions, ct_str, _ = testcases['response_delay_globally']
    expressions['T'] = Real(5)

    # ct0 = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
    # pea0 = build_automaton(ct0, 'c0_')
    # ct1 = CounterTraceTransformer(expressions).transform(parser.parse(ct_str))
    # pea1 = build_automaton(ct0, 'c1_')

    cts, peas = [], []
    for i in range(100):
        cts.append(CounterTraceTransformer(expressions).transform(parser.parse(ct_str)))
        peas.append(build_automaton(cts[-1], f"c{i}_"))

    simulator = Simulator(cts, peas)
    # simulator = Simulator([ct0, ct1], [pea0, pea1])

    while (True):
        print('\n---')
        for i in range(len(simulator.peas)):
            print('phase:', {} if simulator.current_phases[i] is None else simulator.current_phases[i].sets,
                  '| counter trace:', simulator.cts[i], )
        print('clocks:', simulator.clocks, '\n')

        for k, v in simulator.variables.items():
            print('%s: %s' % (k, v))
        print('time step:', simulator.time_step, '\n')

        action = inquirer.select(
            message='Choose an action.',
            choices=[
                Choice(0, 'Continue simulation'),
                Choice(1, 'Change variable'),
                Choice(2, 'Change time step'),
                Choice(3, 'Go back', enabled=False),
                Choice(4, 'Exit')
            ]
        ).execute()

        if action == 4:
            return 0

        if action == 3:
            simulator.remove_last_save_point()

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
                validate=BoolValidator(),
            ).execute()

            simulator.variables[variable] = TRUE() if value == '1' else FALSE()

        if action == 0:
            transitions = simulator.check_sat()

            transition_tuple = inquirer.select(
                message='Choose a transition.',
                choices=[
                    *transitions,
                    Choice(None, 'Exit')
                ],
                default=0
            ).execute()

            if transition_tuple:
                for i in range(len(transition_tuple)):
                    simulator.current_phases[i] = transition_tuple[i].dst
                    simulator.update_clocks(i, transition_tuple[i].resets)

                simulator.create_save_point()
            else:
                return 0


if __name__ == '__main__':
    main()
