import inspect
from types import GenericAlias, UnionType
from typing import get_origin, get_args
from uuid import UUID


class DatabaseTable:
    registry: dict[type, str] = {}

    def __init__(self, cls: type = None, folder: bool = False, file: bool = False):
        self._folder: bool = folder
        self.file: bool = file
        if cls:
            raise Exception(f"DatabaseTable must be set to file or folder: {cls}")

    def __call__(self, cls: type):
        if self._folder == self.file:
            # empty brackets
            raise Exception(f"DatabaseTable must be set to file or folder: {cls}")
        # check if class with name exists already
        if cls.__name__ in [c.__name__ for c in self.registry]:
            raise Exception(f"DatabaseTable with name {cls.__name__} already exists.")
        self.registry[cls] = 'folder' if self._folder else 'file'
        return cls


class DatabaseID:
    registry: dict[type, (str, type)] = {}

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
            self.registry[cls] = (None, UUID)
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
    registry: dict[type, dict[str, any]] = {}

    def __init__(self, field: str = None, f_type: type = None):
        self._field = field
        self._type = f_type
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
        self.registry[cls][self._field] = self._type
        return cls


class DatabaseFieldType:
    registry: set[type] = set()

    def __init__(self, cls: type = None):
        if cls:
            raise Exception(f"DatabaseFieldType must be called with brackets: {cls}")

    def __call__(self, cls: type):
        self.registry.add(cls)
        return cls


class JsonDatabase:

    def __init__(self):
        pass

    def init_tables(self):
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
            for field, f_type in field_dict.items():
                res = is_serializable(f_type, list(tables.union(field_types)))
                if not res[0]:
                    raise Exception(f"The following type of class {cls} is not serializable:\n{field}: {res[1]}")


def is_serializable(f_type: any, additional_types: list[type] = None) -> tuple[bool, str]:
    if additional_types is None:
        additional_types = []
    if f_type is bool:
        return True, ''
    if f_type is str:
        return True, ''
    if f_type is int:
        return True, ''
    if f_type is float:
        return True, ''
    if type(f_type) is GenericAlias:
        if get_origin(f_type) in [tuple, list, dict, set]:
            for arg in get_args(f_type):
                res = is_serializable(arg)
                if not res[0]:
                    return False, res[1]
            return True, ''
    if type(f_type) is UnionType:
        for arg in get_args(f_type):
            res = is_serializable(arg)
            if not res[0]:
                return False, res[1]
        return True, ''
    if f_type in additional_types:
        return True, ''
    return False, str(f_type)
