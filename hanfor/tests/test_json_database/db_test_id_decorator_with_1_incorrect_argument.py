from dataclasses import dataclass
from json_db_connector.json_db import DatabaseID


@DatabaseID(5)
@dataclass()
class TestClass:
    job_id: str
