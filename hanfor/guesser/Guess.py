from reqtransformer import ScopedPattern


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
