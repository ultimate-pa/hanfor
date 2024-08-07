from dataclasses import dataclass
from json_db_connector.json_db import DatabaseField


@DatabaseField(5)  # noqa
@dataclass()
class TestClass:
    job_id: str
