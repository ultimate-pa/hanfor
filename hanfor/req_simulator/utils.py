from __future__ import annotations

import json
import math
from typing import Any

import jsbeautifier
import yaml
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, substitute

SOLVER_NAME = "z3"
LOGIC = "QF_NRA"
CT_PARSER = None


def substitute_free_variables(
    fnode: FNode, suffix: str = "_", do_nothing: bool = True
) -> FNode:
    if do_nothing:
        return fnode

    symbols = fnode.get_free_variables()
    subs = {s: Symbol(s.symbol_name() + suffix, s.symbol_type()) for s in symbols}
    result = substitute(fnode, subs)
    return result


def num_zeros(x: float) -> int:
    return 0 if x >= 1 else -math.floor(math.log10(x)) - 1


def parse_json_or_yaml_string(str: str) -> Any:
    return yaml.safe_load(str)


# TODO: Maybe uses this for save file functions too.
def dump_json_string(data: Any, sort_keys: bool = False) -> str:
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    return jsbeautifier.beautify(
        json.dumps(data, indent=None, sort_keys=sort_keys), opts
    )


def load_json_or_yaml_file(path: str) -> Any:
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    return data


def save_yaml_file(data: Any, path: str, sort_keys: bool = False):
    with open(path, "w") as file:
        yaml.dump(data, file, sort_keys=sort_keys)


def save_json_file(data: Any, path: str, sort_keys: bool = False):
    with open(path, "w") as file:
        json.dump(data, file, indent=2, sort_keys=sort_keys)
