from enum import Enum

from lib_core import boogie_parsing


class Scope(Enum):
    GLOBALLY = "Globally"
    BEFORE = 'Before "{P}"'
    AFTER = 'After "{P}"'
    BETWEEN = 'Between "{P}" and "{Q}"'
    AFTER_UNTIL = 'After "{P}" until "{Q}"'
    NONE = "// None"

    def instantiate(self, *args):
        return str(self.value).format(*args)

    def get_slug(self):
        """Returns a short slug representing the scope value.
        Use in applications where you don't want to use the full string.

        :return: Slug like AFTER_UNTIL for 'After "{P}" until "{Q}"'
        :rtype: str
        """
        slug_map = {
            str(self.GLOBALLY): "GLOBALLY",
            str(self.BEFORE): "BEFORE",
            str(self.AFTER): "AFTER",
            str(self.BETWEEN): "BETWEEN",
            str(self.AFTER_UNTIL): "AFTER_UNTIL",
            str(self.NONE): "NONE",
        }
        return slug_map[self.__str__()]

    def __str__(self):
        result = str(self.value).replace('"', "")
        return result

    def get_allowed_types(self):
        scope_env = {
            "GLOBALLY": {},
            "BEFORE": {"P": [boogie_parsing.BoogieType.bool]},
            "AFTER": {"P": [boogie_parsing.BoogieType.bool]},
            "BETWEEN": {"P": [boogie_parsing.BoogieType.bool], "Q": [boogie_parsing.BoogieType.bool]},
            "AFTER_UNTIL": {"P": [boogie_parsing.BoogieType.bool], "Q": [boogie_parsing.BoogieType.bool]},
            "NONE": {},
        }
        return scope_env[self.name]
