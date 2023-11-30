from unittest import TestCase
from json_db_connector.json_db import DatabaseTable


class TestJsonDatabase(TestCase):

    def setUp(self):
        # reset all json db decorator classes
        DatabaseTable.registry.clear()

    def test_table_decorator(self):
        # test table definition without brackets
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_table_decorator_without_brackets import TestClass
            _ = TestClass
        self.assertEqual('DatabaseTable must be set to file or folder: <class '
                         '\'test_json_database.db_test_table_decorator_without_brackets.TestClass\'>',
                         str(em.exception))

        # test table definition without arguments
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_table_decorator_without_arguments import TestClass
            _ = TestClass
        self.assertEqual('DatabaseTable must be set to file or folder: <class '
                         '\'test_json_database.db_test_table_decorator_without_arguments.TestClass\'>',
                         str(em.exception))

        # test table definition with file and folder argument
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_table_decorator_with_file_and_folder_argument import TestClass
            _ = TestClass
        self.assertEqual('DatabaseTable must be set to file or folder: <class '
                         '\'test_json_database.db_test_table_decorator_with_file_and_folder_argument.TestClass\'>',
                         str(em.exception))

        # test well-formed definition for file and folder
        from test_json_database.db_test_simple_table import TestClassFile, TestClassFolder
        _ = TestClassFile
        _ = TestClassFolder
        classes_dict: dict[str, str] = {'TestClassFile': 'file', 'TestClassFolder': 'folder'}
        self.assertDictEqual(DatabaseTable.registry, classes_dict)

        # test duplicated name of table
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_simple_table_duplicate import TestClassFile
            _ = TestClassFile
        self.assertEqual('DatabaseTable with name TestClassFile already exists.',
                         str(em.exception))

    def tearDown(self):
        pass
