from unittest import TestCase
from json_db_connector.json_db import JsonDatabase, is_serializable, TableType, DatabaseTable, DatabaseID, \
    DatabaseField, DatabaseFieldType
from uuid import UUID
from os import path, rmdir, remove
from dataclasses import dataclass
import json


class TestJsonDatabase(TestCase):

    def setUp(self) -> None:
        self.maxDiff = None
        DatabaseTable.registry.clear()
        DatabaseID.registry.clear()
        DatabaseField.registry.clear()
        DatabaseFieldType.registry.clear()
        self._db = JsonDatabase()
        self._data_path = path.join(path.dirname(path.realpath(__file__)), 'test_json_database', 'test_data')

    def tearDown(self):
        if path.isdir(path.join(self._data_path, 'init_tables_ok', 'TestClassFolder')):
            rmdir(path.join(self._data_path, 'init_tables_ok', 'TestClassFolder'))
        if path.isfile(path.join(self._data_path, 'init_tables_ok', 'TestClassFile.json')):
            remove(path.join(self._data_path, 'init_tables_ok', 'TestClassFile.json'))
        if path.isdir(path.join(self._data_path, 'init_tables_ok')):
            rmdir(path.join(self._data_path, 'init_tables_ok'))

        if path.isfile(path.join(self._data_path, 'data_to_json', 'TestClassFile.json')):
            remove(path.join(self._data_path, 'data_to_json', 'TestClassFile.json'))
        if path.isfile(path.join(self._data_path, 'data_to_json', 'TestClassReference.json')):
            remove(path.join(self._data_path, 'data_to_json', 'TestClassReference.json'))
        if path.isdir(path.join(self._data_path, 'data_to_json')):
            rmdir(path.join(self._data_path, 'data_to_json'))

        if path.isfile(path.join(self._data_path, 'add_object', 'TestClass1.json')):
            remove(path.join(self._data_path, 'add_object', 'TestClass1.json'))
        if path.isfile(path.join(self._data_path, 'add_object', 'TestClass2.json')):
            remove(path.join(self._data_path, 'add_object', 'TestClass2.json'))
        if path.isfile(path.join(self._data_path, 'add_object', 'TestClass3.json')):
            remove(path.join(self._data_path, 'add_object', 'TestClass3.json'))
        if path.isfile(path.join(self._data_path, 'add_object', 'TestClass4.json')):
            remove(path.join(self._data_path, 'add_object', 'TestClass4.json'))
        if path.isdir(path.join(self._data_path, 'add_object')):
            rmdir(path.join(self._data_path, 'add_object'))

        if path.isfile(path.join(self._data_path, 'save', 'TestSzene', '0.json')):
            remove(path.join(self._data_path, 'save', 'TestSzene', '0.json'))
        if path.isfile(path.join(self._data_path, 'save', 'TestSzene', '1.json')):
            remove(path.join(self._data_path, 'save', 'TestSzene', '1.json'))
        if path.isdir(path.join(self._data_path, 'save', 'TestSzene')):
            rmdir(path.join(self._data_path, 'save', 'TestSzene'))
        if path.isfile(path.join(self._data_path, 'save', 'TestRectangle.json')):
            remove(path.join(self._data_path, 'save', 'TestRectangle.json'))
        if path.isfile(path.join(self._data_path, 'save', 'TestUUID.json')):
            remove(path.join(self._data_path, 'save', 'TestUUID.json'))
        if path.isdir(path.join(self._data_path, 'save')):
            rmdir(path.join(self._data_path, 'save'))

        if path.isfile(path.join(self._data_path, 'json_to_value', 'TestClassFile.json')):
            remove(path.join(self._data_path, 'json_to_value', 'TestClassFile.json'))
        if path.isfile(path.join(self._data_path, 'json_to_value', 'TestClassReference.json')):
            remove(path.join(self._data_path, 'json_to_value', 'TestClassReference.json'))
        if path.isdir(path.join(self._data_path, 'json_to_value')):
            rmdir(path.join(self._data_path, 'json_to_value'))

    def test_json_int_float(self):
        tmp = {'int': 0, 'float': 1.2, 'bool': True}
        self.assertEqual(json.dumps(tmp), '{"int": 0, "float": 1.2, "bool": true}')
        tmp = {'int': 0, 'float': 0.0}
        self.assertEqual(json.dumps(tmp), '{"int": 0, "float": 0.0}')
        loaded = json.loads('{"int": 0, "float": 0.0}')
        self.assertEqual(type(loaded['int']), int)
        self.assertEqual(type(loaded['float']), float)
        tmp = {'None': None}
        self.assertEqual(json.dumps(tmp), '{"None": null}')
        tmp = {'empty': []}
        self.assertEqual(json.dumps(tmp), '{"empty": []}')

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

        # test well-formed definition for file and folder
        from test_json_database.db_test_table_decorator_simple import TestClassFile, TestClassFolder
        _ = TestClassFile
        _ = TestClassFolder
        classes_dict: dict[type, TableType] = {TestClassFile: TableType.File, TestClassFolder: TableType.Folder}
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

        # test use_uuid without field name
        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_id_decorator_uuid_without_field import TestClassUuid
            _ = TestClassUuid
        self.assertEqual('DatabaseID must be set to the name and type of an field of the class: <class '
                         '\'test_json_database.db_test_id_decorator_uuid_without_field.TestClassUuid\'>',
                         str(em.exception))

        # test well-formed definition for id
        from test_json_database.db_test_id_decorator_simple import TestClassFile, TestClassFolder, TestClassUuid
        _ = TestClassFile
        _ = TestClassFolder
        _ = TestClassUuid
        id_dict: dict[type, (str, type)] = {TestClassFile: ('job_id', str),
                                            TestClassFolder: ('job_id', int),
                                            TestClassUuid: ('uuid', UUID)}
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
        field_dict: dict[type, dict[str, any]] = {TestClassFile: {'att_bool': (bool, None),
                                                                  'att_str': (str, None),
                                                                  'att_int': (int, None),
                                                                  'att_float': (float, None),
                                                                  'att_tuple': (tuple[int, str], None),
                                                                  'att_list': (list[str], None),
                                                                  'att_dict': (dict, None),
                                                                  'att_set': (set[int], None),
                                                                  },
                                                  TestClassFolder: {'att_bool': (bool, True),
                                                                    'att_str': (str, 'default'),
                                                                    'att_int': (int, 42),
                                                                    'att_float': (float, 3.14),
                                                                    'att_class_file': (TestClassFile, None),
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

        with self.assertRaises(Exception) as em:
            from test_json_database.db_test_field_type_decorator_simple_2 import TestClass as Tc2
            _ = Tc2
        self.assertEqual(f"Name of DatabaseFieldType exists already:\nexisting: {TestClass}\nnew     : <class "
                         "'test_json_database.db_test_field_type_decorator_simple_2.TestClass'>",
                         str(em.exception))

    def test_json_db_init_tables_ok(self):
        from test_json_database.db_test_simple_table import TestClassFile, TestClassFolder, TestClassFieldType
        _ = TestClassFile
        _ = TestClassFolder
        _ = TestClassFieldType
        self._db.init_tables(path.join(self._data_path, 'init_tables_ok'))
        self.assertTrue(TestClassFile in self._db._tables)
        self.assertTrue(TestClassFolder in self._db._tables)
        self.assertEqual(self._db._tables[TestClassFile].cls, TestClassFile)
        self.assertEqual(self._db._tables[TestClassFolder].cls, TestClassFolder)
        self.assertEqual(self._db._tables[TestClassFile].table_type, TableType.File)
        self.assertEqual(self._db._tables[TestClassFolder].table_type, TableType.Folder)
        self.assertEqual(self._db._tables[TestClassFile].id_field, 'job_id')
        self.assertEqual(self._db._tables[TestClassFolder].id_field, 'job_id')
        self.assertEqual(self._db._tables[TestClassFile].id_type, str)
        self.assertEqual(self._db._tables[TestClassFolder].id_type, int)
        self.assertDictEqual(self._db._tables[TestClassFile].fields, {'att_bool': (bool, None),
                                                                      'att_str': (str, None),
                                                                      'att_int': (int, None),
                                                                      'att_float': (float, None),
                                                                      'att_tuple': (tuple[int, str], None),
                                                                      'att_list': (list[str], None),
                                                                      'att_dict': (dict, None),
                                                                      'att_set': (set[int], None)
                                                                      })
        self.assertDictEqual(self._db._tables[TestClassFolder].fields, {'att_bool': (bool, True),
                                                                        'att_str': (str, 'default'),
                                                                        'att_int': (int, 42),
                                                                        'att_float': (float, 3.14),
                                                                        'att_class_file': (TestClassFile, None)
                                                                        })
        field_type_dict = {TestClassFieldType: {'job_id': (str, None)}}
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

    def test_json_db_add_object(self):
        from test_json_database.db_test_add_object import TestClass1, TestClass2, TestClass3, TestClass4

        @dataclass()
        class TestClass:
            f1: str

        self._db.init_tables(path.join(self._data_path, 'add_object'))

        # test class of object is not in database
        tmp = TestClass(f1='Hello World')
        with self.assertRaises(Exception) as em:
            self._db.add_object(tmp)
        self.assertEqual('<class \'test_json_db.TestJsonDatabase.test_json_db_add_object.<locals>.'
                         'TestClass\'> is not part of the Database.',
                         str(em.exception))

        # instance test objects
        tc1_1 = TestClass1(job_id='one', att_str='att')
        tc1_2 = TestClass1(job_id='two', att_str='att2')
        tc1_3 = TestClass1(job_id='three', att_str='att3')
        tc1_4 = TestClass1(job_id='', att_str='att4')
        tc1_5 = TestClass1(job_id='one', att_str='att5')
        tc1_6 = TestClass1(job_id=1, att_str='att5')  # noqa disables the waring for false type
        tc2_1 = TestClass2(job_id=1, att_int=10, att_ref=None)
        tc2_2 = TestClass2(job_id=2, att_int=20, att_ref=tc1_1)
        tc2_3 = TestClass2(job_id=3, att_int=30, att_ref=tc1_3)
        tc2_4 = TestClass2(job_id=None, att_int=40, att_ref=None)
        tc3_1 = TestClass3(att_str='uuid')
        tc4_1 = TestClass4(job_id=100, att_ref=tc3_1)

        table_objects = {t: self._db._tables[t].get_objects() for t in [TestClass1, TestClass2, TestClass3, TestClass4]}
        # add normal object
        self._db.add_object(tc1_1)
        data_id: dict[type, dict[int | str, object]] = {TestClass1: {'one': tc1_1}, TestClass2: {}, TestClass3: {},
                                                        TestClass4: {}}
        self.assertDictEqual(table_objects, data_id)
        # add object with empty reference field
        self._db.add_object(tc1_2)
        self._db.add_object(tc2_1)
        data_id[TestClass1]['two'] = tc1_2
        data_id[TestClass2][1] = tc2_1
        self.assertDictEqual(table_objects, data_id)
        # add object with filled reference field
        self._db.add_object(tc2_2)
        data_id[TestClass2][2] = tc2_2
        self.assertDictEqual(table_objects, data_id)
        # add object with filled reference field but with an unknown object -> test call add @ _data_to_json
        self._db.add_object(tc2_3)
        data_id[TestClass1]['three'] = tc1_3
        data_id[TestClass2][3] = tc2_3
        self.assertDictEqual(table_objects, data_id)
        # add object with uuid as id
        self._db.add_object(tc3_1)
        uid = self._db._tables[TestClass3].get_key_of_object(tc3_1)
        data_id[TestClass3][uid] = tc3_1
        self.assertDictEqual(table_objects, data_id)
        # add object with reference to an object with an uuid as id
        self._db.add_object(tc4_1)
        data_id[TestClass4][100] = tc4_1
        self.assertDictEqual(table_objects, data_id)
        # add object with empty str as id
        with self.assertRaises(Exception) as em:
            self._db.add_object(tc1_4)
        self.assertEqual(f"The id field \'job_id\' of object {tc1_4} is empty.",
                         str(em.exception))
        self.assertDictEqual(table_objects, data_id)
        # add object with None as id
        with self.assertRaises(Exception) as em:
            self._db.add_object(tc2_4)
        self.assertEqual(f"The id field \'job_id\' of object {tc2_4} is empty.",
                         str(em.exception))
        self.assertDictEqual(table_objects, data_id)
        # add object with already existing id
        with self.assertRaises(Exception) as em:
            self._db.add_object(tc1_5)
        self.assertEqual(f"The id \'one\' already exists in table {type(tc1_5)}.",
                         str(em.exception))
        self.assertDictEqual(table_objects, data_id)
        # add object with false type of id
        with self.assertRaises(Exception) as em:
            self._db.add_object(tc1_6)
        self.assertEqual(f"The id field \'job_id\' of object {tc1_6} is not of type \'{str}\'.",
                         str(em.exception))
        self.assertDictEqual(table_objects, data_id)

    def test_json_db_save(self):
        from test_json_database.db_test_save import TestColor, TestRectangle, TestSzene, SZENE1_JSON, SZENE0_JSON, \
            RECTANGLES_JSON, TestUUID, UUID1_JSON, UUID2_JSON
        blue = TestColor('blue', (0., 0., 1.))
        green = TestColor('green', (0., 1., 0.))
        rect0 = TestRectangle('rect0', True, {'x': 0, 'y': 0}, green)
        rect1 = TestRectangle('rect1', False, {'x': 1, 'y': 1}, blue)
        rect2 = TestRectangle('rect2', True, {'x': 2, 'y': 2}, None)
        szene0 = TestSzene(0, {'zero'}, [rect0, rect1, rect2])
        szene1 = TestSzene(1, {'one'}, [])
        uuid1 = TestUUID('one')
        uuid2 = TestUUID('two')
        self._db.init_tables(path.join(self._data_path, 'save'))
        self._db.add_object(szene1)
        with open(path.join(self._data_path, 'save', 'TestSzene', '1.json')) as tmp:
            data_szene1 = tmp.read()
        self.assertEqual(SZENE1_JSON, data_szene1)
        with open(path.join(self._data_path, 'save', 'TestRectangle.json')) as tmp:
            data_rectangles = tmp.read()
        self.assertEqual('{}', data_rectangles)
        self._db.add_object(szene0)
        with open(path.join(self._data_path, 'save', 'TestSzene', '1.json')) as tmp:
            data_szene1 = tmp.read()
        self.assertEqual(SZENE1_JSON, data_szene1)
        with open(path.join(self._data_path, 'save', 'TestSzene', '0.json')) as tmp:
            data_szene0 = tmp.read()
        self.assertEqual(SZENE0_JSON, data_szene0)
        with open(path.join(self._data_path, 'save', 'TestRectangle.json')) as tmp:
            data_rectangles = tmp.read()
        self.assertEqual(RECTANGLES_JSON, data_rectangles)
        self._db.add_object(uuid1)
        with open(path.join(self._data_path, 'save', 'TestUUID.json')) as tmp:
            data_uuid = tmp.read()
        self.assertEqual(UUID1_JSON % self._db._tables[TestUUID].get_key_of_object(uuid1), data_uuid)
        self._db.add_object(uuid2)
        with open(path.join(self._data_path, 'save', 'TestUUID.json')) as tmp:
            data_uuid = tmp.read()
        self.assertEqual(UUID2_JSON % (self._db._tables[TestUUID].get_key_of_object(uuid1),
                                       self._db._tables[TestUUID].get_key_of_object(uuid2)), data_uuid)

    def test_json_db_load(self):
        from test_json_database.db_test_load import TestClassFieldType, TestClassFile, TestClassFolder, TestUUID
        tft0 = TestClassFieldType(False, 'false', 0, 0.0)
        tft1 = TestClassFieldType(True, 'true', 1, 1.0)
        self._db.init_tables(path.join(self._data_path, 'load'))
        self.assertTrue(self._db._tables[TestClassFile].key_in_table('job0'))
        self.assertTrue(self._db._tables[TestClassFile].key_in_table('job1'))
        self.assertEqual(TestClassFile('job0', (0, 1), {0: tft1, 1: tft0}, {0, 1}),
                         self._db._tables[TestClassFile].get_object('job0'))
        self.assertEqual(TestClassFile('job1', (1, 2), {1: tft1, 0: tft0}, {1, 2}),
                         self._db._tables[TestClassFile].get_object('job1'))
        self.assertTrue(self._db._tables[TestClassFolder].key_in_table(100))
        self.assertTrue(self._db._tables[TestClassFolder].key_in_table(200))
        self.assertTrue(self._db._tables[TestClassFolder].key_in_table(300))
        self.assertEqual(TestClassFolder(100, []),
                         self._db._tables[TestClassFolder].get_object(100))
        self.assertEqual(TestClassFolder(200, [self._db._tables[TestClassFile].get_object('job0'),
                                               self._db._tables[TestClassFile].get_object('job1')]),
                         self._db._tables[TestClassFolder].get_object(200))
        self.assertEqual(TestClassFolder(300, [self._db._tables[TestClassFile].get_object('job0')]),
                         self._db._tables[TestClassFolder].get_object(300))
        self.assertTrue(self._db._tables[TestUUID].key_in_table('cad3bea2-36d0-4119-ba42-fa7fc1192582'))
        self.assertTrue(self._db._tables[TestUUID].key_in_table('55f0895b-8861-4af6-b20a-415f58a7839c'))
        self.assertEqual(TestUUID("one"),
                         self._db._tables[TestUUID].get_object('cad3bea2-36d0-4119-ba42-fa7fc1192582'))
        self.assertEqual(self._db._tables[TestUUID].get_object('cad3bea2-36d0-4119-ba42-fa7fc1192582').uuid,
                         'cad3bea2-36d0-4119-ba42-fa7fc1192582')
        self.assertEqual(TestUUID("two"),
                         self._db._tables[TestUUID].get_object('55f0895b-8861-4af6-b20a-415f58a7839c'))
        self.assertEqual(self._db._tables[TestUUID].get_object('55f0895b-8861-4af6-b20a-415f58a7839c').uuid,
                         '55f0895b-8861-4af6-b20a-415f58a7839c')

    def test_json_db_load_with_defaults(self):
        from test_json_database.db_test_load_with_defaults import TestClassFieldType, TestClassFile
        self._db.init_tables(path.join(self._data_path, 'load_with_defaults'))
        tft0 = TestClassFieldType(False, 'individual', 21, 9.81, [])
        tft_default = TestClassFieldType(True, 'default', 42, 3.14, [1, 2])
        self.assertEqual(TestClassFile('job0', True, 'default', 42, 3.14, (1, 2), {0: 'zero', 1: 'one'}, {1, 2}, [tft0],
                                       None),
                         self._db._tables[TestClassFile].get_object('job0'))
        self.assertEqual(TestClassFile('job1', True, 'default', 42, 3.14, (1, 2), {0: 'zero', 1: 'one'}, {1, 2}, [tft0],
                                       None),
                         self._db._tables[TestClassFile].get_object('job1'))
        self.assertEqual(TestClassFile('job2', False, 'not default', 84, 2.71, (1, 2), {0: 'zero', 1: 'one'}, {1, 2},
                                       [tft0], tft_default),
                         self._db._tables[TestClassFile].get_object('job2'))
        self.assertEqual(TestClassFile('job3', False, 'not default', 84, 2.71, (1, 2), {0: 'zero', 1: 'one'}, {1, 2},
                                       [tft0], tft_default),
                         self._db._tables[TestClassFile].get_object('job3'))
        self._db._tables[TestClassFile].get_object('job0').att_bool = False
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_bool,
                            self._db._tables[TestClassFile].get_object('job1').att_bool)
        self._db._tables[TestClassFile].get_object('job0').att_str = 'new val'
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_str,
                            self._db._tables[TestClassFile].get_object('job1').att_str)
        self._db._tables[TestClassFile].get_object('job0').att_int = 1
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_int,
                            self._db._tables[TestClassFile].get_object('job1').att_int)
        self._db._tables[TestClassFile].get_object('job0').att_float = 1.61
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_float,
                            self._db._tables[TestClassFile].get_object('job1').att_float)
        self._db._tables[TestClassFile].get_object('job0').att_tuple = (3, 4)
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_tuple,
                            self._db._tables[TestClassFile].get_object('job1').att_tuple)
        self._db._tables[TestClassFile].get_object('job0').att_dict[0] = 'null'
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_dict,
                            self._db._tables[TestClassFile].get_object('job1').att_dict)
        self._db._tables[TestClassFile].get_object('job0').att_set.add(3)
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_set,
                            self._db._tables[TestClassFile].get_object('job1').att_set)
        self._db._tables[TestClassFile].get_object('job0').att_list.append(tft_default)
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job0').att_list,
                            self._db._tables[TestClassFile].get_object('job1').att_list)
        self._db._tables[TestClassFile].get_object('job2').att_ft.att_list.append(3)
        self.assertNotEqual(self._db._tables[TestClassFile].get_object('job2').att_ft,
                            self._db._tables[TestClassFile].get_object('job3').att_ft)

    def test_json_db_data_to_json(self):
        from test_json_database.db_test_data_to_json import TestClassFieldType, TestClassReference
        self._db.init_tables(path.join(self._data_path, 'data_to_json'))
        res = self._db.data_to_json(True)
        self.assertTrue(res)
        res = self._db.data_to_json('Hello World')
        self.assertEqual(res, 'Hello World')
        res = self._db.data_to_json(42)
        self.assertEqual(res, 42)
        res = self._db.data_to_json(3.14)
        self.assertEqual(res, 3.14)
        res = self._db.data_to_json(3.0)
        self.assertEqual(res, 3.0)
        res = self._db.data_to_json([1, 2, 3, 'Hello', 'World', 3.14])
        self.assertCountEqual(res, {'type': 'list', 'data': [1, 2, 3, 'Hello', 'World', 3.14]})
        res = self._db.data_to_json((1, 2, 3, 'Hello', 'World', 3.14))
        self.assertCountEqual(res, {'type': 'tuple', 'data': [1, 2, 3, 'Hello', 'World', 3.14]})
        res = self._db.data_to_json({1, 2, 3, 'Hello', 'World', 3.14})
        self.assertCountEqual(res, {'type': 'set', 'data': [1, 2, 3, 'Hello', 'World', 3.14]})
        res = self._db.data_to_json({1: 'one', 'two': 2, 3.14: 'float'})
        self.assertDictEqual({'type': 'dict', 'data': [
            {'key': 1, 'value': 'one'},
            {'key': 'two', 'value': 2},
            {'key': 3.14, 'value': 'float'}]}, res)
        res = self._db.data_to_json({'list': [1, 2, 3], 'tuple': (1, 2, 3), 'set': {1, 2, 3},
                                     'dict': {1: 'one', 'two': 2, 3.14: 'float'}})
        self.assertDictEqual({'type': 'dict', 'data': [
            {'key': 'list', 'value': {'type': 'list', 'data': [1, 2, 3]}},
            {'key': 'tuple', 'value': {'type': 'tuple', 'data': [1, 2, 3]}},
            {'key': 'set', 'value': {'type': 'set', 'data': [1, 2, 3]}},
            {'key': 'dict', 'value': {'type': 'dict', 'data': [
                {'key': 1, 'value': 'one'},
                {'key': 'two', 'value': 2},
                {'key': 3.14, 'value': 'float'}]}}]}, res)
        tmp_1 = TestClassFieldType(att_bool=True, att_str='Hello', att_int=42, att_float=3.14)
        res = self._db.data_to_json(tmp_1)
        self.assertDictEqual({'type': 'TestClassFieldType', 'data': {'att_bool': True, 'att_str': 'Hello',
                                                                     'att_int': 42, 'att_float': 3.14}}, res)
        tcr1 = TestClassReference(job_id='tcr1', att_str='Hello')
        self._db._tables[type(tcr1)].add_object(tcr1)
        res = self._db.data_to_json(tcr1)
        self.assertDictEqual(res, {'type': 'TestClassReference', 'data': 'tcr1'})

    def test_json_db_json_to_value(self):
        from test_json_database.db_test_json_to_value import TestClassFieldType, TestClassReference
        self._db.init_tables(path.join(self._data_path, 'json_to_value'))
        self.assertTrue(self._db.json_to_value(self._db.data_to_json(True)))
        self.assertEqual(self._db.json_to_value(self._db.data_to_json('Hello World')), 'Hello World')
        self.assertEqual(self._db.json_to_value(self._db.data_to_json(42)), 42)
        self.assertEqual(self._db.json_to_value(self._db.data_to_json(3.14)), 3.14)
        self.assertEqual(self._db.json_to_value(self._db.data_to_json(3.0)), 3.0)
        self.assertListEqual(self._db.json_to_value(self._db.data_to_json([1, 2, 3, 'Hello', 'World', 3.14])),
                             [1, 2, 3, 'Hello', 'World', 3.14])
        self.assertTupleEqual(self._db.json_to_value(self._db.data_to_json((1, 2, 3, 'Hello', 'World', 3.14))),
                              (1, 2, 3, 'Hello', 'World', 3.14))
        self.assertCountEqual(self._db.json_to_value(self._db.data_to_json({1, 2, 3, 'Hello', 'World', 3.14})),
                              {1, 2, 3, 'Hello', 'World', 3.14})
        self.assertDictEqual({1: 'one', 'two': 2, 3.14: 'float'},
                             self._db.json_to_value(self._db.data_to_json({1: 'one', 'two': 2, 3.14: 'float'})))
        self.assertDictEqual({'list': [1, 2, 3], 'tuple': (1, 2, 3), 'set': {1, 2, 3},
                              'dict': {1: 'one', 'two': 2, 3.14: 'float'}}, self._db.json_to_value(
            self._db.data_to_json({'list': [1, 2, 3], 'tuple': (1, 2, 3), 'set': {1, 2, 3},
                                   'dict': {1: 'one', 'two': 2, 3.14: 'float'}})))
        tmp_1 = TestClassFieldType(att_bool=True, att_str='Hello', att_int=42, att_float=3.14)
        tmp_1_clone = self._db.json_to_value(self._db.data_to_json(tmp_1))
        self.assertEqual(tmp_1, tmp_1_clone)
        tcr1 = TestClassReference(job_id='tcr1', att_str='Hello')
        self._db._tables[type(tcr1)].add_object(tcr1)
        self.assertEqual(self._db.json_to_value(self._db.data_to_json(tcr1)), tcr1)
        with self.assertRaises(Exception) as em:
            self._db.json_to_value({'type': 'TestClassReference', 'data': 'tcr2'})
        self.assertEqual('The id \'tcr2\' can not be found in Table \'TestClassReference\'.',
                         str(em.exception))
        for d in [['Type'], {'set'}, ('tuple', 'tuple'), {'Type': 't', 'data': 'd'}, {'type': 't', 'Data': 'd'}]:
            with self.assertRaises(Exception) as em:
                self._db.json_to_value(d)
            self.assertEqual(f"The following data is not well formed:\n{d}.", str(em.exception))

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
        res = is_serializable(dict)
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
