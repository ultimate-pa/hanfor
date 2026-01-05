from collections import defaultdict

from pysmt.formula import FormulaManager

from lib_pea.countertrace import Countertrace
from lib_pea.location import PhaseSetsLocation, Location
from lib_pea.pea_operations import PeaOperationsMixin
from lib_pea.transition import PhaseSetsTransition, Transition


class Pea(PeaOperationsMixin):
    def __init__(self):
        self.transitions: defaultdict[Location, set[Transition]] = defaultdict(set)
        self.clocks: set[str] = set()

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
    def __init__(self, countertrace: Countertrace = None):
        super().__init__()

        self.transitions: defaultdict[PhaseSetsLocation, set[PhaseSetsTransition]] = defaultdict(set)
        self.countertrace: Countertrace = countertrace
        self.requirement = None
        self.formalization = None
        self.countertrace_id: int = None

    def __eq__(self, o: "PhaseSetsPea") -> bool:
        return isinstance(o, PhaseSetsPea) and o.transitions == self.transitions

    @classmethod
    def load(cls, path: str) -> "PhaseSetsPea":
        # pea = super().load(path)
        # pea.normalize(get_env().formula_manager)
        # return pea
        raise NotImplementedError

    def normalize(self, formula_manager: FormulaManager) -> None:
        self.countertrace.normalize(formula_manager)

        for transitions in self.transitions.values():
            for transition in transitions:
                transition.normalize(formula_manager)

    def add_transition(self, transition: PhaseSetsTransition) -> None:
        if transition in self.transitions[transition.src]:
            raise ValueError("Transition already exists in this phase event automaton.")

        self.clocks |= transition.resets
        self.transitions[transition.src].add(transition)
