from unittest import TestCase

from guesser.reqsyntaxtree import ReqSyntaxTree, ReqTransformer
from guesser.utils import flatten_list

reqs = [
    "IF if_case THEN then_case",  # 1
    "IF if_case THEN then_case ELSE else_case",  # 2
    "IF if_case THEN IF then_if THEN then_then",  # 3
    "IF (OR-logic) x == y THEN x := y + 1",  # 4
    'IF (AND-logic) x == "TRUE"\ny == "TRUE"\nz == "FALSE" THEN z == "TRUE"',  # 5
    "x := y",  # 6
    'IF adp_Lichtsensor_Typ == "LIN_REGEN_LICHT_SENSOR" '
    "THEN s_hmi_afl_autobahn_aktiv := s_pBAP_ExteriorLight.LightOnHighway.Status "
    'ELSE s_hmi_afl_autobahn_aktiv := "FALSE"',  # 7
    'IF (AND-logic) x == "TRUE"\ny == "TRUE"\n((z == "FALSE" && w) || d) THEN z == "TRUE"',  # 8
    'adp_Lichtsensor_Typ == "LIN_REGEN_LICHT_SENSOR"',  # 9
    'IF (AND-logic)\nadp_Lichtsensor_Typ != "LIN_REGEN_LICHT_SENSOR"\n'
    'adp_Maskierung_Regenfunktion != "nicht aktiv"\n'
    'THEN\nso_RLS_01__RS_Verbau_KCAN := "Regensensor nicht verbaut"\n'
    'so_RLS_01__RS_Verbau_SCAN := "Regensensor nicht verbaut"',  # 10
    "IF (AND-logic)\n"
    'adp_Lichtsensor_Typ == "LIN_REGEN_LICHT_SENSOR"\n'
    'si_RLSs_01__LS_Dunkel_LIN1 == "Dunkel"\n'
    "THEN\n"
    's_mvb_Licht_ein_bei_Dunkelheit := "Aus"',  # 11
    "IF\n"
    "s_ls_in_lux_messwert  > 7000 lx\n"
    "THEN\n"
    "so_RLS_01__SLS_Helligkeit_IR_KCAN := 7000 lx\n"
    "so_RLS_01__SLS_Helligkeit_IR_SCAN := 7000 lx",  # 12
    "IF (AND-logic)\n"
    'adp_Lichtsensor_Typ == "SMART_LS"\n'
    "s_helligkeit_uin_mM <= adp_s_outmax\n"
    "THEN\n"
    "s_ls_anaout := s_helligkeit_uin_mM\n"
    "s_ls_in :=  ((adp_s_outmax - s_ls_anaout) * (adp_s_inpmax - adp_s_inpmin) / (adp_s_outmax - adp_s_outmin))\n"
    "s_ls_in_lux_messwert := s_ls_in",  # 13
    "set condition active for VAR1\n"
    "VAR2 is received\n"
    "VAR3 received\n"
    "VAR4 is not received\n"
    "VAR5 not received\n"
    "VAR6 is available\n"
    "VAR7 available\n"
    "VAR8 is not available\n"
    "VAR9 not available",  # 14
]

results = [
    [{"if_part": ["if_case"], "logic": "AND-logic", "then_part": ["then_case"]}],  # 1
    [{"if_part": ["if_case"], "logic": "AND-logic", "then_part": ["then_case"], "else_part": ["else_case"]}],
    # 2
    [
        {
            "if_part": ["if_case"],
            "logic": "AND-logic",
            "then_part": [{"if_part": ["then_if"], "logic": "AND-logic", "then_part": ["then_then"]}],
        }
    ],  # 3
    [{"if_part": ["x == y"], "logic": "OR-logic", "then_part": ["x := y + 1"]}],  # 4
    [{"if_part": ["x", "y", "!z"], "logic": "AND-logic", "then_part": ["z"]}],  # 5
    ["x := y"],  # 6
    [
        {
            "then_part": ["s_hmi_afl_autobahn_aktiv := s_pBAP_ExteriorLight.LightOnHighway.Status"],
            "else_part": ["!s_hmi_afl_autobahn_aktiv"],
            "if_part": ["adp_Lichtsensor_Typ == adp_Lichtsensor_Typ_LIN_REGEN_LICHT_SENSOR "],
            "logic": "AND-logic",
        }
    ],  # 7
    [{"if_part": ["x", "y", "( ( !z && w ) || d )"], "logic": "AND-logic", "then_part": ["z"]}],  # 8
    ["adp_Lichtsensor_Typ == adp_Lichtsensor_Typ_LIN_REGEN_LICHT_SENSOR "],  # 9
    [
        {
            "then_part": [
                "so_RLS_01__RS_Verbau_KCAN := so_RLS_01__RS_Verbau_KCAN_REGENSENSOR NICHT VERBAUT ",
                "so_RLS_01__RS_Verbau_SCAN := so_RLS_01__RS_Verbau_SCAN_REGENSENSOR NICHT VERBAUT ",
            ],
            "if_part": [
                "adp_Lichtsensor_Typ != adp_Lichtsensor_Typ_LIN_REGEN_LICHT_SENSOR ",
                "adp_Maskierung_Regenfunktion != adp_Maskierung_Regenfunktion_NICHT AKTIV ",
            ],
            "logic": "AND-logic",
        }
    ],  # 10
    [
        {
            "if_part": [
                "adp_Lichtsensor_Typ == adp_Lichtsensor_Typ_LIN_REGEN_LICHT_SENSOR ",
                "si_RLSs_01__LS_Dunkel_LIN1 == si_RLSs_01__LS_Dunkel_LIN1_DUNKEL ",
            ],
            "logic": "AND-logic",
            "then_part": ["s_mvb_Licht_ein_bei_Dunkelheit := s_mvb_Licht_ein_bei_Dunkelheit_AUS "],
        }
    ],  # 11
    [
        {
            "then_part": ["so_RLS_01__SLS_Helligkeit_IR_KCAN := 7000", "so_RLS_01__SLS_Helligkeit_IR_SCAN := 7000"],
            "if_part": ["s_ls_in_lux_messwert > 7000"],
            "logic": "AND-logic",
        }
    ],  # 12
    [
        {
            "logic": "AND-logic",
            "then_part": [
                "s_ls_anaout := s_helligkeit_uin_mM",
                "s_ls_in := ( ( adp_s_outmax - s_ls_anaout ) * ( adp_s_inpmax - adp_s_inpmin ) / ( "
                "adp_s_outmax - adp_s_outmin ) )",
                "s_ls_in_lux_messwert := s_ls_in",
            ],
            "if_part": ["adp_Lichtsensor_Typ == adp_Lichtsensor_Typ_SMART_LS ", "s_helligkeit_uin_mM <= adp_s_outmax"],
        }
    ],  # 13
    ["VAR1", "VAR2", "VAR3", "VAR4", "VAR5", "VAR6", "VAR7", "VAR8", "VAR9"],
]


class TestReqTransformer(TestCase):
    def test_transform(self):
        s = ReqSyntaxTree()
        transformer = ReqTransformer()
        for i, req in enumerate(reqs):
            s.create_tree(req)
            new_tree = transformer.transform(s.tree)
            flattend_list = list(flatten_list(new_tree.children))
            # self.assertEqual(flattend_list, results[i])
