from unittest import TestCase
from boogie_parsing import BoogieType


class TestBoogieType(TestCase):

    def test_alias(self):
        map = {
            BoogieType.int: {'int', 'ENUMERATOR', 'ENUM'},
            BoogieType.unknown: {'unknown'},
            BoogieType.bool: {'bool'},
            BoogieType.real: {'real'}
        }

        for type, aliases in map.items():
            self.assertEqual(aliases, BoogieType.aliases(type))

    def test_reverse_alias(self):
        map = {
            'ENUMERATOR': BoogieType.int,
            'Fancy': BoogieType.unknown,
            BoogieType.int.name: BoogieType.int,
            BoogieType.bool.name: BoogieType.bool,
            BoogieType.real.name: BoogieType.real
        }

        for alias_name, alias_type in map.items():
            self.assertEqual(
                alias_type,
                BoogieType.reverse_alias(alias_name),
                msg='Alias name {} should derive {}'.format(alias_name, alias_type)
            )
