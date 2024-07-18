from dataclasses import dataclass
from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseField,
    TableType,
)


@DatabaseTable(TableType.File)
@DatabaseID("job_id", str)
@DatabaseField("att_bool", bool)
@DatabaseField("att_str", str)
@dataclass()
class TestClassFile:
    job_id: str
    att_bool: bool
    att_str: str


@DatabaseTable(TableType.Folder)
@DatabaseID("job_id", int)
@DatabaseField("att_bool", bool)
@DatabaseField("att_str", str)
@DatabaseField("att_int", int)
@DatabaseField("att_float", float)
@DatabaseField("att_class_file", DatabaseTable)
@dataclass()
class TestClassFolder:
    job_id: int
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float
    att_class_file: DatabaseTable
