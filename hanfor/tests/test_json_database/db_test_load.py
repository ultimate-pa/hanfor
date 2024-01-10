from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, DatabaseID, DatabaseField, DatabaseFieldType, TableType


@DatabaseFieldType()
@DatabaseField('att_bool', bool, True)
@DatabaseField('att_str', str, 'default')
@DatabaseField('att_int', int, 42)
@DatabaseField('att_float', float, 3.14)
@dataclass()
class TestClassFieldType:
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float


@DatabaseTable(TableType.File)
@DatabaseID('job_id', str)
@DatabaseField('att_tuple', tuple[int, int], (42, 42))
@DatabaseField('att_dict', dict, {42: None})
@DatabaseField('att_set', set[int], {42})
@dataclass()
class TestClassFile:
    job_id: str
    att_tuple: tuple[int, int]
    att_dict: dict[int, TestClassFieldType]
    att_set: set[int]


@DatabaseTable(TableType.Folder)
@DatabaseID('job_id', int)
@DatabaseField('att_list', list[TestClassFile], [None])
@dataclass()
class TestClassFolder:
    job_id: int
    att_list: list[TestClassFile]


@DatabaseTable(TableType.File)
@DatabaseID(use_uuid=True)
@DatabaseField('att_str', str, 'default')
@dataclass()
class TestUUID:
    att_str: str
