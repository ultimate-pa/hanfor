from json_db_connector.json_db import DatabaseTable, DatabaseID, TableType, DatabaseField
from dataclasses import dataclass


@DatabaseTable(TableType.File)
@DatabaseID("job_id", str)
@DatabaseField("n", int)
@dataclass()
class TestClassFile:
    job_id: str
    n: int
