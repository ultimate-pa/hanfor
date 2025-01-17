from dataclasses import dataclass
from typing import Any

from json_db_connector.json_db import DatabaseField


@DatabaseField("any_field", Any)
@dataclass()
class TestClass:
    any_field: Any
