import json
import inspect
from enum import Enum
from types import GenericAlias, UnionType
from typing import get_origin, get_args, Type, TypeVar, Callable
from uuid import UUID, uuid4
from os import path, mkdir
from static_utils import get_filenames_from_dir
from copy import deepcopy
from dataclasses import dataclass

T = TypeVar('T')
TABLE = TypeVar('TABLE')
ID_TYPE = TypeVar('ID_TYPE')


class TableType(Enum):
    File = 'file'
    Folder = 'folder'
    NotSet = None


class DatabaseTable:
    registry: dict[type, TableType] = {}

    def __init__(self, table_type: TableType = TableType.NotSet):
        self._table_type: TableType = table_type
        if inspect.isclass(table_type):
            raise Exception(f"DatabaseTable must be set to file or folder: {table_type}")

    def __call__(self, cls: type):
        if self._table_type == TableType.NotSet:
            # empty brackets
            raise Exception(f"DatabaseTable must be set to file or folder: {cls}")
        # check if class with name exists already
        if cls.__name__ in [c.__name__ for c in self.registry]:
            raise Exception(f"DatabaseTable with name {cls.__name__} already exists.")
        self.registry[cls] = self._table_type
        return cls


class DatabaseID:
    registry: dict[type, tuple[str, type]] = {}

    def __init__(self, field: str = None, f_type: type = None, use_uuid: bool = False):
        self._id_field = field
        self._type = f_type
        if use_uuid:
            self._type = UUID
            return
        if field is None:
            # empty brackets
            return
        if inspect.isclass(field):
            raise Exception(f"DatabaseID must be set to the name and type of an field of the class: {field}")

    def __call__(self, cls):
        if cls in self.registry:
            raise Exception(f"DatabaseTable with name {cls} already has an id field.")
        if self._id_field is None:
            # empty brackets
            raise Exception(f"DatabaseID must be set to the name and type of an field of the class: {cls}")
        if not type(self._id_field) is str:
            # first argument is not a string
            raise Exception(f"Name of DatabaseID must be of type str: {cls}")
        if self._type is None:
            raise Exception(f"Type of DatabaseID must be provided: {cls}")
        if type(self._type) is not type:
            raise Exception(f"Type of DatabaseID must be of type type: {cls}")
        if self._type not in [str, int, UUID]:
            raise Exception(f"Type of DatabaseID must be of type str or int: {cls}")

        # Define getter and setter method
        private_attribute_name = f"__{self._id_field}"

        def getter(getter_self: object):
            return getattr(getter_self, private_attribute_name)

        def setter(setter_self: object, value):
            if getattr(setter_self, private_attribute_name) is None:
                setattr(setter_self, private_attribute_name, value)
            else:
                raise Exception(f"The id field of an object can not be changed!\n{setter_self}")

        setattr(cls, private_attribute_name, None)
        setattr(cls, self._id_field, property(getter, setter))

        self.registry[cls] = (self._id_field, self._type)
        return cls


# noinspection DuplicatedCode
class DatabaseField:
    registry: dict[type, dict[str, tuple[any, any]]] = {}

    def __init__(self, field: str = None, f_type: type = None, default: any = None):
        self._field = field
        self._type = f_type
        self._default = default
        if field is None:
            # empty brackets
            return
        if inspect.isclass(field):
            raise Exception(f"DatabaseField must be set to the name and type of an field of the class: {field}")

    def __call__(self, cls):
        if self._field is None:
            # empty brackets
            raise Exception(f"DatabaseField must be set to the name and type of an field of the class: {cls}")
        if not type(self._field) is str:
            # first argument is not a string
            raise Exception(f"Name of DatabaseField must be of type str: {cls}")
        if self._type is None:
            raise Exception(f"Type of DatabaseField must be provided: {cls}")
        if type(self._type) not in [type, GenericAlias]:
            raise Exception(f"Type of DatabaseField must be of type type: {cls}")
        if cls not in self.registry:
            self.registry[cls] = {}
        # check if field of class with name exists already
        if self._field in self.registry[cls]:
            raise Exception(f"DatabaseField with name {self._field} already exists in class {cls}.")
        self.registry[cls][self._field] = self._type, self._default
        return cls


class DatabaseFieldType:
    registry: set[type] = set()

    def __init__(self, cls: type = None):
        if cls:
            raise Exception(f"DatabaseFieldType must be called with brackets: {cls}")

    def __call__(self, cls: type):
        if cls.__name__ in [c.__name__ for c in self.registry]:
            existing = None
            for c in self.registry:
                if c.__name__ == cls.__name__:
                    existing = c
                    break
            raise Exception(f"Name of DatabaseFieldType exists already:\nexisting: {existing}\nnew     : {cls}")
        self.registry.add(cls)
        return cls


