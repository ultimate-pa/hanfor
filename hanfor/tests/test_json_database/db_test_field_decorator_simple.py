from dataclasses import dataclass
from json_db_connector.json_db import DatabaseField


@DatabaseField('att_bool', bool)
@DatabaseField('att_str', str)
@DatabaseField('att_int', int)
@DatabaseField('att_float', float)
@DatabaseField('att_tuple', tuple[int, str])
@DatabaseField('att_list', list[str])
@DatabaseField('att_dict', dict[int, str])
@DatabaseField('att_set', set[int])
@dataclass()
class TestClassFile:
    job_id: str
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float
    att_tuple: tuple[int, str]
    att_list: list[str]
    att_dict: dict[int, str]
    att_set: set[int]


@DatabaseField('att_bool', bool)
@DatabaseField('att_str', str)
@DatabaseField('att_int', int)
@DatabaseField('att_float', float)
@DatabaseField('att_class_file', TestClassFile)
@dataclass()
class TestClassFolder:
    job_id: int
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float
    att_tuple: tuple[int, str]
    att_list: list[str]
    att_dict: dict[int, str]
    att_set: set[int]
    att_class_file: TestClassFile
