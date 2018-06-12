# Intro
This module provides all the guessers Hanfor uses to predict formalizations for requirements.

# How to add a guesser
Assume you want to implement `FancyGuesser`.

1. Create the file `FancyGuesser.py` in this directory.
2. Add imports
   ````
   from guesser.AbstractGuesser import AbstractGuesser
   from guesser.Guess import Guess
   from guesser.guesser_registerer import register_guesser
   ````
3. Create your class `FancyGuesser(AbstractGuesser)`
4. In the ``guess()`` method fill the ``self.guesses`` list with your guesses.
5. Decorate your guesser with ``@register_guesser`` so it will be taken into account when Hanfor derives the formalization guesses.

See `GuesserExample.py` in this directory for an example implementation.
