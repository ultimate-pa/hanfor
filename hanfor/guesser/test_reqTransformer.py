from unittest import TestCase
from guesser.reqsyntaxtree import ReqSyntaxTree,ReqTransformer
from guesser.utils import flatten_list

reqs = ['IF if_case THEN then_case', #1
        'IF if_case THEN then_case ELSE else_case', #2
        'IF if_case THEN IF then_if THEN then_then', #3
        'IF (OR-logic) x == y THEN x := y + 1', #4
        'IF (AND-logic) x == "TRUE"\ny == "TRUE"\nz == "FALSE" THEN z == "TRUE"', #5
        'x := y', #6
        'IF adp_Lichtsensor_Typ == "LIN_REGEN_LICHT_SENSOR" '
        'THEN s_hmi_afl_autobahn_aktiv := s_pBAP_ExteriorLight.LightOnHighway.Status '
        'ELSE s_hmi_afl_autobahn_aktiv := "FALSE"', #7
        'IF (AND-logic) x == "TRUE"\ny == "TRUE"\n((z == "FALSE" && w) || d) THEN z == "TRUE"', #8
       ]

results = [[{'if_part': ['if_case'], 'then_part': ['then_case']}], #1
           [{'if_part': ['if_case'], 'then_part': ['then_case'], 'else_part': ['else_case']}], #2
           [{'if_part': ['if_case'], 'then_part': [{'if_part': ['then_if'], 'then_part': ['then_then']}]}], #3
           [{'if_part': ['x == y'], 'then_part': ['x := y + 1']}], #4
           [{'if_part': ['x == "TRUE"', 'y == "TRUE"', 'z == "FALSE"'], 'then_part': ['z == "TRUE"']}], #5
           ['x := y'], #6
           [{'else_part': ['s_hmi_afl_autobahn_aktiv := "FALSE"'],
             'then_part': ['s_hmi_afl_autobahn_aktiv := s_pBAP_ExteriorLight.LightOnHighway.Status'],
             'if_part': ['adp_Lichtsensor_Typ == "LIN_REGEN_LICHT_SENSOR"']}], #87
           [{'if_part': ['x == "TRUE"', 'y == "TRUE"', '( ( z == "FALSE" && w ) || d )'], 'then_part': ['z == "TRUE"']}], #8
           ]


class TestReqTransformer(TestCase):
    def test_transform(self):
        s = ReqSyntaxTree()
        transformer = ReqTransformer()
        for i, req in enumerate(reqs):
            s.create_tree(req)
            new_tree = transformer.transform(s.tree)
            flattend_list = list(flatten_list(new_tree.children))
            self.assertEqual(flattend_list,results[i])

