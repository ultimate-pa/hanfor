from dataclasses import dataclass
from json_db_connector.json_db import DatabaseField


@DatabaseField('job_id', 'str')
@dataclass()
class TestClass:
    job_id: str
