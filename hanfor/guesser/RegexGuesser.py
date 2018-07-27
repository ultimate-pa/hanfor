import re
from functools import reduce

from guesser.AbstractGuesser import AbstractGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from reqtransformer import ScopedPattern, Scope, Pattern



@register_guesser
class RegexGuesser(AbstractGuesser):
    """ A guesser that uses multiple regex in some order to make a guess."""

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
        #if "== ->" in self.requirement.description or "==->" in self.requirement.description:
        #    return None, None

        # match IF ... THEN ... case.
        match = re.search(r'IF(.*)THEN(.*)(Hint: .*)*', self.requirement.description, re.DOTALL)

        if not match:
            return None, None

        # There is IF (AND-logic) .. THEN and IF (OR-logic) .. THEN
        and_logic = True
        if "(or-logic)" in match.group(1).lower():
            and_logic = False

        var1 = self.__process_if_part(match.group(1).replace("(AND-logic)", "").replace("(OR-logic)", ""), and_logic)
        var2 = self.__process_if_part(match.group(2), and_logic)

        if var1 is None or var2 is None:
            return None, None

        return self.__create_bounded_response_if_then(var1=var1, var2=var2)

    def __process_if_part(self, part, and_logic):
        terms = part.strip().split("\n")
        processed = []
        for term in terms:
            sub_terms = re.split("OR|AND", term)
            new_sub_terms = []
            for sub_term in sub_terms:
                new_sub_term = self.__process_term(sub_term.strip())
                if new_sub_term is not None:
                    new_sub_terms.append(new_sub_term)
            if new_sub_terms:
                if "OR" in term:
                    new_term = " || ".join(new_sub_terms)
                elif "AND" in term:
                    new_term = " && ".join(new_sub_terms)
                else:
                    new_term = "".join(new_sub_terms)
                processed.append("(%s)" % new_term)
        if and_logic:
            new_part = "\n&&".join(processed)
        else:
            new_part = "\n||".join(processed)
        return new_part

    def __process_term(self, term):
        equals = re.search(r'(.*)(==)(.*)', term.replace(" := ", " == ").replace("== ->", "==").replace("==->", "=="), re.DOTALL)
        not_equals = re.search(r'(.*)(!=)(.*)', term, re.DOTALL)
        gt_lt = re.search(r'(.*)\s(<|>=|>|<=)\s(.*)', term, re.DOTALL)
        not_available = re.search(r'(.*) not available', term, re.DOTALL)
        available = re.search(r'(.*)(is)* available', term, re.DOTALL)
        received = re.search(r'(.*)(is)* received', term, re.DOTALL)
        not_received = re.search(r'(.*) not received', term, re.DOTALL)
        timer = re.search(r'(start|stop) timer (.*)', term, re.DOTALL)

        sep = "=="
        case = False

        if equals:
            sep = "=="
            case = equals
        elif not_equals:
            sep = "!="
            case = not_equals
        elif not_available:
            sep = None
            case = not_available
        elif not_received:
            sep = None
            case = not_received
        elif received:
            sep = None
            case = received
        elif available:
            sep = None
            case = available
        elif gt_lt:
            sep = gt_lt.group(2)
            case = gt_lt
        elif timer:
            sep = "=="
            case = timer

        if equals or not_equals:
            LHS = case.group(1).strip()
            RHS = case.group(3).strip().replace('"', '').replace(" ", "_").lower().replace("(", "").replace(")", "").replace("&", "AND")
            if RHS != "1" and RHS != "0":
                RHS = "%s_%s" % (LHS, RHS.upper())
            new_term = "%s %s %s" % (LHS, sep, RHS)
        elif not_available or not_received:
            new_term = "!%s" % case.group(1).strip().replace(" is", "")
        elif received or available:
            new_term = "%s" % case.group(1).strip().replace(" is", "")
        elif gt_lt:
            LHS = case.group(1).strip()
            RHS = case.group(3).strip().replace('"', '').replace(" ", "_").replace("(", "").replace(")", "").replace("&", "AND")
            new_term = "%s %s %s" % (LHS, sep, RHS)
        elif timer:
            LHS = case.group(2).strip()
            RHS = 0.0
            new_term = "%s %s %s" % (LHS, sep, RHS)
        else:
            new_term = None

        return new_term


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

    def __create_bounded_response_if_then(self, var1, var2):
        """
        Creates 'BoundedResponse' pattern with MAX_TIME as T
        'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        """
        scoped_pattern = ScopedPattern(
            Scope['GLOBALLY'],
            Pattern(name='BoundedResponse')
        )

        mapping = {
            'R': "%s" % var1,
            'S': "%s" % var2,
            'T': 'MAX_TIME'
        }

        return scoped_pattern, mapping

    def __match(self, regex):
        result = re.finditer(regex, self.requirement.description, re.MULTILINE)
        return list(result)
