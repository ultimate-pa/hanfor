from __future__ import annotations

import inspect
import itertools
import time
from collections import defaultdict

from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, Int, is_sat, And, TRUE, LT, GT
from pysmt.typing import INT
from termcolor import colored

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer
from reqtransformer import Variable

SOLVER_NAME = 'z3'
LOGIC = 'QF_LRA'
parser = boogie_parsing.get_parser_instance()
stats = defaultdict(dict)


def print_stats() -> None:
    for key1 in stats.keys():
        for key2 in stats.keys():
            if key1 != key2:
                equal = stats[key1]['result'] == stats[key2]['result']
                print(f'{key1} == {key2}:', colored(str(equal), 'green' if equal else 'red'))

    min_duration = min([stats[s]['duration'] for s in stats])
    min_check_sat_duration = min([stats[s]['check_sat_duration'] for s in stats])
    min_check_sat_duration_avg = min([stats[s]['check_sat_duration_avg'] for s in stats])
    min_build_formula_duration = min([stats[s]['build_formula_duration'] for s in stats])
    min_build_formula_duration_avg = min([stats[s]['build_formula_duration_avg'] for s in stats])

    for s in stats:
        print(f'\n{s}:')

        min_ = stats[s]["duration"] <= min_duration
        print('duration:', colored(f'{stats[s]["duration"]}', 'green' if min_ else 'white'))

        print('result:', stats[s]['result'])

        print('result size:', f'{len(stats[s]["result"])}')

        print('check sat calls:', stats[s]['check_sat_calls'])

        min_ = stats[s]['check_sat_duration'] <= min_check_sat_duration
        print('check sat duration:', colored(f'{stats[s]["check_sat_duration"]}', 'green' if min_ else 'white'))

        min_ = stats[s]['check_sat_duration_avg'] <= min_check_sat_duration_avg
        print('check sat duration avg:', colored(f'{stats[s]["check_sat_duration_avg"]}', 'green' if min_ else 'white'))

        # print('check sat formulas:', stats[s]['check_sat_formulas'])

        min_ = stats[s]['build_formula_duration'] <= min_build_formula_duration
        print('build formula duration:', colored(f'{stats[s]["build_formula_duration"]}', 'green' if min_ else 'white'))

        min_ = stats[s]['build_formula_duration_avg'] <= min_build_formula_duration_avg
        print('build formula duration avg:',
              colored(f'{stats[s]["build_formula_duration_avg"]}', 'green' if min_ else 'white'))


def get_caller_name() -> str:
    return inspect.stack()[2].function


def get_func_name() -> str:
    return inspect.stack()[1].function


# def build_var_assertion(name: str, value: int):
#    return EqualsOrIff(Symbol(name, INT), Int(value))


# def build_var_assertions(name: str, values: tuple[int]):
#    return And([build_var_assertion(name, v) for v in values])


def build_formula_and(lhs: FNode, rhs: FNode) -> FNode:
    caller = get_caller_name()

    start = time.time()
    result = And(lhs, rhs)
    duration = time.time() - start

    stats[caller].setdefault('build_formula_calls', 0)
    stats[caller]['build_formula_calls'] += 1

    stats[caller].setdefault('build_formula_durations', [])
    stats[caller]['build_formula_durations'].append(duration)

    stats[caller].setdefault('build_formula_duration', 0)
    stats[caller]['build_formula_duration'] += duration

    stats[caller]['build_formula_duration_avg'] = stats[caller]['build_formula_duration'] / stats[caller][
        'build_formula_calls']

    return result


def check_sat(formula: FNode) -> bool:
    caller = get_caller_name()

    start = time.time()
    result = is_sat(formula, solver_name=SOLVER_NAME, logic=LOGIC)
    duration = time.time() - start

    stats[caller].setdefault('check_sat_calls', 0)
    stats[caller]['check_sat_calls'] += 1

    stats[caller].setdefault('check_sat_durations', [])
    stats[caller]['check_sat_durations'].append(duration)

    stats[caller].setdefault('check_sat_duration', 0)
    stats[caller]['check_sat_duration'] += duration

    stats[caller]['check_sat_duration_avg'] = stats[caller]['check_sat_duration'] / stats[caller]['check_sat_calls']

    # stats[caller].setdefault('check_sat_formulas', [])
    # stats[caller]['check_sat_formulas'].append(formula.simplify())

    return result


