from dataclasses import dataclass
from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseField,
    DatabaseFieldType,
    TableType,
)


@DatabaseFieldType()
@DatabaseField("att_bool", bool, True)
@DatabaseField("att_str", str, "default")
@DatabaseField("att_int", int, 42)
@DatabaseField("att_float", float, 3.14)
@DatabaseField("att_list", list[int], [1, 2])
@dataclass()
class TestClassFieldType:
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float
    att_list: list[int]


@DatabaseTable(TableType.File)
@DatabaseID("job_id", str)
@DatabaseField("att_bool", bool, True)
@DatabaseField("att_str", str, "default")
@DatabaseField("att_int", int, 42)
@DatabaseField("att_float", float, 3.14)
@DatabaseField("att_tuple", tuple[int, int], (1, 2))
@DatabaseField("att_dict", dict, {0: "zero", 1: "one"})
@DatabaseField("att_set", set[int], {1, 2})
@DatabaseField(
    "att_list",
    list[TestClassFieldType],
    [TestClassFieldType(False, "individual", 21, 9.81, [])],
)
@DatabaseField("att_ft", TestClassFieldType)
@dataclass()
class TestClassFile:
    job_id: str
    att_bool: bool
    att_str: str
    att_int: int
    att_float: float
    att_tuple: tuple[int, int]
    att_dict: dict[int, str]
    att_set: set[int]
    att_list: list[TestClassFieldType]
    att_ft: TestClassFieldType | None
