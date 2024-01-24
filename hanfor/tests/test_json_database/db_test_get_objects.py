from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, DatabaseFieldType, TableType


@DatabaseTable(TableType.File)
@DatabaseID('job_id', str)
@DatabaseField('att_str', str)
@DatabaseField('att_int', int)
@dataclass()
class TestClassFile:
    job_id: str
    att_str: str
    att_int: int
