from unittest import TestCase
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, DatabaseFieldType, JsonDatabase, \
    is_serializable
from uuid import UUID
from os import path, mkdir, rmdir, remove


class TestJsonDatabase(TestCase):

    def setUp(self) -> None:
        DatabaseTable.registry.clear()
        DatabaseID.registry.clear()
        DatabaseField.registry.clear()
        DatabaseFieldType.registry.clear()
        self._db = JsonDatabase()
        self._data_path = path.join(path.dirname(path.realpath(__file__)), 'test_json_database', 'test_data')
        if not path.isdir(path.join(self._data_path, 'init_tables_ok')):
            mkdir(path.join(self._data_path, 'init_tables_ok'))

    def tearDown(self):
        if path.isdir(path.join(self._data_path, 'init_tables_ok', 'TestClassFolder')):
            rmdir(path.join(self._data_path, 'init_tables_ok', 'TestClassFolder'))
        if path.isfile(path.join(self._data_path, 'init_tables_ok', 'TestClassFile.json')):
            remove(path.join(self._data_path, 'init_tables_ok', 'TestClassFile.json'))

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
                                            TestClassUuid: ('', UUID)}
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

    def test_json_db_init_tables_ok(self):
        from test_json_database.db_test_simple_table import TestClassFile, TestClassFolder, TestClassFieldType
        _ = TestClassFile
        _ = TestClassFolder
        _ = TestClassFieldType
        self._db.init_tables(path.join(self._data_path, 'init_tables_ok'))
        tables_dict = {TestClassFile: ('file', 'job_id', str, {
            'att_bool': bool,
            'att_str': str,
            'att_int': int,
            'att_float': float,
            'att_tuple': tuple[int, str],
            'att_list': list[str],
            'att_dict': dict[int, str],
            'att_set': set[int]
        }),
                       TestClassFolder: ('folder', 'job_id', int,
                                         {'att_bool': bool,
                                          'att_str': str,
                                          'att_int': int,
                                          'att_float': float,
                                          'att_class_file': TestClassFile
                                          })
                       }
        self.assertDictEqual(self._db._tables, tables_dict)
        field_type_dict = {TestClassFieldType: {'job_id': str}}
        self.assertDictEqual(self._db._field_types, field_type_dict)
        self.assertTrue(path.isdir(path.join(self._data_path, 'init_tables_ok', 'TestClassFolder')))
        self.assertTrue(path.isfile(path.join(self._data_path, 'init_tables_ok', 'TestClassFile.json')))

    def test_json_db_init_tables_table_and_field_type(self):
        from test_json_database.db_test_init_tables_table_and_type import TestClass, TestClassTable, TestClassFieldType
        _ = TestClass
        _ = TestClassTable
        _ = TestClassFieldType
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following classes are marked as DatabaseTable and DatabaseFieldType:\n'
                         '{<class \'test_json_database.db_test_init_tables_table_and_type.TestClass\'>}',
                         str(em.exception))

    def test_json_db_init_tables_table_without_id(self):
        from test_json_database.db_test_init_tables_table_without_id import TestClass, TestClassWithoutID
        _ = TestClass
        _ = TestClassWithoutID
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following classes are marked as DatabaseTable but don\'t have an id field:\n'
                         '{<class \'test_json_database.db_test_init_tables_table_without_id.TestClassWithoutID\'>}',
                         str(em.exception))

    def test_json_db_init_tables_id_without_table(self):
        from test_json_database.db_test_init_tables_id_without_table import TestClass, TestClassWithoutTable
        _ = TestClass
        _ = TestClassWithoutTable
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following classes are marked with an id field but not as an DatabaseTable:\n'
                         '{<class \'test_json_database.db_test_init_tables_id_without_table.TestClassWithoutTable\'>}',
                         str(em.exception))

    def test_json_db_init_tables_fields_without_table(self):
        from test_json_database.db_test_init_tables_fields_without_table import TestClass, TestClassWithoutTable
        _ = TestClass
        _ = TestClassWithoutTable
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following classes are marked with fields but not as an DatabaseTable or '
                         'DatabaseFieldType:\n'
                         '{<class \'test_json_database.db_test_init_tables_fields_without_table.'
                         'TestClassWithoutTable\'>}',
                         str(em.exception))

    def test_json_db_init_tables_table_without_fields(self):
        from test_json_database.db_test_init_tables_table_without_fields import TestClass, TestClassWithoutFields
        _ = TestClass
        _ = TestClassWithoutFields
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following classes are marked as DatabaseTable but don\'t have any fields:\n'
                         '{<class \'test_json_database.db_test_init_tables_table_without_fields.'
                         'TestClassWithoutFields\'>}',
                         str(em.exception))

    def test_json_db_init_tables_field_type_without_fields(self):
        from test_json_database.db_test_init_tables_field_type_without_fields import TestClass, TestClassWithoutFields
        _ = TestClass
        _ = TestClassWithoutFields
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following classes are marked as DatabaseFieldType but don\'t have any fields:\n'
                         '{<class \'test_json_database.db_test_init_tables_field_type_without_fields.'
                         'TestClassWithoutFields\'>}',
                         str(em.exception))

    def test_json_db_init_tables_unserializable_fields(self):
        from test_json_database.db_test_init_tables_unserializable_fields import TestClassFile, TestClassFolder
        _ = TestClassFile
        _ = TestClassFolder
        with self.assertRaises(Exception) as em:
            self._db.init_tables(self._data_path)
        self.assertEqual('The following type of class <class \'test_json_database.'
                         'db_test_init_tables_unserializable_fields.TestClassFolder\'> is not serializable:\n'
                         'att_class_file: <class \'json_db_connector.json_db.DatabaseTable\'>',
                         str(em.exception))

    def test_json_db_is_serializable_function(self):
        res = is_serializable(DatabaseTable)
        self.assertFalse(res[0])
        self.assertEqual(res[1], '<class \'json_db_connector.json_db.DatabaseTable\'>')
        res = is_serializable(bool)
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(str)
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(int)
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(float)
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(tuple[int, float, str])
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(tuple[int, float, DatabaseTable])
        self.assertFalse(res[0])
        self.assertEqual(res[1], '<class \'json_db_connector.json_db.DatabaseTable\'>')
        res = is_serializable(list[int])
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(list[int | float])
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(list[DatabaseTable])
        self.assertFalse(res[0])
        self.assertEqual(res[1], '<class \'json_db_connector.json_db.DatabaseTable\'>')
        res = is_serializable(dict[int, str])
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(set[int])
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(DatabaseTable, [DatabaseTable])
        self.assertTrue(res[0])
        self.assertEqual(res[1], '')
        res = is_serializable(DatabaseTable, [DatabaseField])
        self.assertFalse(res[0])
        self.assertEqual(res[1], '<class \'json_db_connector.json_db.DatabaseTable\'>')
