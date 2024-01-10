from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, TableType


@DatabaseTable(TableType.File)
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


@DatabaseTable(TableType.Folder)
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
