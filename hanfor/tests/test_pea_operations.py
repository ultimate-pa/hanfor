from unittest import TestCase

from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.utils import get_countertrace_parser
from tests.test_req_simulator.test_counter_trace import testcases


class TestPhaseAutomatonOperations(TestCase):

    def test_1_1(self):
        expressions, ct_str, _ = testcases["false"]
        ct1 = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
        a1 = build_automaton(ct1)

        expressions, ct_str, _ = testcases["false"]
        ct2 = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
        a2 = build_automaton(ct2)

        result = a1.intersect(a2)
        pass
