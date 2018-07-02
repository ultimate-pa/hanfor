import re

from guesser.AbstractGuesser import AbstractGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from reqtransformer import ScopedPattern, Scope, Pattern


@register_guesser
class RegexGuesser(AbstractGuesser):
    """ A guesser that uses multiple regex in some order to make a guess."""

    def guess(self):
        matcher = [
            self.__guess_assign,
            self.__guess_signal_routing
        ]

        # If one matches, use it
        for match in matcher:
            scoped_pattern, mapping = match()
            if not scoped_pattern:
                continue
            self.guesses.append(
                Guess(
                    score=1,
                    scoped_pattern=scoped_pattern,
                    mapping=mapping
                )
            )
            break

    def __guess_assign(self):
        # try `var_a := var_b`
        regex = r"(.*):=(.*)"

        result = re.finditer(regex, self.requirement.description, re.MULTILINE)
        matches = list(result)
        if len(matches) != 1:
            return None, None

        match = matches[0]
        scoped_pattern = ScopedPattern(
            Scope['GLOBALLY'],
            Pattern(name='Invariant')
        )
        mapping = {
            'R': match.group(1).strip(),
            'S': match.group(2).strip()
        }
        return scoped_pattern, mapping

    def __guess_signal_routing(self):
        regex = r"^The signal (\w+) shall be routet on \w+ \((\w+)\)[\s|\.]*$"
        result = re.finditer(regex, self.requirement.description, re.MULTILINE)
        matches = list(result)
        if len(matches) != 1:
            return None, None

        """
        Becomes 'BoundedResponse':
        'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        """

        match = matches[0]
        scoped_pattern = ScopedPattern(
            Scope['GLOBALLY'],
            Pattern(name='BoundedResponse')
        )
        mapping = {
            'R': match.group(1).strip(),
            'S': match.group(2).strip(),
            'T': 'MAX_TIME'
        }
        return scoped_pattern, mapping
