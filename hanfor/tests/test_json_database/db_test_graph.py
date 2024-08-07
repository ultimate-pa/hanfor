from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseField,
    TableType,
)


@DatabaseTable(TableType.Folder)
@DatabaseID("label", str)
@DatabaseField("n", int)
@DatabaseField("initial", bool)
@DatabaseField("successors", bool)
@DatabaseField("predecessors", bool)
class Node:
    def __init__(self, label: str, n: int, initial: bool = False) -> None:
        self.label = label
        self.n = n
        self.initial = initial
        self.successors = []
        self.predecessors = []
