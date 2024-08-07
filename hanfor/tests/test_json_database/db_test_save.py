from dataclasses import dataclass, field
from json_db_connector.json_db import (
    DatabaseTable,
    DatabaseID,
    DatabaseField,
    DatabaseFieldType,
    TableType,
)
from uuid import uuid4


@DatabaseFieldType()
@DatabaseField("name", str)
@DatabaseField("rgb", tuple[float, float, float])
@dataclass()
class TestColor:
    name: str
    rgb: tuple[float, float, float]


@DatabaseTable(TableType.File)
@DatabaseID("name", str)
@DatabaseField("visible", bool)
@DatabaseField("position", dict)
@DatabaseField("color", TestColor)
@dataclass()
class TestRectangle:
    name: str
    visible: bool
    position: dict[str, int]
    color: TestColor | None


@DatabaseTable(TableType.Folder)
@DatabaseID("szene_id", int)
@DatabaseField("keywords", set[str])
@DatabaseField("rectangles", list[TestRectangle])
@dataclass()
class TestSzene:
    szene_id: int
    keywords: set[str]
    rectangles: list[TestRectangle]


@DatabaseTable(TableType.File)
@DatabaseID("uuid", use_uuid=True)
@DatabaseField("att_str", str)
@dataclass()
class TestUUID:
    att_str: str
    uuid: str = field(default_factory=lambda: str(uuid4()))


SZENE0_JSON = (
    "{\n"
    '    "rectangles": {\n'
    '        "type": "list",\n'
    '        "data": [\n'
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect0"\n'
    "            },\n"
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect1"\n'
    "            },\n"
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect2"\n'
    "            }\n"
    "        ]\n"
    "    },\n"
    '    "keywords": {\n'
    '        "type": "set",\n'
    '        "data": [\n'
    '            "zero"\n'
    "        ]\n"
    "    },\n"
    '    "$meta": {\n'
    '        "type": "JsonDatabaseMetaData",\n'
    '        "data": {\n'
    '            "is_deleted": false\n'
    "        }\n"
    "    }\n"
    "}"
)

SZENE1_JSON = (
    "{\n"
    '    "rectangles": {\n'
    '        "type": "list",\n'
    '        "data": []\n'
    "    },\n"
    '    "keywords": {\n'
    '        "type": "set",\n'
    '        "data": [\n'
    '            "one"\n'
    "        ]\n"
    "    },\n"
    '    "$meta": {\n'
    '        "type": "JsonDatabaseMetaData",\n'
    '        "data": {\n'
    '            "is_deleted": false\n'
    "        }\n"
    "    }\n"
    "}"
)

SZENE1_JSON_1 = (
    "{\n"
    '    "rectangles": {\n'
    '        "type": "list",\n'
    '        "data": [\n'
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect0"\n'
    "            }\n"
    "        ]\n"
    "    },\n"
    '    "keywords": {\n'
    '        "type": "set",\n'
    '        "data": [\n'
    '            "one"\n'
    "        ]\n"
    "    },\n"
    '    "$meta": {\n'
    '        "type": "JsonDatabaseMetaData",\n'
    '        "data": {\n'
    '            "is_deleted": false\n'
    "        }\n"
    "    }\n"
    "}"
)

SZENE1_JSON_2 = (
    "{\n"
    '    "rectangles": {\n'
    '        "type": "list",\n'
    '        "data": [\n'
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect0"\n'
    "            },\n"
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect0"\n'
    "            }\n"
    "        ]\n"
    "    },\n"
    '    "keywords": {\n'
    '        "type": "set",\n'
    '        "data": [\n'
    '            "one"\n'
    "        ]\n"
    "    },\n"
    '    "$meta": {\n'
    '        "type": "JsonDatabaseMetaData",\n'
    '        "data": {\n'
    '            "is_deleted": false\n'
    "        }\n"
    "    }\n"
    "}"
)

SZENE1_JSON_3 = (
    "{\n"
    '    "rectangles": {\n'
    '        "type": "list",\n'
    '        "data": [\n'
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect0"\n'
    "            },\n"
    "            {\n"
    '                "type": "TestRectangle",\n'
    '                "data": "rect0"\n'
    "            }\n"
    "        ]\n"
    "    },\n"
    '    "keywords": {\n'
    '        "type": "set",\n'
    '        "data": [\n'
    '            "one"\n'
    "        ]\n"
    "    },\n"
    '    "$meta": {\n'
    '        "type": "JsonDatabaseMetaData",\n'
    '        "data": {\n'
    '            "is_deleted": true\n'
    "        }\n"
    "    }\n"
    "}"
)

RECTANGLES_JSON = (
    "{\n"
    '    "rect0": {\n'
    '        "color": {\n'
    '            "type": "TestColor",\n'
    '            "data": {\n'
    '                "rgb": {\n'
    '                    "type": "tuple",\n'
    '                    "data": [\n'
    "                        0.0,\n"
    "                        1.0,\n"
    "                        0.0\n"
    "                    ]\n"
    "                },\n"
    '                "name": "green"\n'
    "            }\n"
    "        },\n"
    '        "position": {\n'
    '            "type": "dict",\n'
    '            "data": [\n'
    "                {\n"
    '                    "key": "x",\n'
    '                    "value": 0\n'
    "                },\n"
    "                {\n"
    '                    "key": "y",\n'
    '                    "value": 0\n'
    "                }\n"
    "            ]\n"
    "        },\n"
    '        "visible": true,\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    },\n"
    '    "rect1": {\n'
    '        "color": {\n'
    '            "type": "TestColor",\n'
    '            "data": {\n'
    '                "rgb": {\n'
    '                    "type": "tuple",\n'
    '                    "data": [\n'
    "                        0.0,\n"
    "                        0.0,\n"
    "                        1.0\n"
    "                    ]\n"
    "                },\n"
    '                "name": "blue"\n'
    "            }\n"
    "        },\n"
    '        "position": {\n'
    '            "type": "dict",\n'
    '            "data": [\n'
    "                {\n"
    '                    "key": "x",\n'
    '                    "value": 1\n'
    "                },\n"
    "                {\n"
    '                    "key": "y",\n'
    '                    "value": 1\n'
    "                }\n"
    "            ]\n"
    "        },\n"
    '        "visible": false,\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    },\n"
    '    "rect2": {\n'
    '        "color": null,\n'
    '        "position": {\n'
    '            "type": "dict",\n'
    '            "data": [\n'
    "                {\n"
    '                    "key": "x",\n'
    '                    "value": 2\n'
    "                },\n"
    "                {\n"
    '                    "key": "y",\n'
    '                    "value": 2\n'
    "                }\n"
    "            ]\n"
    "        },\n"
    '        "visible": true,\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    }\n"
    "}"
)

UUID1_JSON = (
    "{\n"
    '    "%s": {\n'
    '        "att_str": "one",\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    }\n"
    "}"
)

UUID2_JSON = (
    "{\n"
    '    "%s": {\n'
    '        "att_str": "one",\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    },\n"
    '    "%s": {\n'
    '        "att_str": "two",\n'
    '        "$meta": {\n'
    '            "type": "JsonDatabaseMetaData",\n'
    '            "data": {\n'
    '                "is_deleted": false\n'
    "            }\n"
    "        }\n"
    "    }\n"
    "}"
)
