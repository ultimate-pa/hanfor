from dataclasses import dataclass
from json_db_connector.json_db import DatabaseID


@DatabaseID(5)  # noqa
@dataclass()
class TestClass:
    job_id: str