class JsonDatabase:

    def __init__(self) -> None:
        self.__data_folder: str = ''
        self._tables: dict[Type[T], JsonDatabaseTable] = {}
        # class: (dict of fields(field_name, (type, default)))
        self._field_types: dict[Type[T], dict[str, tuple[any, any]]] = {}

    @property
    def data_folder(self):
        return self.__data_folder

    def init_tables(self, data_folder: str) -> None:
        if data_folder == '':
            raise Exception(f"The data_folder is required")
        self.__data_folder = data_folder
        tables: set[type] = set(DatabaseTable.registry.keys())
        id_fields: set[type] = set(DatabaseID.registry.keys())
        db_fields: set[type] = set(DatabaseField.registry.keys())
        field_types: set[type] = DatabaseFieldType.registry

        # check if decorated classes are well-formed tables and field types
        if tables & field_types:
            raise Exception(f"The following classes are marked as DatabaseTable and DatabaseFieldType:\n"
                            f"{tables & field_types}")

        if tables.difference(id_fields):
            raise Exception(f"The following classes are marked as DatabaseTable but don\'t have an id field:\n"
                            f"{tables.difference(id_fields)}")

        if id_fields.difference(tables):
            raise Exception(f"The following classes are marked with an id field but not as an DatabaseTable:\n"
                            f"{id_fields.difference(tables)}")

        if db_fields.difference(tables.union(field_types)):
            raise Exception(f"The following classes are marked with fields but not as an DatabaseTable or "
                            f"DatabaseFieldType:\n"
                            f"{db_fields.difference(tables.union(field_types))}")

        if tables.difference(db_fields):
            raise Exception(f"The following classes are marked as DatabaseTable but don\'t have any fields:\n"
                            f"{tables.difference(db_fields)}")

        if field_types.difference(db_fields):
            raise Exception(f"The following classes are marked as DatabaseFieldType but don\'t have any fields:\n"
                            f"{field_types.difference(db_fields)}")

        # check if all used types are serializable
        for cls, field_dict in DatabaseField.registry.items():
            for field, (f_type, _) in field_dict.items():
                res = is_serializable(f_type, list(tables.union(field_types)))
                if not res[0]:
                    raise Exception(f"The following type of class {cls} is not serializable:\n{field}: {res[1]}")

        # create database folder if not exist
        if not path.isdir(self.__data_folder):
            mkdir(self.__data_folder)

        # create tables
        for cls, table_type in DatabaseTable.registry.items():
            id_field = DatabaseID.registry[cls][0]
            id_type = DatabaseID.registry[cls][1]
            fields = {}
            for f_name, (f_type, f_default) in DatabaseField.registry[cls].items():
                fields[f_name] = f_type, f_default
            self._tables[cls] = JsonDatabaseTable(self, cls, table_type, id_field, id_type, fields)

        # create field types
        for cls in DatabaseFieldType.registry:
            fields = {}
            for f_name, (f_type, f_default) in DatabaseField.registry[cls].items():
                fields[f_name] = f_type, f_default
            self._field_types[cls] = fields

        # load json data from files
        fill_functions = []
        for _, table in self._tables.items():
            fill_functions.append(table.load())

        for f in fill_functions:
            f()

    def add_object(self, obj: object) -> None:
        # check if object is part of the database
        if type(obj) not in self._tables.keys():
            raise Exception(f"{type(obj)} is not part of the Database.")
        self._tables[type(obj)].add_object(obj)
        self.__save_data()

    def data_to_json(self, data: any) -> any:
        if data is None:
            return None
        f_type = type(data)
        if f_type in [bool, str, int, float]:
            return data
        if f_type in [tuple, list, set]:
            res = []
            for item in data:
                tmp = self.data_to_json(item)
                res.append(tmp)
            return {'type': f_type.__name__, 'data': res}
        if f_type is dict:
            res = []
            for k, v in data.items():
                k_serialized = self.data_to_json(k)
                v_serialized = self.data_to_json(v)
                res.append({'key': k_serialized, 'value': v_serialized})
            return {'type': 'dict', 'data': res}
        if f_type in self._tables.keys():
            if not self._tables[f_type].object_in_table(data):
                self.add_object(data)
            return {'type': f_type.__name__, 'data': self._tables[f_type].get_key_of_object(data)}
        if f_type in self._field_types.keys():
            res = {}
            for field, ft_f_type in self._field_types[f_type].items():
                field_data = getattr(data, field, None)
                field_data_serialized = self.data_to_json(field_data)
                if field_data_serialized is not None:
                    res[field] = field_data_serialized
            return {'type': f_type.__name__, 'data': res}
        raise Exception(f"The following data is not serializable:\n{data}.")

    def __save_data(self) -> None:
        for _, table in self._tables.items():
            table.save()

    def json_to_value(self, data: any) -> any:
        data_type = type(data)
        if data_type in [str, int, float, bool, None]:
            return data
        if data_type is dict:
            if 'type' not in data or 'data' not in data:
                raise Exception(f"The following data is not well formed:\n{data}.")
            if data['type'] == 'list':
                res = []
                for i in data['data']:
                    res.append(self.json_to_value(i))
                return res
            if data['type'] == 'set':
                res = set()
                for i in data['data']:
                    res.add(self.json_to_value(i))
                return res
            if data['type'] == 'dict':
                res = {}
                for i in data['data']:
                    res[self.json_to_value(i['key'])] = self.json_to_value(i['value'])
                return res
            if data['type'] == 'tuple':
                res = []
                for i in data['data']:
                    res.append(self.json_to_value(i))
                return tuple(res)
            # check if field is of type FieldType
            # key: name of FieldType
            # value: (class, fields of FieldType)
            tmp = {k.__name__: (k, v) for k, v in self._field_types.items()}
            if data['type'] in tmp:
                cls, fields = tmp[data['type']]
                obj = object.__new__(cls)
                for field in fields:
                    if field in data['data']:
                        setattr(obj, field, self.json_to_value(data['data'][field]))
                    else:
                        # insert default value
                        if type(fields[field][1]) in [str, int, float, bool, tuple]:
                            setattr(obj, field, fields[field][1])
                        else:
                            setattr(obj, field, deepcopy(fields[field][1]))
                return obj
            # check if field is of type DatabaseTable
            # key: name of DatabaseTable
            # value: JsonDatabaseTable
            tmp = {k.__name__: v for k, v in self._tables.items()}
            if data['type'] in tmp:
                if tmp[data['type']].key_in_table(data['data']):
                    return tmp[data['type']].get_object(data['data'])
                else:
                    raise Exception(f"The id \'{data['data']}\' can not be found in Table \'{data['type']}\'.")
        raise Exception(f"The following data is not well formed:\n{data}.")


