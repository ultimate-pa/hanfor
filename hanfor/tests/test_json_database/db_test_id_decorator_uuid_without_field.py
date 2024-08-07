from dataclasses import dataclass
from json_db_connector.json_db import DatabaseID


@DatabaseID(use_uuid=True)
@dataclass()
class TestClassUuid:
    job_id: str
