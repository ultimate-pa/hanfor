import itertools
import json
import inspect
from enum import Enum
from types import GenericAlias, UnionType
from typing import get_origin, get_args, TypeVar, Callable, Type
from uuid import UUID, uuid4
from os import path, mkdir
from static_utils import get_filenames_from_dir
from copy import deepcopy
from dataclasses import dataclass
from immutabledict import immutabledict
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import re


CLS_TYPE = TypeVar("CLS_TYPE")
ID_TYPE = TypeVar("ID_TYPE")
GET_TYPE = TypeVar("GET_TYPE")
SERIALIZER_TYPE = TypeVar("SERIALIZER_TYPE")

KEY_REGEX = re.compile(r"^[a-zA-Z0-9_\-.]+$")


class TableType(Enum):
    File = "file"
    Folder = "folder"
    NotSet = None


class DatabaseTable:
    registry: dict[type, TableType] = {}

    def __init__(self, table_type: TableType = TableType.NotSet):
        self._table_type: TableType = table_type
        if inspect.isclass(table_type):
            raise DatabaseDefinitionError(f"DatabaseTable must be set to file or folder: {table_type}")

    def __call__(self, cls: type):
        if self._table_type == TableType.NotSet:
            # empty brackets
            raise DatabaseDefinitionError(f"DatabaseTable must be set to file or folder: {cls}")
        # check if class with name exists already
        if cls.__name__ in [c.__name__ for c in self.registry]:
            raise DatabaseDefinitionError(f"DatabaseTable with name {cls.__name__} already exists.")
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
            raise DatabaseDefinitionError(
                f"DatabaseID must be set to the name and type of an field of the class: " f"{field}"
            )

    def __call__(self, cls):
        if cls in self.registry:
            raise DatabaseDefinitionError(f"DatabaseTable with name {cls} already has an id field.")
        if self._id_field is None:
            # empty brackets
            raise DatabaseDefinitionError(
                f"DatabaseID must be set to the name and type of an field of the class: " f"{cls}"
            )
        if not type(self._id_field) is str:
            # first argument is not a string
            raise DatabaseDefinitionError(f"Name of DatabaseID must be of type str: {cls}")
        if self._type is None:
            raise DatabaseDefinitionError(f"Type of DatabaseID must be provided: {cls}")
        if type(self._type) is not type:
            raise DatabaseDefinitionError(f"Type of DatabaseID must be of type type: {cls}")
        if self._type not in [str, int, UUID]:
            raise DatabaseDefinitionError(f"Type of DatabaseID must be of type str or int: {cls}")

        # Define getter and setter method
        private_attribute_name = f"__{self._id_field}"

        def getter(getter_self: object):
            return getattr(getter_self, private_attribute_name)

        def setter(setter_self: object, value):
            if getattr(setter_self, private_attribute_name) is None:
                if not KEY_REGEX.match(str(value)):
                    raise DatabaseKeyError(f"The given id is invalid!\n{value} not in {KEY_REGEX.pattern}")
                setattr(setter_self, private_attribute_name, value)
            else:
                raise DatabaseKeyError(f"The id field of an object can not be changed!\n{setter_self}")

        setattr(cls, private_attribute_name, None)
        setattr(cls, self._id_field, property(getter, setter))

        self.registry[cls] = (self._id_field, self._type)
        return cls


# noinspection DuplicatedCode
class DatabaseField:
    registry: dict[type, dict[str, tuple[any, any]]] = {}

    def __init__(self, field: str = None, f_type: type | str = None, default: any = None):
        self._field = field
        self._type = f_type
        self._default = default
        if field is None:
            # empty brackets
            return
        if inspect.isclass(field):
            raise DatabaseDefinitionError(
                f"DatabaseField must be set to the name and type of an field of the class: " f"{field}"
            )

    def __call__(self, cls):
        if self._field is None:
            # empty brackets
            raise DatabaseDefinitionError(
                f"DatabaseField must be set to the name and type of an field of the class: " f"{cls}"
            )
        if not type(self._field) is str:
            # first argument is not a string
            raise DatabaseDefinitionError(f"Name of DatabaseField must be of type str: {cls}")
        if self._type is None:
            raise DatabaseDefinitionError(f"Type of DatabaseField must be provided: {cls}")
        if type(self._type) not in [type, GenericAlias, str]:
            raise DatabaseDefinitionError(f"Type of DatabaseField must be of type type or str: {cls}")
        if cls not in self.registry:
            self.registry[cls] = {}
        # check if field of class with name exists already
        if self._field in self.registry[cls]:
            raise DatabaseDefinitionError(f"DatabaseField with name {self._field} already exists in class {cls}.")
        self.registry[cls][self._field] = self._type, self._default
        return cls


