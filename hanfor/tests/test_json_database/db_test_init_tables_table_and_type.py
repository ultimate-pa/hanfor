from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseFieldType


@DatabaseTable(file=True)
@DatabaseID('job_id', str)
@DatabaseFieldType()
@dataclass()
class TestClass:
    job_id: str


@DatabaseTable(file=True)
@DatabaseID('job_id', str)
@dataclass()
class TestClassTable:
    job_id: str


@DatabaseFieldType()
@dataclass()
class TestClassFieldType:
    job_id: str
