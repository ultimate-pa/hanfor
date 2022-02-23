from __future__ import annotations

import json
from typing import Any

import yaml
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, substitute


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


def parse_yaml_string(yaml_str: str) -> Any:
    return yaml.safe_load(yaml_str)
