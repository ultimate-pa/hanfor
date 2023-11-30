from dataclasses import dataclass
from json_db_connector.json_db import DatabaseTable


@DatabaseTable(file=True, folder=True)
@dataclass()
class TestClass:
    job_id: str
