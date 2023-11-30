from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID


@DatabaseTable(file=True)
@DatabaseID('job_id', str)
@dataclass()
class TestClassFile:
    job_id: str


@DatabaseTable(folder=True)
@DatabaseID('job_id', int)
@dataclass()
class TestClassFolder:
    job_id: int
