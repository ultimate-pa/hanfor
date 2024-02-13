from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseField,
    TableType,
)


@DatabaseTable(TableType.File)
@DatabaseID("job_id", str)
@DatabaseField("att_str", str)
@DatabaseField("att_int", int)
class TestClassFile:

    def __init__(self, job_id: str, s: str, i: int):
        self.job_id: str = job_id
        self.att_str: str = s
        self.att_int: int = i

    def get_values(self) -> tuple[str, str, int]:
        return self.job_id, self.att_str, self.att_int
