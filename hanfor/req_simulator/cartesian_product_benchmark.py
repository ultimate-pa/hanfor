import inspect
import itertools
import time
from collections import defaultdict

from pysmt.fnode import FNode
from pysmt.shortcuts import TRUE, Symbol, EqualsOrIff, Int, is_sat, And
from pysmt.typing import INT

stats = defaultdict(dict)


def print_stats() -> None:
    for s in stats:
        print(f'\n{s}:')
        print('result:', stats[s]['result'])
        print('result size:', f'{len(stats[s]["result"])}')
        print('check sat calls:', stats[s]['check_sat_calls'])
        print('check sat duration:', sum(stats[s]['check_sat_durations']))
        print('check sat duration avg:', sum(stats[s]['check_sat_durations']) / len(stats[s]['check_sat_durations']))
        print('check sat formulas:', stats[s]['check_sat_formulas'])


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


def cartesian_product_naive(inputs: list[list[int]]) -> list[tuple[int]]:
    results = []

    results_ = list(itertools.product(*inputs))

    for i, result_ in enumerate(results_):
        formula = TRUE()

        for r_ in result_:
            formula = And(formula, build_var_assertion('x', r_))

        if check_sat(formula):
            results.append(result_)

    return results


def cartesian_product_optimized(lists) -> list[tuple[int]]:
    results = []

    if [] in lists:
        return results

    for l in lists[0]:
        if check_sat(build_var_assertion('x', l)):
            results.append((l,))

    for i, list in enumerate(lists[1:]):
        results_ = []

        for result in results:
            formula = And(TRUE(), build_var_assertions('x', result))

            for l in list:
                if check_sat(And(formula, build_var_assertion('x', l))):
                    result_ = result + (l,)
                    results_.append(result_)

        results = results_

    check_sat(TRUE())

    return results


def main():
    inputs = [[1, 1], [0, 1]]

    stats['cartesian_product_naive']['result'] = cartesian_product_naive(inputs)
    stats['cartesian_product_optimized']['result'] = cartesian_product_optimized(inputs)

    print_stats()


if __name__ == '__main__':
    main()