class DatabaseFieldType:
    registry: set[type] = set()

    def __init__(self, cls: type = None):
        if cls:
            raise DatabaseDefinitionError(f"DatabaseFieldType must be called with brackets: {cls}")

    def __call__(self, cls: type):
        if cls.__name__ in [c.__name__ for c in self.registry]:
            existing = None
            for c in self.registry:
                if c.__name__ == cls.__name__:
                    existing = c
                    break
            raise DatabaseDefinitionError(
                f"Name of DatabaseFieldType exists already:\nexisting: {existing}\n" f"new     : {cls}"
            )
        self.registry.add(cls)
        return cls


class JsonDatabase:

    def __init__(self, *, test_mode: bool = False) -> None:
        self.__data_folder: str = ""
        self._tables: dict[type, JsonDatabaseTable] = {}
        # class: (dict of fields(field_name, (type, default)))
        self._field_types: dict[type, dict[str, tuple[any, any]]] = {}
        self.__custom_serializer: dict[
            SERIALIZER_TYPE, Callable[[SERIALIZER_TYPE, Callable[[any, str], any], str], dict]
        ] = {}
        self.__custom_deserializer: dict[SERIALIZER_TYPE, Callable[[dict, Callable[[any], any]], SERIALIZER_TYPE]] = {}
        self.__test_mode = test_mode  # testmode disables data tracing and update files at load of database
        if test_mode:
            logging.warning("JsonDatabase is running in test mode")
        self.__data_tracing_logger: Logger | None = None

    @property
    def data_folder(self):
        return self.__data_folder

    def add_custom_serializer(
        self,
        cls: type,
        serializer: Callable[[SERIALIZER_TYPE, Callable[[any, str], any], str], dict],
        deserializer: Callable[[dict, Callable[[any], any]], SERIALIZER_TYPE],
    ):
        self.__custom_serializer[cls] = serializer
        self.__custom_deserializer[cls] = deserializer

    def init_tables(self, data_folder: str) -> None:
        if data_folder == "":
            raise DatabaseInitialisationError(f"The data_folder is required")
        self.__data_folder = data_folder
        tables: set[type] = set(DatabaseTable.registry.keys())
        id_fields: set[type] = set(DatabaseID.registry.keys())
        db_fields: set[type] = set(DatabaseField.registry.keys())
        field_types: set[type] = DatabaseFieldType.registry
        custom_serializer: set[type] = set(self.__custom_serializer.keys())

        # check if decorated classes are well-formed tables and field types
        if tables & field_types:
            raise DatabaseInitialisationError(
                f"The following classes are marked as DatabaseTable and " f"DatabaseFieldType:\n{tables & field_types}"
            )

        # check if decorated classes are well-formed tables and custom serializer
        if tables & custom_serializer:
            raise DatabaseInitialisationError(
                f"The following classes are marked as DatabaseTable and custom serializer:\n"
                f"{tables & custom_serializer}"
            )

        # check if decorated classes are well-formed field types and custom serializer
        if field_types & custom_serializer:
            raise DatabaseInitialisationError(
                f"The following classes are marked as DatabaseFieldType and custom serializer:\n"
                f"{field_types & custom_serializer}"
            )

        if tables.difference(id_fields):
            raise DatabaseInitialisationError(
                f"The following classes are marked as DatabaseTable but don't have an "
                f"id field:\n{tables.difference(id_fields)}"
            )

        if id_fields.difference(tables):
            raise DatabaseInitialisationError(
                f"The following classes are marked with an id field but not as an "
                f"DatabaseTable:\n{id_fields.difference(tables)}"
            )

        if db_fields.difference(tables.union(field_types)):
            raise DatabaseInitialisationError(
                f"The following classes are marked with fields but not as an "
                f"DatabaseTable or DatabaseFieldType:\n"
                f"{db_fields.difference(tables.union(field_types))}"
            )

        if field_types.difference(db_fields):
            raise DatabaseInitialisationError(
                f"The following classes are marked as DatabaseFieldType but don't have "
                f"any fields:\n{field_types.difference(db_fields)}"
            )

        # check if all used types are serializable
        for cls, field_dict in DatabaseField.registry.items():
            for field, (f_type, _) in field_dict.items():
                res = is_serializable(f_type, list(tables.union(field_types).union(self.__custom_serializer.keys())))
                if not res[0]:
                    raise DatabaseInitialisationError(
                        f"The following type of class {cls} is not serializable:\n" f"{field}: {res[1]}"
                    )

        # create database folder if not exist
        if not path.isdir(self.__data_folder):
            mkdir(self.__data_folder)

        self.__data_tracing_logger = self.__setup_data_tracing_logger()

        # create tables
        for cls, table_type in DatabaseTable.registry.items():
            id_field = DatabaseID.registry[cls][0]
            id_type = DatabaseID.registry[cls][1]
            fields = {}
            for f_name, (f_type, f_default) in DatabaseField.registry[cls].items():
                if type(f_type) is str:
                    f_type = self.__get_cls_from_cls_name(f_type)
                fields[f_name] = f_type, f_default
            self._tables[cls] = JsonDatabaseTable(self, cls, table_type, id_field, id_type, fields)

        # create field types
        for cls in DatabaseFieldType.registry:
            fields = {}
            for f_name, (f_type, f_default) in DatabaseField.registry[cls].items():
                if type(f_type) is str:
                    f_type = self.__get_cls_from_cls_name(f_type)
                fields[f_name] = f_type, f_default
            self._field_types[cls] = fields

        # load json data from files
        fill_functions = []
        for _, table in self._tables.items():
            fill_functions.append(table.load())

        for f in fill_functions:
            f()
        # Save DB to save all new inserted default values
        if not self.__test_mode:
            self.update("system")
        logging.info("Database fully loaded.")

    def add_object(self, obj: object, user: str = None) -> None:
        if user is None:
            logging.warning(f"JsonDatabase.add_object should be called with the user parameter.")
        # check if object is part of the database
        if type(obj) not in self._tables.keys():
            raise DatabaseInsertionError(f"{type(obj)} is not part of the Database.")
        self._tables[type(obj)].add_object(obj, user)
        self.update(user)

    def get_objects(self, tbl: Type[GET_TYPE]) -> immutabledict[int | str, GET_TYPE]:
        return self._tables[tbl].get_objects()

    def update(self, user: str = None) -> None:
        if user is None:
            logging.warning(f"JsonDatabase.update should be called with the user parameter.")
        for _, table in self._tables.items():
            table.save(user)

    def remove_object(self, obj: object, user: str = None) -> None:
        if user is None:
            logging.warning(f"JsonDatabase.remove_object should be called with the user parameter.")
        # check if object is part of the database
        if type(obj) not in self._tables.keys():
            raise DatabaseInsertionError(f"{type(obj)} is not part of the Database.")
        self._tables[type(obj)].remove_object(obj)
        self.update(user)

    def data_to_json(self, data: any, user: str) -> any:
        if data is None:
            return None
        f_type = type(data)
        if f_type in [bool, str, int, float]:
            return data
        if f_type in [tuple, list, set]:
            res = []
            for item in data:
                tmp = self.data_to_json(item, user)
                res.append(tmp)
            return {"type": f_type.__name__, "data": res}
        if f_type is dict:
            res = []
            for k, v in data.items():
                k_serialized = self.data_to_json(k, user)
                v_serialized = self.data_to_json(v, user)
                res.append({"key": k_serialized, "value": v_serialized})
            return {"type": "dict", "data": res}
        if f_type in self._tables.keys():
            if not self._tables[f_type].object_in_table(data):
                self.add_object(data, user)
            return {
                "type": f_type.__name__,
                "data": self._tables[f_type].get_key_of_object(data),
            }
        if f_type in self._field_types.keys():
            res = {}
            for field, ft_f_type in self._field_types[f_type].items():
                field_data = getattr(data, field, None)
                field_data_serialized = self.data_to_json(field_data, user)
                if field_data_serialized is not None:
                    res[field] = field_data_serialized
            return {"type": f_type.__name__, "data": res}
        if f_type in self.__custom_serializer.keys():
            return {"type": f_type.__name__, "data": self.__custom_serializer[f_type](data, self.data_to_json, user)}
        raise DatabaseSaveError(f"The following data is not serializable:\n{data}.")

    def json_to_value(self, data: any) -> any:
        data_type = type(data)
        if data_type in [str, int, float, bool]:
            return data
        if data is None:
            return None
        if data_type is dict:
            if "type" not in data or "data" not in data:
                raise DatabaseLoadError(f"The following data is not well formed:\n{data}.")
            if data["type"] == "list":
                res = []
                for i in data["data"]:
                    res.append(self.json_to_value(i))
                return res
            if data["type"] == "set":
                res = set()
                for i in data["data"]:
                    res.add(self.json_to_value(i))
                return res
            if data["type"] == "dict":
                res = {}
                for i in data["data"]:
                    res[self.json_to_value(i["key"])] = self.json_to_value(i["value"])
                return res
            if data["type"] == "tuple":
                res = []
                for i in data["data"]:
                    res.append(self.json_to_value(i))
                return tuple(res)
            # check if field is of type FieldType
            # key: name of FieldType
            # value: (class, fields of FieldType)
            tmp = {k.__name__: (k, v) for k, v in self._field_types.items()}
            if data["type"] in tmp:
                cls, fields = tmp[data["type"]]
                obj = cls.__new__(cls)  # noqa
                for field in fields:
                    if field in data["data"]:
                        setattr(obj, field, self.json_to_value(data["data"][field]))
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
            if data["type"] in tmp:
                if tmp[data["type"]].key_in_table(data["data"]):
                    return tmp[data["type"]].get_object(data["data"])
                else:
                    raise DatabaseLoadError(f"The id '{data['data']}' can not be found in Table " f"'{data['type']}'.")
            # check if field is of type DatabaseTable
            # key: name of DatabaseTable
            # value: deserialize function
            tmp = {k.__name__: v for k, v in self.__custom_deserializer.items()}
            if data["type"] in tmp:
                return tmp[data["type"]](data["data"], self.json_to_value)
        raise DatabaseLoadError(f"The following data is not well formed:\n{data}.")

    def write_data_trace(self, user: str, table_name: str, obj_id: int | str, old_data: dict) -> None:
        if self.__test_mode:
            return
        if self.__data_tracing_logger is None:
            raise DatabaseInitialisationError("JsonDatabase write_data_trace is called before init_tables is called")
        self.__data_tracing_logger.info(f"{user};{table_name};{obj_id};{json.dumps(old_data)}")

    def __get_cls_from_cls_name(self, cls_name: str) -> type:
        for cls in self._tables.keys() | self._field_types.keys() | self.__custom_serializer.keys():
            if cls_name == cls.__name__:
                return cls
        raise DatabaseInitialisationError(
            f"Can not find a class with name '{cls_name}' in DatabaseTables, DatabaseFieldTypes or the custom "
            f"serializer."
        )

    def __setup_data_tracing_logger(self) -> Logger | None:
        if self.__test_mode:
            return
        if not path.isdir(path.join(self.__data_folder, ".DataTracing")):
            mkdir(path.join(self.__data_folder, ".DataTracing"))
        logfile = path.join(self.__data_folder, ".DataTracing", "log.csv")
        logger = logging.getLogger("JsonDbDataTracing")
        logger.setLevel(logging.INFO)
        logger.propagate = False  # disables console prints

        formatter = logging.Formatter("%(asctime)s;%(message)s")

        file_handler = DataTracingFileHandler(logfile, 500 * 1024 * 1024)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        file_handler.setFormatter(formatter)
        return logger


