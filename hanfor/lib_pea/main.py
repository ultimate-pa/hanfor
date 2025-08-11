from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import build_automaton
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

    def interact(self, command: str, args: list[str]):
        match (command):
            case "pop":
                if len(self.stack) > 0:
                    self.stack.pop()
                print(f"Stack is now of len {len(self.stack)}")
            case "push":
                try:
                    form = " ".join(args)
                    trace = CountertraceTransformer(self.vars).transform(get_countertrace_parser().parse(form))
                    aut = build_automaton(trace)
                    self.stack.append(aut)
                except Exception as e:
                    print(f"Error: {e}")
            case "status":
                print(f"Stack is now of len {len(self.stack)} and variables {self.vars}")
            case "print":
                if not args:
                    return
                if args[0].isdecimal() and int(args[0]) < len(self.stack):
                    print(str(self.stack[int(args[0])]))
                elif args[0] in self.vars:
                    print(f"{args[0]} is {self.vars[args[0]]}")  # TODO: this is strange
                else:
                    print(f"ERROR: Arg {args[0]} is neither a stack index nor a variable name...")
            case "define":
                name, type, value = None, None, None
                if len(args) == 2:
                    name, type = args
                elif len(args) == 3:
                    name, type, value = args
                else:
                    print(f"ERROR: Wrong number of Arguments either <name> <type> or <name> cosnt <value> ")
                if type not in BoogiePysmtTransformer.hanfor_to_pysmt_mapping:
                    print(f"ERROR: Bad type {type}")
                    return
                if value:
                    self.vars[name] = BoogiePysmtTransformer.hanfor_to_pysmt_mapping[type](name, value)
                else:
                    self.vars[name] = BoogiePysmtTransformer.hanfor_to_pysmt_mapping[type](name, None)
            case "product":
                times = 2
                if args and args[0].isdecimal() and int(args[0]) < len(self.stack):
                    times = int(args[0])
                pea = self.stack[-1]
                for other in self.stack[-2:-times:-1]:
                    pea = pea.intersect(other)
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