def naive(inputs: list[list[FNode]]) -> list[tuple[FNode]]:
    results = []

    # Compute cartesian product
    results_ = list(itertools.product(*inputs))

    # Check result tuples
    for i in range(len(results_) - 1, -1, -1):
        if i > 0 and i % 1000 == 0:
            print('[naive] check result tuples:', i)

        formula = TRUE()
        for r_ in results_[i]:
            formula = build_formula_and(formula, r_)

        if not check_sat(formula):
            del results_[i]

    return results_


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

    inputs = inputs_

    # Compute cartesian product
    results_ = list(itertools.product(*inputs))

    # Check result tuples
    for result_ in results_:
        formula = TRUE()

        for r_ in result_:
            formula = build_formula_and(formula, r_)

        if not check_sat(formula):
            results.remove(result_)

    return results_


def optimized_intermediate_checks(inputs: list[list[FNode]]) -> list[tuple[FNode]]:
    results = []

    if [] in inputs:
        return results

    # Check single elements
    inputs_ = []
    for input in inputs:
        input_ = []

        for e in input:
            if check_sat(build_formula_and(e, TRUE())):
                input_.append(e)

        inputs_.append(input_)

    inputs = inputs_

    # Compute cartesian product with intermediate checks
    for e in inputs[0]:
        results.append((e,))

    for input in inputs[1:]:
        results_ = []

        for result in results:
            formula = TRUE()

            for r in result:
                formula = build_formula_and(formula, r)

            for e in input:
                if check_sat(build_formula_and(formula, e)):
                    result_ = result + (e,)
                    results_.append(result_)

        results = results_

    return results


mapping = {
    'BndEdgeResponsePattern': {
        'name': '',
        'pattern': '',
        'variables': {'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V'}
    }
}


def main():
    inputs = [
        ['a && b', 'b && a'],
        ['!b', 'b && a']
    ]

    variables = {
        'a': Variable('a', 'bool', 'true'),
        'b': Variable('b', 'bool', 'true')
    }

    inputs = parse_inputs(inputs, variables)

    duration = time.time()
    stats['naive']['result'] = naive(inputs)
    stats['naive']['duration'] = time.time() - duration

    # duration = time.time()
    # stats['optimized_initial_checks']['result'] = optimized_initial_checks(inputs)
    # stats['optimized_initial_checks']['duration'] = time.time() - duration

    duration = time.time()
    stats['optimized_intermediate_checks']['result'] = optimized_intermediate_checks(inputs)
    stats['optimized_intermediate_checks']['duration'] = time.time() - duration

    print_stats()


def test_pysmt_durations():
    duration = time.time()
    a = Symbol('a', INT)
    b = Symbol('b', INT)
    print('vars:', (time.time() - duration) * 1000)

    duration = time.time()
    f1 = And(LT(a, Int(5)), GT(a, Int(0)))
    print('formula:', (time.time() - duration) * 1000)

    duration = time.time()
    c = Symbol('c', INT)
    d = Symbol('d', INT)
    print('vars:', (time.time() - duration) * 1000)

    duration = time.time()
    f2 = And(LT(c, Int(6)), GT(d, Int(1)))
    print('formula:', (time.time() - duration) * 1000)

    duration = time.time()
    x = Symbol('x', INT)
    y = Symbol('y', INT)
    print('vars:', (time.time() - duration) * 1000)

    duration = time.time()
    f3 = And(LT(x, Int(7)), GT(y, Int(2)))
    print('formula:', (time.time() - duration) * 1000)

    duration = time.time()
    is_sat(f1, solver_name=SOLVER_NAME, logic=LOGIC)
    print('sat f1:', (time.time() - duration) * 1000)

    duration = time.time()
    is_sat(f2, solver_name=SOLVER_NAME, logic=LOGIC)
    print('sat f2:', (time.time() - duration) * 1000)

    duration = time.time()
    is_sat(f3, solver_name=SOLVER_NAME, logic=LOGIC)
    print('sat f3:', (time.time() - duration) * 1000)

    duration = time.time()
    f4 = And(f1, f2, f3, f1, f2, f3, f1, f2, f3, )
    print('f4:', (time.time() - duration) * 1000)

    duration = time.time()
    is_sat(f4, solver_name=SOLVER_NAME, logic=LOGIC)
    print('sat f4:', (time.time() - duration) * 1000)


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
