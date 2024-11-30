from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseNonSavedField,
    TableType,
)

from threading import Lock


JSON_DATA = (
    "{\n"
    '    "test0": {\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    },\n"
    '    "test1": {\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    }\n"
    "}"
)


@DatabaseTable(TableType.File)
@DatabaseID("job_id", str)
@DatabaseNonSavedField("att_str", "Hello World")
@DatabaseNonSavedField("att_int", 42)
@DatabaseNonSavedField("att_lock", Lock())
class TestClassFile:

    def __init__(self, job_id: str, s: str, i: int):
        self.job_id: str = job_id
        self.att_str: str = s
        self.att_int: int = i
        self.att_lock: Lock = Lock()

    def get_values(self) -> tuple[str, str, int]:
        return self.job_id, self.att_str, self.att_int
