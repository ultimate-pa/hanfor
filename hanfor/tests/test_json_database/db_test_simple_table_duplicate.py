from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable, TableType


@DatabaseTable(TableType.File)
@dataclass()
class TestClassFile:
    job_id: str
