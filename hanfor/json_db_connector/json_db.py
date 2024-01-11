import inspect
import json
from types import GenericAlias, UnionType
from typing import get_origin, get_args, Type, TypeVar
from uuid import UUID, uuid4
from os import path, mkdir
from static_utils import get_filenames_from_dir
from copy import deepcopy
from enum import Enum

T = TypeVar('T')


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
        self._user_uuid = use_uuid
        if use_uuid:
            return
        if field is None:
            # empty brackets
            return
        if inspect.isclass(field):
            raise Exception(f"DatabaseID must be set to the name and type of an field of the class: {field}")

    def __call__(self, cls):
        if cls in self.registry:
            raise Exception(f"DatabaseTable with name {cls} already has an id field.")
        if self._user_uuid:
            self.registry[cls] = ('', UUID)
            return cls
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
        if not (self._type is str or self._type is int):
            raise Exception(f"Type of DatabaseID must be of type str or int: {cls}")
        # check if class with name exists already
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
        self._data_folder: str = ''
        # class: (table_type, id_field, id_type, dict of fields(field_name, (type, default)))
        self._tables: dict[Type[T], tuple[TableType, str, type, dict[str, tuple[any, any]]]] = {}
        # class: (dict of fields(field_name, (type, default)))
        self._field_types: dict[Type[T], dict[str, tuple[any, any]]] = {}
        # class: dict of objects(id, data))
        self._json_data: dict[Type[T], dict[str | int, any]] = {}
        # object storage
        # class: id(object): id
        self._data_obj: dict[Type[T], dict[int, str | int]] = {}
        # class: id: object
        self._data_id: dict[Type[T], dict[str | int, T]] = {}

    def init_tables(self, data_folder: str) -> None:
        if data_folder == '':
            raise Exception(f"The data_folder is required")
        self._data_folder = data_folder
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

        # create tables
        for cls, table_type in DatabaseTable.registry.items():
            id_field = DatabaseID.registry[cls][0]
            id_type = DatabaseID.registry[cls][1]
            fields = {}
            for f_name, (f_type, f_default) in DatabaseField.registry[cls].items():
                fields[f_name] = f_type, f_default
            self._tables[cls] = table_type, id_field, id_type, fields
            self._data_obj[cls] = {}
            self._data_id[cls] = {}
            self._json_data[cls] = {}

        # create field types
        for cls in DatabaseFieldType.registry:
            fields = {}
            for f_name, (f_type, f_default) in DatabaseField.registry[cls].items():
                fields[f_name] = f_type, f_default
            self._field_types[cls] = fields

        # create database folder if not exist
        if not path.isdir(self._data_folder):
            mkdir(self._data_folder)

        # create folders and files is not exist
        for cls, (table_type, _, _, _) in self._tables.items():
            if table_type == TableType.File:
                table_file = path.join(self._data_folder, f"{cls.__name__}.json")
                if not path.isfile(table_file):
                    file = open(table_file, 'w')
                    file.write("{}")
                    file.close()
            elif table_type == TableType.Folder:
                table_folder = path.join(self._data_folder, cls.__name__)
                if not path.isdir(table_folder):
                    mkdir(table_folder)
        self.__load_data()

    def add_object(self, obj: object) -> None:
        # check if object is part of the database
        if type(obj) not in self._tables.keys():
            raise Exception(f"{type(obj)} is not part of the Database.")
        if id(obj) in self._data_obj[type(obj)].keys():
            # object already in database -> TODO do update of this object
            pass
        _, id_f_name, id_f_type, fields = self._tables[type(obj)]
        if id_f_type is UUID:
            obj_id = str(uuid4())
        else:
            # check if id is already in db
            obj_id = getattr(obj, id_f_name, None)
            if obj_id is None or obj_id == '':
                raise Exception(f"The id field \'{id_f_name}\' of object {obj} is empty.")
            if obj_id in self._data_id[type(obj)].keys():
                raise Exception(f"The id \'{obj_id}\' already exists in table {type(obj)}.")
            if type(obj_id) != id_f_type:
                raise Exception(f"The id field \'{id_f_name}\' of object {obj} is not of type \'{id_f_type}\'.")
        # save object to db
        self._data_obj[type(obj)][id(obj)] = obj_id
        self._data_id[type(obj)][obj_id] = obj
        # TODO insert into data tracing
        obj_data = {}
        for field, f_type in fields.items():
            field_data = getattr(obj, field, None)
            field_data_serialized = self._data_to_json(field_data)
            obj_data[field] = field_data_serialized
        self._json_data[type(obj)][obj_id] = obj_data
        self.__save_data(type(obj))

    def _data_to_json(self, data: any) -> any:
        if data is None:
            return None
        f_type = type(data)
        if f_type in [bool, str, int, float]:
            return data
        if f_type in [tuple, list, set]:
            res = []
            for item in data:
                tmp = self._data_to_json(item)
                if tmp is None:
                    continue
                res.append(tmp)
            return {'type': f_type.__name__, 'data': res}
        if f_type is dict:
            res = []
            for k, v in data.items():
                k_serialized = self._data_to_json(k)
                v_serialized = self._data_to_json(v)
                res.append({'key': k_serialized, 'value': v_serialized})
            return {'type': 'dict', 'data': res}
        if f_type in self._tables.keys():
            if id(data) not in self._data_obj[f_type]:
                self.add_object(data)
            return {'type': f_type.__name__, 'data': self._data_obj[f_type][id(data)]}
        if f_type in self._field_types.keys():
            res = {}
            for field, ft_f_type in self._field_types[f_type].items():
                field_data = getattr(data, field, None)
                field_data_serialized = self._data_to_json(field_data)
                if field_data_serialized is not None:
                    res[field] = field_data_serialized
            return {'type': f_type.__name__, 'data': res}
        raise Exception(f"The following data is not serializable:\n{data}.")

    def __save_data(self, cls: type) -> None:
        table_type, _, _, _ = self._tables[cls]
        if table_type == TableType.File:
            table_file = path.join(self._data_folder, f"{cls.__name__}.json")
            with open(table_file, 'w') as json_file:
                json.dump(self._json_data[cls], json_file, indent=4)
        elif table_type == TableType.Folder:
            table_folder = path.join(self._data_folder, cls.__name__)
            for obj_id, obj_data in self._json_data[cls].items():
                file_name = path.join(table_folder, f"{obj_id}.json")
                with open(file_name, 'w') as json_file:
                    json.dump(obj_data, json_file, indent=4)

    def __load_data(self) -> None:
        # load json data from files and create objects without data
        for cls, (table_type, id_field, id_type, _) in self._tables.items():
            if table_type == TableType.File:
                table_file = path.join(self._data_folder, f"{cls.__name__}.json")
                with open(table_file, 'r') as json_file:
                    for obj_id, obj_data in json.load(json_file).items():
                        if id_type is int:
                            self._json_data[cls][int(obj_id)] = obj_data
                            self.__create_and_insert_object(cls, int(obj_id))
                        elif id_type in [str, UUID]:
                            self._json_data[cls][obj_id] = obj_data
                            self.__create_and_insert_object(cls, obj_id)
            elif table_type == TableType.Folder:
                table_folder = path.join(self._data_folder, cls.__name__)
                for file_name in get_filenames_from_dir(table_folder):
                    with open(file_name, 'r') as json_file:
                        obj_data = json.load(json_file)
                        obj_id = path.splitext(path.basename(file_name))[0]
                        if id_type is int:
                            self._json_data[cls][int(obj_id)] = obj_data
                            self.__create_and_insert_object(cls, int(obj_id))
                        elif id_type in [str, UUID]:
                            self._json_data[cls][obj_id] = obj_data
                            self.__create_and_insert_object(cls, obj_id)
        # fill objects with data
        for cls in self._tables:
            for obj_id, data in self._json_data[cls].items():
                self.__fill_object_from_dict(self._data_id[cls][obj_id], data)

    def __create_and_insert_object(self, cls: Type[T], obj_id: int | str) -> None:
        _, id_field, id_type, _ = self._tables[cls]
        obj = object.__new__(cls)
        if id_type in [str, int]:
            setattr(obj, id_field, obj_id)
        self._data_obj[cls][id(obj)] = obj_id
        self._data_id[cls][obj_id] = obj

    def __fill_object_from_dict(self, obj: object, obj_data: dict[str | int, any]) -> None:
        _, _, _, table_fields = self._tables[type(obj)]
        for field in table_fields:
            if field in obj_data:
                setattr(obj, field, self._json_to_value(obj_data[field]))
            else:
                # insert default value
                if type(table_fields[field][1]) in [str, int, float, bool, tuple]:
                    setattr(obj, field, table_fields[field][1])
                else:
                    setattr(obj, field, deepcopy(table_fields[field][1]))

    def _json_to_value(self, data: any) -> any:
        data_type = type(data)
        if data_type in [str, int, float, bool, None]:
            return data
        if data_type is dict:
            if 'type' not in data or 'data' not in data:
                raise Exception(f"The following data is not well formed:\n{data}.")
            if data['type'] == 'list':
                res = []
                for i in data['data']:
                    res.append(self._json_to_value(i))
                return res
            if data['type'] == 'set':
                res = set()
                for i in data['data']:
                    res.add(self._json_to_value(i))
                return res
            if data['type'] == 'dict':
                res = {}
                for i in data['data']:
                    res[self._json_to_value(i['key'])] = self._json_to_value(i['value'])
                return res
            if data['type'] == 'tuple':
                res = []
                for i in data['data']:
                    res.append(self._json_to_value(i))
                return tuple(res)
            tmp = {k.__name__: (k, v) for k, v in self._field_types.items()}
            if data['type'] in tmp:
                cls, fields = tmp[data['type']]
                obj = object.__new__(cls)
                for field in fields:
                    if field in data['data']:
                        setattr(obj, field, self._json_to_value(data['data'][field]))
                    else:
                        # insert default value
                        if type(fields[field][1]) in [str, int, float, bool, tuple]:
                            setattr(obj, field, fields[field][1])
                        else:
                            setattr(obj, field, deepcopy(fields[field][1]))
                return obj
            tmp = {k.__name__: k for k in self._tables}
            if data['type'] in tmp:
                if data['data'] in self._data_id[tmp[data['type']]]:
                    return self._data_id[tmp[data['type']]][data['data']]
                else:
                    raise Exception(f"The id \'{data['data']}\' can not be found in Table \'{data['type']}\'.")
        raise Exception(f"The following data is not well formed:\n{data}.")


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
