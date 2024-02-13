from dataclasses import dataclass
from json_db_connector.json_db import DatabaseID


@DatabaseID("job_id", str)
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


@DatabaseID("job_id", int)
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


@DatabaseID("uuid", use_uuid=True)
@dataclass()
class TestClassUuid:
    job_id: str
