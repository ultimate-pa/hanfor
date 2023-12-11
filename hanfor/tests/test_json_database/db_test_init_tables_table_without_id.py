from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID


@DatabaseTable(file=True)
@DatabaseID('job_id', str)
@dataclass()
class TestClass:
    job_id: str


@DatabaseTable(file=True)
@dataclass()
class TestClassWithoutID:
    job_id: str
