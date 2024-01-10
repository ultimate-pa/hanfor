from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, TableType


@DatabaseTable(TableType.File)
@DatabaseID('job_id', str)
@dataclass()
class TestClass:
    job_id: str


@DatabaseTable(TableType.File)
@dataclass()
class TestClassWithoutID:
    job_id: str
