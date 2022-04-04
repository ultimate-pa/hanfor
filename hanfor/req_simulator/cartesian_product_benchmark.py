from __future__ import annotations

import inspect
import itertools
import time
from collections import defaultdict

from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, EqualsOrIff, Int, is_sat, And, TRUE
from pysmt.typing import INT

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer
from termcolor import colored

parser = boogie_parsing.get_parser_instance()
stats = defaultdict(dict)


def print_stats() -> None:
    min_duration = min([stats[s]['duration'] for s in stats])
    min_sat_duration = min([sum(stats[s]['check_sat_durations']) for s in stats])

    for s in stats:
        duration_color = 'green' if stats[s]["duration"] <= min_duration else 'white'
        check_sat_durations_color = 'green' if sum(stats[s]['check_sat_durations']) <= min_sat_duration else 'white'

        print(f'\n{s}:')
        print(colored(f'duration: {stats[s]["duration"]}', duration_color))
        print('result:', stats[s]['result'])
        print('result size:', f'{len(stats[s]["result"])}')
        print('check sat calls:', stats[s]['check_sat_calls'])
        print(colored(f'check sat duration: {sum(stats[s]["check_sat_durations"])}', check_sat_durations_color))
        print('check sat duration avg:', sum(stats[s]['check_sat_durations']) / len(stats[s]['check_sat_durations']))
        # print('check sat formulas:', stats[s]['check_sat_formulas'])

    print('\nresults are equal:',
          stats['naive']['result'] == stats['optimized_initial_checks']['result'] and
          stats['naive']['result'] == stats['optimized_intermediate_checks']['result'])


def get_caller_name() -> str:
    return inspect.stack()[2].function


def get_func_name() -> str:
    return inspect.stack()[1].function


def build_var_assertion(name: str, value: int):
    return EqualsOrIff(Symbol(name, INT), Int(value))


def build_var_assertions(name: str, values: tuple[int]):
    return And([build_var_assertion(name, v) for v in values])


def check_sat(formula: FNode) -> bool:
    caller = get_caller_name()

    check_sat_duration = time.time()
    result = is_sat(formula)
    check_sat_duration = time.time() - check_sat_duration

    stats[caller].setdefault('check_sat_calls', 0)
    stats[caller]['check_sat_calls'] += 1

    stats[caller].setdefault('check_sat_durations', [])
    stats[caller]['check_sat_durations'].append(check_sat_duration)

    stats[caller].setdefault('check_sat_formulas', [])
    stats[caller]['check_sat_formulas'].append(formula.simplify())

    return result


def naive(inputs: list[list[FNode]]) -> list[tuple[FNode]]:
    results = []

    # Compute cartesian product
    results_ = list(itertools.product(*inputs))

    # Check result tuples
    for result_ in results_:
        formula = TRUE()

        for r_ in result_:
            formula = And(formula, r_)

        if check_sat(formula):
            results.append(result_)

    return results


def optimized_initial_checks(inputs: list[list[FNode]]) -> list[tuple[FNode]]:
    results = []

    # Check single elements
    inputs_ = []
    for input in inputs:
        input_ = []

        for e in input:
            if check_sat(e):
                input_.append(e)

        inputs_.append(input_)

    inputs = inputs

    # Compute cartesian product
    results_ = list(itertools.product(*inputs))

    # Check result tuples
    for result_ in results_:
        formula = TRUE()

        for r_ in result_:
            formula = And(formula, r_)

        if check_sat(formula):
            results.append(result_)

    return results


def optimized_intermediate_checks(inputs: list[list[FNode]]) -> list[tuple[FNode]]:
    results = []

    if [] in inputs:
        return results

    # Check single elements
    inputs_ = []
    for input in inputs:
        input_ = []

        for e in input:
            if check_sat(e):
                input_.append(e)

        inputs_.append(input_)

    inputs = inputs

    # Compute cartesian product with intermediate checks
    for e in inputs[0]:
        results.append((e,))

    for input in inputs[1:]:
        results_ = []

        for result in results:
            formula = And(*result)

            for e in input:
                if check_sat(And(formula, e)):
                    result_ = result + (e,)
                    results_.append(result_)

        results = results_

    return results


def main():
    inputs = [
        ['true', 'true'],
        ['true', 'true']
    ]

    variables = {
        'a': 'int',
        'b': 'int'
    }

    inputs = parse_inputs(inputs, variables)

    duration = time.time()
    stats['naive']['result'] = naive(inputs)
    stats['naive']['duration'] = time.time() - duration

    duration = time.time()
    stats['optimized_initial_checks']['result'] = optimized_initial_checks(inputs)
    stats['optimized_initial_checks']['duration'] = time.time() - duration

    duration = time.time()
    stats['optimized_intermediate_checks']['result'] = optimized_intermediate_checks(inputs)
    stats['optimized_intermediate_checks']['duration'] = time.time() - duration

    print_stats()


def parse_inputs(inputs: list[list[str]], variables: dict[str, str]) -> list[list[FNode]]:
    results = []

    for input in inputs:
        result = []

        for e in input:
            lark_tree = parser.parse(e)
            result.append(BoogiePysmtTransformer(variables).transform(lark_tree))

        results.append(result)

    return results


if __name__ == '__main__':
    main()
