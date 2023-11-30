from dataclasses import dataclass
from json_db_connector.json_db import DatabaseID


@DatabaseID('job_id', int)
@DatabaseID('job_id', int)
@dataclass()
class TestClass:
    job_id: str
