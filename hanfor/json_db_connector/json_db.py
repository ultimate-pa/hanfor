import inspect
from types import GenericAlias
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
    registry: dict[str, dict[str, any]] = {}

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
