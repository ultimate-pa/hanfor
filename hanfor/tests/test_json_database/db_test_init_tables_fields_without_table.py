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
@DatabaseField("att_int", int)
@dataclass()
class TestClass:
    job_id: str
    att_bool: bool
    att_str: str
    att_int: int


@DatabaseField("att_bool", bool)
@DatabaseField("att_str", str)
@DatabaseField("att_int", int)
@dataclass()
class TestClassWithoutTable:
    job_id: str
    att_bool: bool
    att_str: str
    att_int: int
