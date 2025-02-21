from unittest import TestCase
from lib_core.boogie_parsing import BoogieType


class TestBoogieType(TestCase):

    def test_alias(self):
        mapping = {
            BoogieType.int: {"int", "ENUMERATOR_INT", "ENUM_INT"},
            BoogieType.unknown: {"unknown"},
            BoogieType.bool: {"bool"},
            BoogieType.real: {"real", "ENUMERATOR_REAL", "ENUM_REAL"},
        }

        for boogie_type, aliases in mapping.items():
            self.assertEqual(aliases, BoogieType.aliases(boogie_type))

    def test_reverse_alias(self):
        mapping = {
            "ENUMERATOR_INT": BoogieType.int,
            "ENUM_INT": BoogieType.int,
            "ENUMERATOR_REAL": BoogieType.real,
            "ENUM_REAL": BoogieType.real,
            "Fancy": BoogieType.unknown,
            BoogieType.int.name: BoogieType.int,
            BoogieType.bool.name: BoogieType.bool,
            BoogieType.real.name: BoogieType.real,
        }

        for alias_name, alias_type in mapping.items():
            self.assertEqual(
                alias_type,
                BoogieType.reverse_alias(alias_name),
                msg="Alias name {} should derive {}".format(alias_name, alias_type),
            )
