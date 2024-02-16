from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseField,
    TableType,
    DatabaseFieldType,
)
from dataclasses import dataclass


@DatabaseFieldType()
@DatabaseField("foo", dict)
@DatabaseField("bar", dict)
@dataclass
class DataClassThing:
    def __init__(self, foostr=None):
        self.foo = dict()
        self.bar = dict()
        if foostr:
            self.foo[foostr] = foostr


@DatabaseTable(TableType.Folder)
@DatabaseID("job_id", str)
@DatabaseField("att_str", str)
@DatabaseField("x", str)
@DatabaseField("__dat1", DataClassThing)
@DatabaseField("__dat2", DataClassThing)
@DatabaseField("updatethis", str, default="defaultvalue")
class TestClassFile:

    def __init__(self, job_id: str, s: str, x: str):
        self.job_id: str = job_id
        self.att_str: str = s
        self.x: str = x
        self.__dat1: DataClassThing = DataClassThing("aasdfppended default element")
        self.__dat2: DataClassThing = DataClassThing("appended default element")
