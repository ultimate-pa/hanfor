# Import all classes in this directory so that guessers with @guesser_registerer are registered.
from guesser.guesser_registerer import REGISTERED_GUESSERS
from os.path import basename, dirname, join
from glob import glob

pwd = dirname(__file__)
for x in glob(join(pwd, "*.py")):
    if not x.startswith("__"):
        __import__("guesser." + basename(x)[:-3], globals(), locals())

__all__ = ["REGISTERED_GUESSERS"]
