from dataclasses import dataclass
from json_db_connector.json_db import DatabaseFieldType


@DatabaseFieldType()
@dataclass()
class TestClass:
    job_id: str
