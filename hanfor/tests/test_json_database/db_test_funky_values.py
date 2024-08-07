from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, TableType
from dataclasses import dataclass


@DatabaseTable(TableType.File)
@DatabaseID("job_id", int)
@DatabaseField("att_str", str)
@dataclass()
class TestClassFile:
    job_id: int
    att_str: str
