from guesser.AbstractGuesser import AbstractGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from guesser.reqsyntaxtree import ReqSyntaxTree, ReqTransformer
from guesser.utils import flatten_list, replace_characters
from lib_core.data import Scope, ScopedPattern, Pattern


@register_guesser
class TreeGuesser(AbstractGuesser):
    """A guesser that uses multiple regex in some order to make a guess."""

    def __init__(self, requirement, variable_collection, app):
        AbstractGuesser.__init__(self, requirement, variable_collection, app)
        self.req_syntax_tree = ReqSyntaxTree()
        self.req_transformer = ReqTransformer()

    def guess(self):
        # scoped_pattern, mapping = self.__generate_tree_guess()
        return None, None
        if not scoped_pattern:
            return
        self.guesses.append(Guess(score=1, scoped_pattern=scoped_pattern, mapping=mapping))

    def __generate_tree_guess(self):
        self.req_syntax_tree.create_tree(replace_characters(self.requirement.description))
        transformed = self.req_transformer.transform(self.req_syntax_tree.tree)
        req = list(flatten_list(transformed.children))
        if isinstance(req[0], dict):
            logic = req[0]["logic"]
            if_part = req[0]["if_part"]
            then_part = req[0]["then_part"]
            print(logic)
            print(if_part)
            print(then_part)
        else:
            print(req)
        var1 = ""
        var2 = ""

        scope = "GLOBALLY"
        scoped_pattern = ScopedPattern(Scope[scope], Pattern(name="BoundedResponse"))

        mapping = {"R": "%s" % var1, "S": "%s" % var2, "T": "MAX_TIME"}

        return scoped_pattern, mapping
