import graphviz
from lark import Lark
from pysmt.fnode import FNode
from pysmt.shortcuts import Symbol, substitute

from lib_pea.pea import PhaseSetsPea

CT_PARSER = None


def get_countertrace_parser() -> Lark:
    global CT_PARSER

    if CT_PARSER is None:
        CT_PARSER = Lark.open(
            "countertrace_grammar.lark",
            rel_to=__file__,
            start="countertrace",
            parser="lalr",
        )

    return CT_PARSER


def substitute_free_variables(fnode: FNode, suffix: str = "_", do_nothing: bool = True) -> FNode:
    if do_nothing:
        return fnode

    symbols = fnode.get_free_variables()
    subs = {s: Symbol(s.symbol_name() + suffix, s.symbol_type()) for s in symbols}
    result = substitute(fnode, subs)
    return result


def render_pea(pea: PhaseSetsPea, filename: str, view=False) -> None:
    dot = graphviz.Digraph(comment='Phase Event Automaton')
    for phase, transitions in pea.transitions.items():
        src_label = str(phase.label) if phase is not None else 'None'
        dot.node(src_label)

        for transition in transitions:
            dst_label = str(transition.dst.label) if transition.dst is not None else 'None'
            guard_str = transition.guard.serialize()

            for clock in pea.clocks:
                guard_str = guard_str.replace(clock, "c" + guard_str.split("_")[-1])

            dot.edge(src_label, dst_label, label=guard_str)

    dot.render(filename, view=view)
