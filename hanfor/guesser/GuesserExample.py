import re

from guesser.AGuesser import AGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from reqtransformer import ScopedPattern, Scope, Pattern


@register_guesser
class GuesserExample(AGuesser):
    """ A simple guesser implementation. Using regex to search for `var_a := var_b` """
    def guess(self):
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
