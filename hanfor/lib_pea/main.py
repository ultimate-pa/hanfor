from pysmt.environment import Environment

from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import PeaBuilder
from lib_pea.utils import get_countertrace_parser
from pea import Pea

"""
This module provides a standalone interface for the PEA functionality of Hanfor.
"""

HELP = """
pop: remove automaton from stack
push <cex>: add formula to stack (format as in hanfor doc, vars must be defined)
status: print overall status
print <n>: print nth automaton (on stack) or variable called n
define <n> <t> <v>: define variable <name> <type> or constant of <name> const <value>
product <n>: build product of uppermost n automata and put on stack
-----------------------------------------------------------------
exit: exit
file <path>: execute script file
"""


class PeaLibStack:

    def __init__(self):
        self.stack: list[Pea] = list()
        self.vars = dict()
        self.smt_env = Environment()
        self.smt_solver = self.smt_env.factory.get_solver("z3")
        self.pea_builder = PeaBuilder(self.smt_env)
        self.transformer = BoogiePysmtTransformer(self.smt_env, set())

    def interact(self, command: str, args: list[str]):
        match command:
            case "pop":
                if len(self.stack) > 0:
                    self.stack.pop()
                print(f"Stack is now of len {len(self.stack)}")
            case "push":
                try:
                    form = " ".join(args)
                    trace = CountertraceTransformer(self.smt_env, self.vars).transform(
                        get_countertrace_parser().parse(form)
                    )
                    aut = self.pea_builder.build_automaton(trace)
                    self.stack.append(aut)
                except Exception as e:
                    print(f"Error: {e}")
            case "status":
                print(f"Stack is now of len {len(self.stack)} and variables {self.vars}")
            case "print":
                if not args:
                    return
                if args[0].isdecimal() and int(args[0]) < len(self.stack):
                    # print(str(self.stack[int(args[0])]))
                    print(self.stack[int(args[0])].pretty_str())
                elif args[0] in self.vars:
                    print(f"{args[0]} is {self.vars[args[0]]}")
                else:
                    print(f"ERROR: Arg {args[0]} is neither a stack index nor a variable name...")
            case "define":
                name, vtype, value = None, None, None
                if len(args) == 2:
                    name, vtype = args
                elif len(args) == 3:
                    name, vtype, value = args
                else:
                    print(f"ERROR: Wrong number of Arguments either <name> <vtype> or <name> cosnt <value> ")
                if vtype not in self.transformer.hanfor_to_pysmt_mapping:
                    print(f"ERROR: Bad vtype {vtype}")
                    return
                if value:
                    self.vars[name] = self.transformer.hanfor_to_pysmt_mapping[vtype](name, value)
                else:
                    self.vars[name] = self.transformer.hanfor_to_pysmt_mapping[vtype](name, None)
            case "product":
                times = 2
                if args and args[0].isdecimal() and int(args[0]) < len(self.stack):
                    times = int(args[0])
                pea = self.stack[-1]
                for other in self.stack[-2:-times:-1]:
                    pea = pea.intersect(other, self.smt_env, self.smt_solver)
                self.stack.append(pea)
            case _:
                print(f"Did not understand... \n {HELP}")


def main():
    stack = PeaLibStack()
    print(f"PEA CLI\n use commands \n{HELP}")
    cst = []
    while True:
        if cst:
            print(f">>> {cst[0]}")
            c = cst[0]
            cst = cst[1:]
        else:
            c = input(">")
        args = str.split(c.strip(), " ")
        match (args[0]):
            case "exit":
                return
            case "help":
                print(HELP)
            case "file":
                with open(" ".join(args[1:]), "r", encoding="utf-8") as f:
                    cst = f.readlines()
            case _:
                stack.interact(args[0], args[1:])


if __name__ == "__main__":
    main()