class JsonDatabaseTable:

    def __init__(
        self,
        db: JsonDatabase,
        cls: type,
        table_type: TableType,
        id_field: str,
        id_type: type,
        fields: dict[str, tuple[any, any]],
    ) -> None:
        self.__db: JsonDatabase = db
        self.cls: CLS_TYPE = cls
        self.table_type: TableType = table_type
        self.id_field: str = id_field
        self.id_type: ID_TYPE = id_type
        self.fields: dict[str, tuple[any, any]] = fields
        self.__data: dict[ID_TYPE, CLS_TYPE] = {}
        self.__meta_data: dict[ID_TYPE, JsonDatabaseMetaData] = {}
        self.__json_data: dict[str | int, any] = {}
        self.__max_serialize_depth: int = 0

        # create folders and files is not exist
        if self.table_type == TableType.File:
            table_file = path.join(self.__db.data_folder, f"{cls.__name__}.json")
            if not path.isfile(table_file):
                with open(table_file, "w") as file:
                    file.write("{}")
        elif self.table_type == TableType.Folder:
            table_folder = path.join(self.__db.data_folder, cls.__name__)
            if not path.isdir(table_folder):
                mkdir(table_folder)

    def add_object(self, obj: object, user: str) -> None:
        if type(obj) is not self.cls:
            raise DatabaseInsertionError(f"{obj} does not belong to this table.")
        if id(obj) in [id(i) for i in self.__data.values()]:
            # object already in database -> update db
            return
        if self.id_type is UUID:
            obj_id = str(uuid4())
            setattr(obj, self.id_field, obj_id)
        else:
            # check if id is already in db
            obj_id = getattr(obj, self.id_field, None)
            if obj_id is None or obj_id == "":
                raise DatabaseInsertionError(f"The id field '{self.id_field}' of object {obj} is empty.")
            if obj_id in self.__data.keys():
                raise DatabaseInsertionError(f"The id '{obj_id}' already exists in table {type(obj)}.")
            if type(obj_id) is not self.id_type:
                raise DatabaseInsertionError(
                    f"The id field '{self.id_field}' of object {obj} is not of type " f"'{self.id_type}'."
                )
        # save object to db
        self.__data[obj_id] = obj
        self.__meta_data[obj_id] = JsonDatabaseMetaData()
        # serialize all objects to catch contained objects from other tables witch are not saved in the other tabel
        self.__serialize(user)

    def remove_object(self, obj: CLS_TYPE) -> None:
        if type(obj) is not self.cls:
            raise DatabaseKeyError(f"{obj} does not belong to this table.")
        if not self.object_in_table(obj):
            return
        self.__meta_data[self.get_key_of_object(obj)].is_deleted = True

    def key_in_table(self, key: ID_TYPE) -> bool:
        return key in self.__data.keys()

    def object_in_table(self, obj: CLS_TYPE) -> bool:
        if type(obj) is not self.cls:
            return False
        return getattr(obj, self.id_field, None) in self.__data.keys()

    def get_key_of_object(self, obj: CLS_TYPE) -> ID_TYPE:
        if type(obj) is not self.cls:
            raise DatabaseKeyError(f"{obj} does not belong to this table.")
        return getattr(obj, self.id_field, None)

    def get_object(self, key: ID_TYPE) -> CLS_TYPE:
        if key not in self.__data.keys():
            raise DatabaseKeyError(f"No object with key {key} in this table.")
        if self.__meta_data[key].is_deleted:
            logging.warning(f"Deleted object from table {self.cls.__name__} with key {key} is requested.")
        return self.__data[key]

    def get_objects(self) -> immutabledict[ID_TYPE, CLS_TYPE]:
        res = {}
        for k, obj in self.__data.items():
            if self.__meta_data[k].is_deleted:
                continue
            res[k] = obj
        return immutabledict(res)

    def __serialize(self, user: str) -> dict:
        self.__max_serialize_depth += 1
        my_serialize_depth = self.__max_serialize_depth
        break_outer = False
        json_data = {}
        for obj_id, obj in self.__data.items():
            obj_data = {}
            for field in self.fields.keys():
                field_data = getattr(obj, field, None)
                field_data_serialized = self.__db.data_to_json(field_data, user)
                if self.__max_serialize_depth > my_serialize_depth:
                    break_outer = True
                    break
                obj_data[field] = field_data_serialized
            if break_outer:
                break
            obj_data["$meta"] = self.__db.data_to_json(self.__meta_data[obj_id], user)
            json_data[obj_id] = obj_data
        if break_outer:
            json_data = self.__serialize(user)
        if my_serialize_depth == 1:
            self.__max_serialize_depth = 0
        return json_data

    def save(self, user: str) -> None:
        json_data = self.__serialize(user)
        # check for changes and write them to data tracing
        changes = False
        new_keys = set(json_data.keys())
        old_keys = set(self.__json_data.keys())
        for new_element in new_keys.difference(old_keys):
            changes = True
            self.__db.write_data_trace(user, self.cls.__name__, new_element, {})
        for old_element in old_keys.intersection(old_keys):
            if dict_changed(self.__json_data[old_element], json_data[old_element]):
                changes = True
                self.__db.write_data_trace(user, self.cls.__name__, old_element, self.__json_data[old_element])
        if not changes:
            return
        if self.table_type == TableType.File:
            table_file = path.join(self.__db.data_folder, f"{self.cls.__name__}.json")
            with open(table_file, "w") as json_file:
                json.dump(json_data, json_file, indent=4)
        elif self.table_type == TableType.Folder:
            table_folder = path.join(self.__db.data_folder, self.cls.__name__)
            for obj_id, obj_data in json_data.items():
                file_name = path.join(table_folder, f"{obj_id}.json")
                with open(file_name, "w") as json_file:
                    json.dump(obj_data, json_file, indent=4)
        self.__json_data = json_data

    def load(self) -> Callable[[], None]:
        if self.table_type == TableType.File:
            table_file = path.join(self.__db.data_folder, f"{self.cls.__name__}.json")
            with open(table_file, "r") as json_file:
                for obj_id, obj_data in json.load(json_file).items():
                    if self.id_type is int:
                        self.__create_and_insert_object(int(obj_id), obj_data)
                    elif self.id_type in [str, UUID]:
                        self.__create_and_insert_object(obj_id, obj_data)
        elif self.table_type == TableType.Folder:
            table_folder = path.join(self.__db.data_folder, self.cls.__name__)
            for file_name in get_filenames_from_dir(table_folder):
                with open(file_name, "r") as json_file:
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

    def __create_and_insert_object(self, obj_id: ID_TYPE, obj_data: dict) -> None:
        obj = CLS_TYPE.__new__(self.cls)
        setattr(obj, self.id_field, obj_id)
        self.__data[obj_id] = obj
        self.__json_data[obj_id] = obj_data
        self.__meta_data[obj_id] = self.__db.json_to_value(obj_data["$meta"])

    def __fill_object_from_dict(self, obj: CLS_TYPE, obj_data: dict[ID_TYPE, any]) -> None:
        for field in self.fields:
            if field in obj_data:
                setattr(obj, field, self.__db.json_to_value(obj_data[field]))
            else:
                # insert default value
                if type(self.fields[field][1]) in [str, int, float, bool, tuple]:
                    setattr(obj, field, self.fields[field][1])
                else:
                    setattr(obj, field, deepcopy(self.fields[field][1]))


