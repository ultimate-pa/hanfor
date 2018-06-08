import re
from abc import ABC, abstractmethod
from reqtransformer import Requirement, ScopedPattern, Scope, Pattern

REGISTERED_GUESSERS = []


def register_guesser(guesser):
    REGISTERED_GUESSERS.append(guesser)


class AGuesser(ABC):
    """ Guess formalization(s) for a requirement. """
    def __init__(self, requirement, variable_collection, app):
        """

        :param requirement: Requirement the guess should be based on.
        :type requirement: Requirement
        :param variable_collection: Available variables
        :type variable_collection: VariableCollection
        :param app: Flask app for context.
        :type app:
        """
        self.requirement = requirement
        self.variable_collection = variable_collection
        self.app = app
        super().__init__()

    @abstractmethod
    def guess(self):
        """ Determine formalization guess(es).
        This method is expected to return a list containing guesses.
        A valid returned list would be:

            [
                Guess(
                    score=0.1,
                    scoped_pattern=ScopedPattern(
                        Scope['AFTER'],
                        Pattern(name='Universality')
                    ),
                    mapping={
                        'P': 'Rain',
                        'R': 'Street_is_wet'
                    }
                )
            ]


        :returns: list of guesses [guess, ... ]
        :rtype: list
        """
        pass


class Guess(tuple):
    """ A guess should be used by an AGuesser implementation. """
    def __init__(cls, score, scoped_pattern, mapping):
        # This is just a dummy __init__ to make documentation work
        """ A single `guess` is represented by tuple:

            (score, scoped_pattern, mapping)

        'score:'          Float \in [0, 1]. The `score` will determine the order of the available guesses (DESC).
        'scoped_pattern:' A ScopedPattern instance.
        'mapping:'        A dict for the variables assignement like:

            {
                'P': 'Rain',
                'R': 'Street_is_wet'
            }

        :param score: Float \in [0, 1]. The `score` will determine the order of the available guesses (DESC).
        :type score: float
        :param scoped_pattern: A ScopedPattern instance.
        :type scoped_pattern: ScopedPattern
        :param mapping: A dict for the variables assignement like:
            {
                'P': 'Rain',
                'R': 'Street_is_wet'
            }
        :type mapping: dict
        """
        super().__init__()

    def __new__(cls, score, scoped_pattern, mapping):
        """ A single `guess` is represented by tuple:

            (score, scoped_pattern, mapping)

        'score:'          Float \in [0, 1]. The `score` will determine the order of the available guesses (DESC).
        'scoped_pattern:' A ScopedPattern instance.
        'mapping:'        A dict for the variables assignement like:

            {
                'P': 'Rain',
                'R': 'Street_is_wet'
            }

        :param score: Float \in [0, 1]. The `score` will determine the order of the available guesses (DESC).
        :type score: float
        :param scoped_pattern: A ScopedPattern instance.
        :type scoped_pattern: ScopedPattern
        :param mapping: A dict for the variables assignement like:
            {
                'P': 'Rain',
                'R': 'Street_is_wet'
            }
        :type mapping: dict
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError('The Score `{}` should be between 0 and 1'.format(score))

        if not isinstance(scoped_pattern, ScopedPattern):
            raise ValueError('scoped_pattern should be an instance of ScopedPattern')

        if not isinstance(mapping, dict):
            raise ValueError('scoped_pattern should be an instance of ScopedPattern')

        try:
            scoped_pattern.get_string(mapping)
        except:
            raise ValueError('Mapping is missing some variables.')

        return super(Guess, cls).__new__(cls, tuple((score, scoped_pattern, mapping)))

####################################################################
# Add your Guessers here and decorate them with "@register_guesser".
# On all registered guessers the results will be combined and added
# to the available guesses.
####################################################################


@register_guesser
class GuessSimpleInvariant(AGuesser):
    """ A simple guesser implementation. Using regex to search for `var_a := var_b` """
    def guess(self):
        guesses = list()

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
            guesses.append(
                Guess(
                    score=1,
                    scoped_pattern=scoped_pattern,
                    mapping=mapping
                )
            )

        return guesses
