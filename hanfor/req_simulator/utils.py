from __future__ import annotations

import json
from typing import Any

import yaml
from lark import Lark
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, substitute

ct_parser = None


def get_countertrace_parser() -> Lark:
    global ct_parser

    if ct_parser is None:
        ct_parser = Lark.open('countertrace_grammar.lark', rel_to=__file__, start='countertrace', parser='lalr')

    return ct_parser


def substitute_free_variables(fnode: FNode, suffix: str = "_") -> FNode:
    symbols = fnode.get_free_variables()
    subs = {s: Symbol(s.symbol_name() + suffix, s.symbol_type()) for s in symbols}
    result = substitute(fnode, subs)
    return result


def save_yaml_file(data: Any, path: str, sort_keys: bool = False):
    with open(path, 'w') as file:
        yaml.dump(data, file, sort_keys=sort_keys)


def save_json_file(data: Any, path: str, sort_keys: bool = False):
    with open(path, 'w') as file:
        json.dump(data, file, indent=2, sort_keys=sort_keys)


def load_yaml_or_json_file(path: str) -> Any:
    with open(path, 'r') as file:
        data = yaml.safe_load(file)

    return data


def parse_yaml_or_json_string(yaml_str: str) -> Any:
    return yaml.safe_load(yaml_str)
