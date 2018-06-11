# Intro.
This module provides all the guessers hanfor uses to predict formalizations for requirements.

# How to add a guesser.
Assume you want to implement `FancyGuesser`.
    
    1. Create the file `FancyGuesser.py` in this directory.
    2. import
        
        from guesser.AGuesser import AGuesser
        from guesser.Guess import Guess
        from guesser.guesser_registerer import register_guesser
    3. Create your class `FancyGuesser(AGuesser)`
    4. In the guess() method fill the self.guesses list with you gesses.
    5. Decorate your gesser with @register_guesser so it will be taken into account 
       when hanfor derives the formalization guesses.

See `GuessExample.py` for a example implementation.