class DataTracingFileHandler(RotatingFileHandler):

    def __init__(self, filename: str, max_bytes: int = 0):
        self.last_backup_cnt = 0
        super().__init__(
            filename=filename,
            mode="a",
            maxBytes=max_bytes,
            backupCount=1,
            encoding=None,
            delay=False,
        )

    # override
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None  # noqa
        # find first free log backup number and backup current log file to it
        for i in itertools.count(1):
            next_name = "%s.%d" % (self.baseFilename, i)
            if not path.exists(next_name):
                self.rotate(self.baseFilename, next_name)
                break
        if not self.delay:
            self.stream = self._open()


# When adding new fields to the JsonDatabaseMetaData class you have to insert them to:
# - the setUp function in tests/test_json_db.py
# - SZENE0_JSON, SZENE1_JSON, RECTANGLES_JSON, UUID1_JSON, UUID2_JSON in tests/test_json_database/db_test_save.py
@dataclass()
@DatabaseFieldType()
@DatabaseField("is_deleted", bool, False)
class JsonDatabaseMetaData:
    is_deleted: bool = False


def is_serializable(f_type: any, additional_types: list[type] = None) -> tuple[bool, str]:
    if additional_types is None:
        additional_types = []
    if f_type in [bool, str, int, float, dict]:
        return True, ""
    if type(f_type) is GenericAlias:
        if get_origin(f_type) in [tuple, list, set]:
            for arg in get_args(f_type):
                res = is_serializable(arg, additional_types)
                if not res[0]:
                    return False, res[1]
            return True, ""
    if type(f_type) is UnionType:
        for arg in get_args(f_type):
            res = is_serializable(arg, additional_types)
            if not res[0]:
                return False, res[1]
        return True, ""
    if f_type in additional_types:
        return True, ""
    if type(f_type) is str:
        if f_type in [cls.__name__ for cls in additional_types]:
            return True, ""
    return False, str(f_type)


