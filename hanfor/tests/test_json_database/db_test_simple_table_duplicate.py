from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable


@DatabaseTable(file=True)
@dataclass()
class TestClassFile:
    job_id: str
