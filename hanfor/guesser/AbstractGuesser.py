from abc import ABC, abstractmethod
from lib_core.data import Requirement
from hanfor_flask import HanforFlask


class AbstractGuesser(ABC):
    """Guess formalization(s) for a requirement.

    Attributes:
        guesses: list of: Guesses | lists of Guesses | mixture of both.
                 To determine which guesses will be used:
                 Single guesses will be sorted by their score.
                 Lists of guesses will be sorted by their average score.
    """

    def __init__(self, requirement, variable_collection, app: HanforFlask):
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
        self.guesses = list()
        super().__init__()

    @abstractmethod
    def guess(self):
        """Determine formalization guess(es).
        This method is expected to fill the self.guesses() list with guesses.
        A valid append would be:

            self.guesses.append(
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
            )
        """
        raise NotImplementedError
