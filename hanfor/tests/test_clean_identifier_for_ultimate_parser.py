"""
Test cleaning requirement_ids with formalisation_ids to be sound identifier to be used in ultimate.

Purpose of clean_identifier_for_ultimate_parser is to translate requirement_ids and formalisation_ids used as
requirement identifier to be sound in ultimate.
Given a set of already used_identifiers, clean_identifier_for_ultimate_parser should return for a new (str)
requirement_id and formalisation_id:
* A version of identifier not already in used_identifiers by adding _{incrementing int} to the requirement_id
* Preceding ints to ID_, whitespace to _, remove .

"""

from unittest import TestCase

from utils import clean_identifier_for_ultimate_parser


class TestCleanIdentifierForUltimateParser(TestCase):
    def test_clean_identifier_for_ultimate_parser_whitespace(self):
        req_id = "This is  a  Test\n"
        used_identifiers = {"foo"}
        identifier = clean_identifier_for_ultimate_parser(req_id, 0, used_identifiers)
        self.assertEqual("This_is_a_Test_0", identifier)
        self.assertEqual({"foo", "This_is_a_Test_0"}, used_identifiers)

    def test_clean_identifier_for_ultimate_parser_name_occupied(self):
        req_id = "This is a Test"
        used_identifiers = {"This_is_a_Test_0", "This_is_a_Test_1"}
        identifier = clean_identifier_for_ultimate_parser(req_id, 0, used_identifiers)
        self.assertEqual("This_is_a_Test_1_0", identifier)
        self.assertEqual({"This_is_a_Test_0", "This_is_a_Test_1", "This_is_a_Test_1_0"}, used_identifiers)

    def test_clean_identifier_for_ultimate_parser_illegal_start(self):
        req_id = "0This is a Test"
        used_identifiers = set()
        identifier = clean_identifier_for_ultimate_parser(req_id, 0, used_identifiers)
        self.assertEqual("ID_0This_is_a_Test_0", identifier)
        self.assertEqual({"ID_0This_is_a_Test_0"}, used_identifiers)

    def test_clean_identifier_for_ultimate_parser_illegal_chars(self):
        req_id = "\n\nThis . - . is.a-Test   "
        used_identifiers = set()
        identifier = clean_identifier_for_ultimate_parser(req_id, 0, used_identifiers)
        self.assertEqual("This_is_a_Test_0", identifier)
        self.assertEqual({"This_is_a_Test_0"}, used_identifiers)
