
class DatabaseTable:
    registry: dict[str, str] = {}

    def __init__(self, cls: type = None, folder: bool = False, file: bool = False):
        self.folder: bool = folder
        self.file: bool = file
        if cls:
            raise Exception(f"DatabaseTable must be set to file or folder: {cls}")

    def __call__(self, cls: type):
        if self.folder == self.file:
            # empty brackets
            raise Exception(f"DatabaseTable must be set to file or folder: {cls}")
        # check if class with name exists already
        if cls.__name__ in self.registry:
            raise Exception(f"DatabaseTable with name {cls.__name__} already exists.")
        self.registry[cls.__name__] = 'folder' if self.folder else 'file'
        return cls
