from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseFieldType, TableType


@DatabaseTable(TableType.File)
@DatabaseID('job_id', str)
@DatabaseFieldType()
@dataclass()
class TestClass:
    job_id: str


@DatabaseTable(TableType.File)
@DatabaseID('job_id', str)
@dataclass()
class TestClassTable:
    job_id: str


@DatabaseFieldType()
@dataclass()
class TestClassFieldType:
    job_id: str
