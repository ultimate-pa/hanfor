import re

from guesser.AbstractGuesser import AbstractGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from reqtransformer import ScopedPattern, Scope, Pattern


@register_guesser
class RegexGuesser(AbstractGuesser):
    """ A guesser that uses multiple regex in some order to make a guess."""
    def guess(self):
        # try `var_a := var_b`
        regex = r"(.*):=(.*)"
        # Search in the requirement description.
        matches = re.finditer(regex, self.requirement.description, re.MULTILINE)

        # For each match add a guess.
        for match in matches:
            scoped_pattern = ScopedPattern(
                Scope['GLOBALLY'],
                Pattern(name='Invariant')
            )
            mapping = {
                'R': match.group(1).strip(),
                'S': match.group(2).strip()
            }
            self.guesses.append(
                Guess(
                    score=1,
                    scoped_pattern=scoped_pattern,
                    mapping=mapping
                )
            )
