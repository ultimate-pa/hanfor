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
@DatabaseField('att_tuple', tuple[int, int])
@DatabaseField('att_dict', dict)
@DatabaseField('att_set', set[int])
@dataclass()
class TestClassFile:
    job_id: str
    att_tuple: tuple[int, int]
    att_dict: dict[int, TestClassFieldType]
    att_set: set[int]


@DatabaseTable(folder=True)
@DatabaseID('job_id', int)
@DatabaseField('att_list', list[TestClassFile])
@dataclass()
class TestClassFolder:
    job_id: int
    att_list: list[TestClassFile]


@DatabaseTable(file=True)
@DatabaseID(use_uuid=True)
@DatabaseField('att_str', str)
@dataclass()
class TestUUID:
    att_str: str
