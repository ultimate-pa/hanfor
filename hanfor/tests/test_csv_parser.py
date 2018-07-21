from hanfor import db
from hanfor.boogie_parsing import boogie_parsing
from hanfor.models import Tag, Variable, Expression, CsvEntry, CsvHeaderEntry, Requirement
from hanfor.tests.test_environment import TestEnvironment
from hanfor.utils.csv_parser import CsvParser
from unittest.mock import patch


def mock_user_input(*args, **kwargs) -> str:
    """ Mocks user input. Returns the mock_results entry at position given by the number of calls.

    :return: mock_results[#of call starting with 0]
    """
    global mock_results
    global count
    try:
        count += 1
    except:
        count = 0

    result = mock_results[count]
    print('Mocked input: {}'.format(result))
    return str(result)


class TestCsvParser(TestEnvironment):

    def test_creating_headers(self):
        csv_parser = CsvParser()
        csv_parser.csv_meta['headers'] = ['header_1', 'header_2', 'header_3', 'header_4']
        csv_parser.store_csv_headers_to_db()
        for order, header_name in enumerate(csv_parser.csv_meta['headers']):
            header = CsvHeaderEntry().query.filter_by(text=header_name, order=order).first()
            self.assertTrue(header is not None)

        csv_parser.csv_meta['headers'] = ['header_3', 'header_1']
        csv_parser.store_csv_headers_to_db()
        for order, header_name in enumerate(csv_parser.csv_meta['headers']):
            header = CsvHeaderEntry().query.filter_by(text=header_name, order=order).first()
            self.assertTrue(header is not None)

    @patch('builtins.input', mock_user_input)
    def test_create_from_csv(self):
        global mock_results
        mock_results = [0, 1, 3, 2]

        csv_parser = CsvParser()
        csv_parser.create_from_csv('test_csv.csv')

        expected_results = {
            'Requirement_1': {'description': 'Description of Requirement_1', 'type': 'Some_type_1'},
            'Requirement_2': {'description': 'Description of Requirement_2', 'type': 'Some_type_2'}
        }

        requirements = Requirement().query.all()

        # Ensure, that all requirements exist.
        self.assertEqual(len(expected_results), len(requirements))
        self.assertEqual(set(expected_results.keys()), {requirement.rid for requirement in requirements})

        # Ensure, that the entries are correct.
        for requirement in requirements:
            self.assertEqual(expected_results[requirement.rid]['description'], requirement.description)
            self.assertEqual(expected_results[requirement.rid]['type'], requirement.type)

        # Store, so one can further inspect the test DB.
        db.session.commit()