class JsonDatabaseTable:

    def __init__(self, db: JsonDatabase, cls: type, table_type: TableType, id_field: str, id_type: type,
                 fields: dict[str, tuple[any, any]]) -> None:
        self.__db: JsonDatabase = db
        self.cls: TABLE = cls
        self.table_type: TableType = table_type
        self.id_field: str = id_field
        self.id_type: ID_TYPE = id_type
        self.fields: dict[str, tuple[any, any]] = fields
        self.__data: dict[ID_TYPE, TABLE] = {}
        self.__meta_data: dict[ID_TYPE, JsonDatabaseMetaData] = {}
        self.__json_data: dict[str | int, any] = {}

        # create folders and files is not exist
        if self.table_type == TableType.File:
            table_file = path.join(self.__db.data_folder, f"{cls.__name__}.json")
            if not path.isfile(table_file):
                file = open(table_file, 'w')
                file.write("{}")
                file.close()
        elif self.table_type == TableType.Folder:
            table_folder = path.join(self.__db.data_folder, cls.__name__)
            if not path.isdir(table_folder):
                mkdir(table_folder)

    def add_object(self, obj: object) -> None:
        if not type(obj) == self.cls:
            raise Exception(f"{obj} does not belong to this table.")
        if id(obj) in [id(i) for i in self.__data.values()]:
            # object already in database -> update db
            return
        if self.id_type is UUID:
            obj_id = str(uuid4())
            setattr(obj, self.id_field, obj_id)
        else:
            # check if id is already in db
            obj_id = getattr(obj, self.id_field, None)
            if obj_id is None or obj_id == '':
                raise Exception(f"The id field \'{self.id_field}\' of object {obj} is empty.")
            if obj_id in self.__data.keys():
                raise Exception(f"The id \'{obj_id}\' already exists in table {type(obj)}.")
            if type(obj_id) != self.id_type:
                raise Exception(f"The id field \'{self.id_field}\' of object {obj} is not of type "
                                f"\'{self.id_type}\'.")
        # save object to db
        self.__data[obj_id] = obj
        self.__meta_data[obj_id] = JsonDatabaseMetaData()
        self.__serialize()

    def key_in_table(self, key: ID_TYPE) -> bool:
        return key in self.__data.keys()

    def object_in_table(self, obj: TABLE) -> bool:
        if not type(obj) == self.cls:
            return False
        return getattr(obj, self.id_field, None) in self.__data.keys()

    def get_key_of_object(self, obj: TABLE) -> int | str:
        if not type(obj) == self.cls or getattr(obj, self.id_field, None) not in self.__data:
            raise Exception(f"Object {obj} not in this table.")
        return getattr(obj, self.id_field, None)

    def get_object(self, key: ID_TYPE) -> T:
        if key not in self.__data.keys():
            raise Exception(f"No object with key {key} in this table.")
        return self.__data[key]

    def get_objects(self) -> dict[Type[ID_TYPE], Type[TABLE]]:
        return self.__data

    def __serialize(self) -> dict:
        json_data = {}
        for obj_id, obj in self.__data.items():
            obj_data = {}
            for field in self.fields.keys():
                field_data = getattr(obj, field, None)
                field_data_serialized = self.__db.data_to_json(field_data)
                obj_data[field] = field_data_serialized
            obj_data['$meta'] = self.__db.data_to_json(self.__meta_data[obj_id])
            json_data[obj_id] = obj_data
        return json_data

    def save(self) -> None:
        json_data = self.__serialize()
        # TODO diff and write diff to data tracing
        self.__json_data = json_data
        if self.table_type == TableType.File:
            table_file = path.join(self.__db.data_folder, f"{self.cls.__name__}.json")
            with open(table_file, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
        elif self.table_type == TableType.Folder:
            table_folder = path.join(self.__db.data_folder, self.cls.__name__)
            for obj_id, obj_data in json_data.items():
                file_name = path.join(table_folder, f"{obj_id}.json")
                with open(file_name, 'w') as json_file:
                    json.dump(obj_data, json_file, indent=4)

    def load(self) -> Callable[[], None]:
        if self.table_type == TableType.File:
            table_file = path.join(self.__db.data_folder, f"{self.cls.__name__}.json")
            with open(table_file, 'r') as json_file:
                for obj_id, obj_data in json.load(json_file).items():
                    if self.id_type is int:
                        self.__create_and_insert_object(int(obj_id), obj_data)
                    elif self.id_type in [str, UUID]:
                        self.__create_and_insert_object(obj_id, obj_data)
        elif self.table_type == TableType.Folder:
            table_folder = path.join(self.__db.data_folder, self.cls.__name__)
            for file_name in get_filenames_from_dir(table_folder):
                with open(file_name, 'r') as json_file:
                    obj_data = json.load(json_file)
                    obj_id = path.splitext(path.basename(file_name))[0]
                    if self.id_type is int:
                        self.__create_and_insert_object(int(obj_id), obj_data)
                    elif self.id_type in [str, UUID]:
                        self.__create_and_insert_object(obj_id, obj_data)
        return self.__fill_objects

    def __fill_objects(self) -> None:
        for obj_id, data in self.__json_data.items():
            self.__fill_object_from_dict(self.__data[obj_id], data)
        # TODO save object because of default value insertions?

    def __create_and_insert_object(self, obj_id: int | str, obj_data: dict) -> None:
        obj = TABLE.__new__(self.cls)
        setattr(obj, self.id_field, obj_id)
        self.__data[obj_id] = obj
        self.__json_data[obj_id] = obj_data
        self.__meta_data[obj_id] = self.__db.json_to_value(obj_data['$meta'])

    def __fill_object_from_dict(self, obj: object, obj_data: dict[str | int, any]) -> None:
        for field in self.fields:
            if field in obj_data:
                setattr(obj, field, self.__db.json_to_value(obj_data[field]))
            else:
                # insert default value
                if type(self.fields[field][1]) in [str, int, float, bool, tuple]:
                    setattr(obj, field, self.fields[field][1])
                else:
                    setattr(obj, field, deepcopy(self.fields[field][1]))


# When adding new fields to the JsonDatabaseMetaData class you have to insert them to:
# - the setUp function in tests/test_json_db.py
# - SZENE0_JSON, SZENE1_JSON, RECTANGLES_JSON, UUID1_JSON, UUID2_JSON in tests/test_json_database/db_test_save.py
@dataclass()
@DatabaseFieldType()
@DatabaseField('is_deleted', bool, False)
class JsonDatabaseMetaData:
    is_deleted: bool = False


def is_serializable(f_type: any, additional_types: list[type] = None) -> tuple[bool, str]:
    if additional_types is None:
        additional_types = []
    if f_type in [bool, str, int, float, dict]:
        return True, ''
    if type(f_type) is GenericAlias:
        if get_origin(f_type) in [tuple, list, set]:
            for arg in get_args(f_type):
                res = is_serializable(arg, additional_types)
                if not res[0]:
                    return False, res[1]
            return True, ''
    if type(f_type) is UnionType:
        for arg in get_args(f_type):
            res = is_serializable(arg, additional_types)
            if not res[0]:
                return False, res[1]
        return True, ''
    if f_type in additional_types:
        return True, ''
    return False, str(f_type)
