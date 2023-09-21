from __future__ import annotations

import json
import math
from typing import Any

import jsbeautifier
import yaml
from lark import Lark
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, substitute

SOLVER_NAME = 'z3'
LOGIC = 'QF_NRA'
CT_PARSER = None


def get_countertrace_parser() -> Lark:
    global CT_PARSER

    if CT_PARSER is None:
        CT_PARSER = Lark.open('countertrace_grammar.lark', rel_to=__file__, start='countertrace', parser='lalr')

    return CT_PARSER


def substitute_free_variables(fnode: FNode, suffix: str = "_", do_nothing: bool = True) -> FNode:
    if do_nothing:
        return fnode

    symbols = fnode.get_free_variables()
    subs = {s: Symbol(s.symbol_name() + suffix, s.symbol_type()) for s in symbols}
    result = substitute(fnode, subs)
    return result

def num_zeros(x: float) -> int:
    return 0 if x >= 1 else -math.floor(math.log10(x)) - 1


