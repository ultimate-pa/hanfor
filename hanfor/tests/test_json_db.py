from unittest import TestCase
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, DatabaseFieldType
from uuid import UUID


class TestJsonDatabase(TestCase):

    def setUp(self) -> None:
        DatabaseTable.registry.clear()
        DatabaseID.registry.clear()
        DatabaseField.registry.clear()
        DatabaseFieldType.registry.clear()

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
        from test_json_database.db_test_table_decorator_simple import TestClassFile, TestClassFolder
        _ = TestClassFile
        _ = TestClassFolder
        classes_dict: dict[type, str] = {TestClassFile: 'file', TestClassFolder: 'folder'}
        self.assertDictEqual(DatabaseTable.registry, classes_dict)

        # test duplicated name of table
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_simple_table_duplicate import TestClassFile
            _ = TestClassFile
        self.assertEqual('DatabaseTable with name TestClassFile already exists.',
                         str(em.exception))

    def test_id_decorator(self):
        # test id definition without brackets
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_without_brackets import TestClass
            _ = TestClass
        self.assertEqual('DatabaseID must be set to the name and type of an field of the class: <class '
                         '\'test_json_database.db_test_id_decorator_without_brackets.TestClass\'>',
                         str(em.exception))

        # test id definition without arguments
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_without_arguments import TestClass
            _ = TestClass
        self.assertEqual('DatabaseID must be set to the name and type of an field of the class: <class '
                         '\'test_json_database.db_test_id_decorator_without_arguments.TestClass\'>',
                         str(em.exception))

        # test id definition with 1 incorrect argument
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_with_1_incorrect_argument import TestClass
            _ = TestClass
        self.assertEqual('Name of DatabaseID must be of type str: <class '
                         '\'test_json_database.db_test_id_decorator_with_1_incorrect_argument.TestClass\'>',
                         str(em.exception))

        # test id definition with 1 correct argument
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_with_1_argument import TestClass
            _ = TestClass
        self.assertEqual('Type of DatabaseID must be provided: <class '
                         '\'test_json_database.db_test_id_decorator_with_1_argument.TestClass\'>',
                         str(em.exception))

        # test id definition with 1 correct argument and 1 incorrect argument
        # test with str object instead of type object
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_with_2_incorrect_arguments import TestClass
            _ = TestClass
        self.assertEqual('Type of DatabaseID must be of type type: <class '
                         '\'test_json_database.db_test_id_decorator_with_2_incorrect_arguments.TestClass\'>',
                         str(em.exception))

        # test with float type
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_with_2_incorrect_arguments_2 import TestClass
            _ = TestClass
        self.assertEqual('Type of DatabaseID must be of type str or int: <class '
                         '\'test_json_database.db_test_id_decorator_with_2_incorrect_arguments_2.TestClass\'>',
                         str(em.exception))

        # test well-formed definition for id
        from test_json_database.db_test_id_decorator_simple import TestClassFile, TestClassFolder, TestClassUuid
        _ = TestClassFile
        _ = TestClassFolder
        _ = TestClassUuid
        id_dict: dict[type, (str, type)] = {TestClassFile: ('job_id', str),
                                            TestClassFolder: ('job_id', int),
                                            TestClassUuid: (None, UUID)}
        self.assertDictEqual(DatabaseID.registry, id_dict)

        # test id definition with 2 decorators
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_with_2_decorators import TestClass
            _ = TestClass
        self.assertEqual('DatabaseTable with name <class '
                         '\'test_json_database.db_test_id_decorator_with_2_decorators.TestClass\'> '
                         'already has an id field.',
                         str(em.exception))

    def test_field_decorator(self):
        # test field definition without brackets
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_decorator_without_brackets import TestClass
            _ = TestClass
        self.assertEqual('DatabaseField must be set to the name and type of an field of the class: <class '
                         '\'test_json_database.db_test_field_decorator_without_brackets.TestClass\'>',
                         str(em.exception))

        # test id definition without arguments
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_decorator_without_arguments import TestClass
            _ = TestClass
        self.assertEqual('DatabaseField must be set to the name and type of an field of the class: <class '
                         '\'test_json_database.db_test_field_decorator_without_arguments.TestClass\'>',
                         str(em.exception))

        # test id definition with 1 incorrect argument
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_decorator_with_1_incorrect_argument import TestClass
            _ = TestClass
        self.assertEqual('Name of DatabaseField must be of type str: <class '
                         '\'test_json_database.db_test_field_decorator_with_1_incorrect_argument.TestClass\'>',
                         str(em.exception))

        # test id definition with 1 correct argument
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_decorator_with_1_argument import TestClass
            _ = TestClass
        self.assertEqual('Type of DatabaseField must be provided: <class '
                         '\'test_json_database.db_test_field_decorator_with_1_argument.TestClass\'>',
                         str(em.exception))

        # test id definition with 1 correct argument and 1 incorrect argument
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_decorator_with_2_incorrect_arguments import TestClass
            _ = TestClass
        self.assertEqual('Type of DatabaseField must be of type type: <class '
                         '\'test_json_database.db_test_field_decorator_with_2_incorrect_arguments.TestClass\'>',
                         str(em.exception))

        # test id definition with 2 decorators
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_decorator_with_2_decorators import TestClass
            _ = TestClass
        self.assertEqual('DatabaseField with name job_id already exists in class <class '
                         '\'test_json_database.db_test_field_decorator_with_2_decorators.TestClass\'>.',
                         str(em.exception))

        DatabaseField.registry.clear()

        # test well-formed definition for id
        from test_json_database.db_test_field_decorator_simple import TestClassFile, TestClassFolder
        _ = TestClassFile
        _ = TestClassFolder
        field_dict: dict[type, dict[str, any]] = {TestClassFile: {'att_bool': bool,
                                                                  'att_str': str,
                                                                  'att_int': int,
                                                                  'att_float': float,
                                                                  'att_tuple': tuple[int, str],
                                                                  'att_list': list[str],
                                                                  'att_dict': dict[int, str],
                                                                  'att_set': set[int]
                                                                  },
                                                  TestClassFolder: {'att_bool': bool,
                                                                    'att_str': str,
                                                                    'att_int': int,
                                                                    'att_float': float,
                                                                    'att_class_file': TestClassFile
                                                                    }
                                                  }
        self.assertDictEqual(DatabaseField.registry, field_dict)

    def test_field_type_decorator(self):
        # test field definition without brackets
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_type_decorator_without_brackets import TestClass
            _ = TestClass
        self.assertEqual('DatabaseFieldType must be called with brackets: <class '
                         '\'test_json_database.db_test_field_type_decorator_without_brackets.TestClass\'>',
                         str(em.exception))

        # test well-formed database field type definition
        from test_json_database.db_test_field_type_decorator_simple import TestClass
        _ = TestClass
        type_set: set[type] = {TestClass}
        self.assertSetEqual(DatabaseFieldType.registry, type_set)
