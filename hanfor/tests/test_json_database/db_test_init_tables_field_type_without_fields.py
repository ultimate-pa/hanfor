from dataclasses import dataclass
from json_db_connector.json_db import DatabaseFieldType, DatabaseID, DatabaseField


@DatabaseFieldType()
@DatabaseField('att_bool', bool)
@DatabaseField('att_str', str)
@DatabaseField('att_int', int)
@dataclass()
class TestClass:
    job_id: str
    att_bool: bool
    att_str: str
    att_int: int


@DatabaseFieldType()
@dataclass()
class TestClassWithoutFields:
    job_id: str


