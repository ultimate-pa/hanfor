from pysmt.fnode import FNode
from pysmt.shortcuts import get_free_variables, FALSE, TRUE, And, is_sat, Iff, Symbol, Int, Equals
from pysmt.typing import BOOL, INT

from simulator.counter_trace import CounterTrace
from simulator.phase_event_automaton import PhaseEventAutomaton, Phase


class Simulator:
    def __init__(self, ct: CounterTrace, pea: PhaseEventAutomaton) -> None:
        self.current_phase: Phase = None
        self.ct: CounterTrace = ct
        self.pea: PhaseEventAutomaton = pea
        self.clocks: dict[str, int] = {'c' + str(i): 0 for i in range(len(ct.dc_phases))}


    def get_variables(self):
        variables = set()
        for transition in self.pea.phases[self.current_phase]:
            variables |= get_free_variables(transition.guard)

        return list(variables)

    def choice(self, choices):
        while True:
            for i in range(len(choices)):
                print('%d: %s' % (i, choices[i]))

            print('[Choice or enter]: ', end='')
            user_input = input()

            if len(user_input) == 0:
                return None

            try:
                i = int(user_input)
                _ = choices[i]
                return i
            except:
                print('Illegal input `%s`. Choose again.' % user_input)
                print()
                continue

    def choice_value(self, variable):
        while True:
            print('[Enter new value]: ', end='')
            user_input = input()

            try:
                i = int(user_input)
            except:
                print('Illegal input `%s`. Try again.' % user_input)
                print()
                continue

            if isinstance(variable, FNode) and variable.is_symbol(BOOL) and i == 0:
                return FALSE()

            if isinstance(variable, FNode) and variable.is_symbol(BOOL) and i == 1:
                return TRUE()

            if isinstance(variable, int):
                return i

            print('Illegal input `%s`. Try again.' % user_input)

    def simulate(self):
        variables = {i: None for i in self.get_variables()}
        t = 1
        time = 0

        while True:
            while True:
                print('---')
                print('counter trace:', self.ct)
                print('sets:', {} if self.current_phase is None else self.current_phase.sets)
                print('clocks:', self.clocks)
                print('time:', time)
                print()

                i = self.choice(['%s = %s' % (k, v) for k, v in variables.items()] + ['t = %d' % t])

                if i == None:
                    break

                if i == len(variables.keys()):
                    t = self.choice_value(t)
                else:
                    variable = list(variables.keys())[i]
                    value = self.choice_value(variable)
                    variables[variable] = value

            print('---')
            print('counter trace:', self.ct)
            print('sets:', {} if self.current_phase is None else self.current_phase.sets)
            print()

            transitions = []
            for transition in self.pea.phases[self.current_phase]:
                clocks = self.clocks.copy()
                for clock in clocks:
                    clocks[clock] = 0 if transition.src is None or clock in transition.resets else clocks[clock]

                f = And(transition.guard, *[Iff(k, v) for k, v in variables.items()],
                        *[Equals(Symbol(k, INT), Int(v)) for k, v in clocks.items()])
                sat_f = is_sat(f)
                print('Check sat `%s`: %s' % (f, sat_f))

                g = And(transition.dst.clock_invariant,
                        *[Equals(Symbol(k, INT), Int(v + t)) for k, v in clocks.items()])
                sat_g = is_sat(g)
                print('Check sat `%s`: %s' % (g, sat_g))

                if sat_f and sat_g:
                    transitions.append(transition)
            print()

            i = self.choice([i.guard for i in transitions])
            transition = transitions[i]
            self.current_phase = transition.dst
            time += t
            for clock in self.clocks:
                self.clocks[clock] = 0 + t if transition.src is None or clock in transition.resets else self.clocks[clock] + t