def dict_changed(old: dict, new: dict) -> bool:
    new_keys = set(old.keys())
    old_keys = set(new.keys())
    if len(new_keys.symmetric_difference(old_keys)) != 0:
        return True
    # catch dict representing a set
    if "type" in new_keys and old["type"] == "set":
        if new["type"] != "set":
            return True
        if len(set(old["data"]).symmetric_difference(set(new["data"]))) != 0:
            return True
        return False
    for key in new_keys:
        if isinstance(old[key], type(new[key])):
            return True
        if type(old[key]) in [bool, str, int, float]:
            if old[key] != new[key]:
                return True
        elif type(old[key]) is list:
            if list_changed(old[key], new[key]):
                return True
        elif type(old[key]) is dict:
            if dict_changed(old[key], new[key]):
                return True
        else:
            raise DictDiffError(f"{type(old[key])} is not diff able")
    return False


def list_changed(old: list, new: list) -> bool:
    if len(old) != len(new):
        return True
    for o, n in old, new:
        if isinstance(o, type(n)):
            return True
        if type(o) in [bool, str, int, float]:
            if o != n:
                return True
        elif type(o) is list:
            if list_changed(o, n):
                return True
        elif type(o) is dict:
            if dict_changed(o, n):
                return True
        else:
            raise DictDiffError(f"{type(o)} is not diff able")
    return False


class DatabaseDefinitionError(Exception):
    def __init__(self, message):
        super().__init__(f"DatabaseDefinitionError: {message}")


class DatabaseInitialisationError(Exception):
    def __init__(self, message):
        super().__init__(f"DatabaseInitialisationError: {message}")


class DatabaseInsertionError(Exception):
    def __init__(self, message):
        super().__init__(f"DatabaseInsertionError: {message}")


class DatabaseLoadError(Exception):
    def __init__(self, message):
        super().__init__(f"DatabaseLoadError: {message}")


class DatabaseSaveError(Exception):
    def __init__(self, message):
        super().__init__(f"DatabaseSaveError: {message}")


class DatabaseKeyError(Exception):
    def __init__(self, message):
        super().__init__(f"DatabaseKeyError: {message}")


class DictDiffError(Exception):
    def __init__(self, message):
        super().__init__(f"DictDiffError: {message}")
