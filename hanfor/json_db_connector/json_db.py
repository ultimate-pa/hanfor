import inspect


class DatabaseTable:
    registry: dict[str, str] = {}

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
        if cls.__name__ in self.registry:
            raise Exception(f"DatabaseTable with name {cls.__name__} already exists.")
        self.registry[cls.__name__] = 'folder' if self._folder else 'file'
        return cls


class DatabaseID:
    registry = {}

    def __init__(self, field: str = None, f_type: type = None):
        self._id_field = field
        self._type = f_type
        if field is None:
            # empty brackets
            return
        if inspect.isclass(field):
            raise Exception(f"DatabaseID must be set to the name and type of an field of the class: {field}")

    def __call__(self, cls):
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
        if cls.__name__ in self.registry:
            raise Exception(f"DatabaseTable with name {cls} already has an id field.")
        self.registry[cls.__name__] = (self._id_field, self._type)
        return cls
