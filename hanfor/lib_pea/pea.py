from collections import defaultdict

from pysmt.environment import Environment

from lib_pea.countertrace import Countertrace
from lib_pea.location import PhaseSetsLocation, Location
from lib_pea.pea_operations import PeaOperationsMixin
from lib_pea.transition import PhaseSetsTransition, Transition


class Pea(PeaOperationsMixin):
    def __init__(
        self,
        smt_env: Environment,  # current  pySMT Environment (containing the right/current symbols and types)
    ):
        self.transitions: defaultdict[Location, set[Transition]] = defaultdict(set)
        self.clocks: set[str] = set()
        self._smt_env: Environment = smt_env
        self._solver = self._smt_env.factory.get_solver(name="z3")

    def locations(self) -> set[Location]:
        return set(self.transitions.keys())

    def __str__(self):
        return (
            "\nPEA:\n"
            + "\n".join([str(l) for l in self.locations()])
            + "\n"
            + "\n".join([str(t) for ts in self.transitions.values() for t in ts])
        )


class PhaseSetsPea(Pea):
    def __init__(self, smt_env: Environment, countertrace: Countertrace):
        super().__init__(smt_env)
        self.transitions: defaultdict[PhaseSetsLocation | None, set[PhaseSetsTransition]] = defaultdict(set)
        self.countertrace: Countertrace = countertrace
        self.requirement = None
        self.formalization = None
        self.countertrace_id: int | None = None

    def __eq__(self, o: "PhaseSetsPea") -> bool:
        return isinstance(o, PhaseSetsPea) and o.transitions == self.transitions

    def normalize(self) -> None:
        self.countertrace.normalize()

        for transitions in self.transitions.values():
            for transition in transitions:
                transition.normalize()

    def add_transition(self, transition: PhaseSetsTransition) -> None:
        if transition in self.transitions[transition.src]:
            raise ValueError("Transition already exists in this phase event automaton.")

        self.clocks |= transition.resets
        self.transitions[transition.src].add(transition)
