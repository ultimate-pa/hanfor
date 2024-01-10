from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, TableType


@DatabaseTable(TableType.File)
@DatabaseID('job_id', str)
@DatabaseField('att_str', str)
@dataclass()
class TestClass1:
    job_id: str
    att_str: str


@DatabaseTable(TableType.File)
@DatabaseID('job_id', int)
@DatabaseField('att_int', int)
@DatabaseField('att_ref', TestClass1)
@dataclass()
class TestClass2:
    job_id: int | None
    att_int: int
    att_ref: TestClass1 | None


@DatabaseTable(TableType.File)
@DatabaseID(use_uuid=True)
@DatabaseField('att_str', str)
@dataclass()
class TestClass3:
    att_str: str


@DatabaseTable(TableType.File)
@DatabaseID('job_id', int)
@DatabaseField('att_ref', TestClass3)
@dataclass()
class TestClass4:
    job_id: int
    att_ref: TestClass3 | None
