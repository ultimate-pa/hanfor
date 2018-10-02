import re
from functools import reduce

from guesser.AbstractGuesser import AbstractGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from reqtransformer import ScopedPattern, Scope, Pattern
from guesser.FormulaProcessor import FormulaProcessor



@register_guesser
class RegexGuesser(AbstractGuesser):
    """ A guesser that uses multiple regex in some order to make a guess."""

    def __init__(self,requirement, variable_collection, app):
        AbstractGuesser.__init__(self,requirement, variable_collection, app)
        self.formula_processor = FormulaProcessor()

    def guess(self):
        matcher = [
            self.__guess_if_then,
            self.__guess_assign,
            self.__guess_signal_routing,
            self.__guess_signal_routing_message,
            self.__guess_signal_routing_value
        ]

        # If one matches, use it
        for match in matcher:
            try:
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
            except:
                pass

    def __guess_assign(self):
        # try `var_a := var_b`
        matches = self.__match(r"(.*):=(.*)")
        if len(matches) != 1:
            return None, None

        return self.__create_invariant(matches[0])

    def __guess_signal_routing(self):
        matches = self.__match(r"^The signal (\w+) shall be routet on \w+ \((\w+)\s*\)[\s|\.]*$")
        if len(matches) != 1:
            return None, None

        return self.__create_bounded_response(matches[0])

    def __guess_signal_routing_message(self):
        matches = self.__match(r"^The message (\w+) shall be routet on \w+ \((\w+)\s*\)[\s|\.]*$")
        if len(matches) != 1:
            return None, None

        return self.__create_bounded_response(matches[0])

    def __guess_signal_routing_value(self):
        matches = self.__match(r"^The value of the parameter (\w+) shall be routet on \w+ \((\w+)\s*\)[\s|\.]*$")
        if len(matches) != 1:
            return None, None

        return self.__create_bounded_response(matches[0])

    def __guess_if_then(self):

        # match IF ... THEN ... case.
        match = re.search(r'(?:IF|WENN)(.*)(?:THEN|DANN)(.*)(Hint: .*)*', self.requirement.description, re.DOTALL)

        if not match:
            return None, None

        after = "== ->" in self.requirement.description or "==->" in self.requirement.description

        # There is IF (AND-logic) .. THEN and IF (OR-logic) .. THEN
        and_logic = True
        if "(or-logic)" in match.group(1).lower():
            and_logic = False

        if_part = match.group(1).replace("(AND-logic)", "").replace("(OR-logic)", "")
        then_part = match.group(2)
        var1 = self.formula_processor.process_if_part(if_part, and_logic)
        var2 = self.formula_processor.process_if_part(then_part, and_logic)

        if var1 is None or var2 is None:
            return None, None

        return self.__create_bounded_response_if_then(var1=var1, var2=var2, after=after)


    def __create_bounded_response(self, match):
        """
        Creates 'BoundedResponse' pattern with MAX_TIME as T
        'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        """
        scoped_pattern = ScopedPattern(
            Scope['GLOBALLY'],
            Pattern(name='BoundedResponse')
        )

        var1 = match.group(1).strip()
        var2 = match.group(2).strip()

        mapping = {
            'R': "{} != {}".format(var1, var2),
            'S': "{} == {}".format(var1, var2),
            'T': 'MAX_TIME'
        }
        return scoped_pattern, mapping

    def __create_invariant(self, match):
        scoped_pattern = ScopedPattern(
            Scope['GLOBALLY'],
            Pattern(name='Invariant')
        )
        mapping = {
            'R': match.group(1).strip(),
            'S': match.group(2).strip()
        }
        return scoped_pattern, mapping

    def __create_bounded_response_if_then(self, var1, var2, after=False):
        """
        Creates 'BoundedResponse' pattern with MAX_TIME as T
        'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        """
        if after:
            scope = 'AFTER'
        else:
            scope = 'GLOBALLY'

        scoped_pattern = ScopedPattern(
            Scope[scope],
            Pattern(name='BoundedResponse')
        )

        if after:
            mapping = {
                'P': "!(%s)" % var1,
                'R': "%s" % var1,
                'S': "%s" % var2,
                'T': 'MAX_TIME'
            }
        else:
            mapping = {
                'R': "%s" % var1,
                'S': "%s" % var2,
                'T': 'MAX_TIME'
            }

        return scoped_pattern, mapping

    def __match(self, regex):
        result = re.finditer(regex, self.requirement.description, re.MULTILINE)
        return list(result)
