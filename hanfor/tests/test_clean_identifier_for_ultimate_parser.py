"""
Test cleaning slugs to be sound identifier to be used in ultimate.

Purpose of clean_identifier_for_ultimate_parser is to translate slugs used as requirement identifier to be sound in
ultimate.
Given a set of already used_identifiers, clean_identifier_for_ultimate_parser should return for a new (str) slug:
* A version of slug not already in used_identifiers by adding _{incrementing int}
* Preceding ints to ID_, whitespace to _, remove .

"""
from unittest import TestCase

from utils import clean_identifier_for_ultimate_parser


class TestClean_identifier_for_ultimate_parser(TestCase):
    def test_clean_identifier_for_ultimate_parser_whitespace(self):
        slug = 'This is  a  Test\n'
        used_slugs = {'foo'}
        new_slug, new_used_slugs = clean_identifier_for_ultimate_parser(slug, used_slugs)
        self.assertEqual('This_is_a_Test', new_slug)
        self.assertEqual({'foo', 'This_is_a_Test'}, new_used_slugs)

    def test_clean_identifier_for_ultimate_parser_name_occupied(self):
        slug = 'This is a Test'
        used_slugs = {'This_is_a_Test', 'This_is_a_Test_1'}
        new_slug, new_used_slugs = clean_identifier_for_ultimate_parser(slug, used_slugs)
        self.assertEqual('This_is_a_Test_2', new_slug)
        self.assertEqual({'This_is_a_Test', 'This_is_a_Test_1', 'This_is_a_Test_2'}, new_used_slugs)

    def test_clean_identifier_for_ultimate_parser_illegal_start(self):
        slug = '0This is a Test'
        used_slugs = set()
        new_slug, new_used_slugs = clean_identifier_for_ultimate_parser(slug, used_slugs)
        self.assertEqual('ID_This_is_a_Test', new_slug)
        self.assertEqual({'ID_This_is_a_Test'}, new_used_slugs)

    def test_clean_identifier_for_ultimate_parser_illegal_chars(self):
        slug = '\n\nThis . - . is.a-Test   '
        used_slugs = set()
        new_slug, new_used_slugs = clean_identifier_for_ultimate_parser(slug, used_slugs)
        self.assertEqual('This_is_a_Test', new_slug)
        self.assertEqual({'This_is_a_Test'}, new_used_slugs)
