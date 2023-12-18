from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, DatabaseFieldType


@DatabaseFieldType()
@DatabaseField('att_bool', bool)
@DatabaseField('att_str', str)
@DatabaseField('att_int', int)
@DatabaseField('att_float', float)
@dataclass()
class TestClassFieldType:
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float


@DatabaseTable(file=True)
@DatabaseID('job_id', str)
@DatabaseField('att_str', str)
@dataclass()
class TestClassReference:
    job_id: str
    att_str: str


@DatabaseTable(file=True)
@DatabaseID('job_id', str)
@DatabaseField('att_ref', TestClassReference)
@dataclass()
class TestClassFile:
    job_id: str
    att_ref: TestClassReference
