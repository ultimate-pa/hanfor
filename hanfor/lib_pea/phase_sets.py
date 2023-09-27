from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseSets:
    gteq: frozenset[int] = frozenset()
    wait: frozenset[int] = frozenset()
    less: frozenset[int] = frozenset()
    active: frozenset[int] = frozenset()

    def __str__(self) -> str:
        result = ""

        for i in self.active:
            result += str(i)
            result += (
                "ᴳ" if i in self.gteq else
                "ᵂ" if i in self.wait else
                "ᴸ" if i in self.less else
                ""
            )

        return result

    def is_empty(self) -> bool:
        return len(self.gteq) == 0 and len(self.wait) == 0 and len(self.less) == 0 and len(self.active) == 0

    def add_gteq(self, i: int) -> "PhaseSets":
        return PhaseSets(
            self.gteq.union({i}),
            self.wait.union({i}),
            self.less.copy(),
            self.active.union({i}),
        )

    def add_wait(self, i: int) -> "PhaseSets":
        return PhaseSets(self.gteq.copy(), self.wait.union({i}), self.less.copy(), self.active.union({i}))

    def add_less(self, i: int) -> "PhaseSets":
        return PhaseSets(self.gteq.copy(), self.wait.copy(), self.less.union({i}), self.active.union({i}))

    def add_active(self, i: int) -> "PhaseSets":
        return PhaseSets(self.gteq.copy(), self.wait.copy(), self.less.copy(), self.active.union({i}))
