from dataclasses import dataclass, field
from typing import Type

from flask import Blueprint, Response, current_app, jsonify, render_template, request
from flask.views import MethodView
from pydantic import BaseModel

from configuration.tags import STANDARD_TAGS
from defaults import Color
from reqtransformer import Requirement

from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField, DatabaseNonSavedField
from uuid import UUID

BUNDLE_JS = "dist/tags-bundle.js"
blueprint = Blueprint("tags", __name__, template_folder="templates", url_prefix="/tags")
api_blueprint = Blueprint("api_tags", __name__, url_prefix="/api/tags")


@blueprint.route("/", methods=["GET"])
def index():
    return render_template("tags/index.html", BUNDLE_JS=BUNDLE_JS)


@DatabaseTable(TableType.File)
@DatabaseID("uuid", use_uuid=True)
@DatabaseField("name", str)
@DatabaseField("color", str)
@DatabaseField("internal", bool)
@DatabaseField("description", str)
@DatabaseNonSavedField("used_by", [])
@dataclass
class Tag:
    name: str
    color: str
    internal: bool
    description: str
    used_by: list = field(default_factory=list)
    uuid: UUID = None


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view("tags_api")
    bp.add_url_rule("/", defaults={"name": None}, view_func=view, methods=["GET"])
    bp.add_url_rule("/<string:command>", view_func=view, methods=["POST"])
    bp.add_url_rule("/<string:name>", view_func=view, methods=["GET", "PUT", "PATCH", "DELETE"])


class TagsApi(MethodView):
    INIT_TAGS = {
        "Type_inference_error": {"color": Color.BS_DANGER.value, "internal": True, "description": ""},
        "incomplete_formalization": {"color": Color.BS_WARNING.value, "internal": True, "description": ""},
        "has_formalization": {"color": Color.BS_SUCCESS.value, "internal": True, "description": ""},
        "unknown_type": {"color": Color.BS_DANGER.value, "internal": True, "description": ""},
    }

    def __init__(self):
        self.app = current_app
        self.__available_tags: dict[str, Tag] = {}
        self.__load()

    def __load(self):
        # load tags
        for tag in self.app.db.get_objects(Tag).values():
            self.__available_tags[tag.name] = tag
            tag.used_by.clear()

            # insert initial tags
        for name, values in self.INIT_TAGS.items():
            if name not in self.__available_tags.keys():
                tag = Tag(name, **values)
                self.app.db.add_object(tag)
                self.__available_tags[tag.name] = tag

        # create used by relation
        for req in self.app.db.get_objects(Requirement).values():
            for tag_name in req.tags:
                self.__available_tags[tag_name].used_by.append(req.rid)

        for tag in self.__available_tags.values():
            tag.used_by.sort()

    def __store(self):
        self.app.db.update()

    def add_if_new(self, tag_name: str) -> None:
        if tag_name not in self.__available_tags:
            self.add(tag_name)

    def add(
        self, tag_name: str, tag_color: str = Color.BS_INFO.value, tag_internal: bool = False, tag_description: str = ""
    ) -> None:
        self.app.db.add_object(Tag(tag_name, tag_color, tag_internal, tag_description))

    def get(self, name: str | None) -> str | dict | tuple | Response:
        if name is None:
            return jsonify([tag for tag in self.__available_tags.values()])

        if name in self.__available_tags:
            return jsonify(self.__available_tags[name])

        raise ValueError(f"Unknown tag `{name}`.")

    def post(self, command: str) -> str | dict | tuple | Response:
        response_data = {}

        match command:
            case "add_standard":
                for name, properties in STANDARD_TAGS.items():
                    self.add(name, properties["color"], properties["internal"], properties["description"])
            case _:
                raise ValueError(f"Unknown command `{command}`.")

        return response_data

    def put(self, name: str) -> str | dict | tuple | Response:
        raise NotImplementedError

    def patch(self, name: str) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            name_new: str = ""
            occurrences: list[str] = []
            color: str = Color.BS_INFO.value
            description: str = ""
            internal: bool = False

            class Config:
                anystr_strip_whitespace = True

        request_data = RequestData.model_validate(request.json)
        response_data = {}

        for rid in request_data.occurrences:
            if rid == "":  # TODO frontend should not send an empty string
                continue
            requirement = self.app.db.get_object(Requirement, rid)
            comment = requirement.tags.pop(name)
            requirement.tags[request_data.name_new] = comment

        self.__available_tags[name].name = request_data.name_new
        self.__available_tags[name].color = request_data.color
        self.__available_tags[name].description = request_data.description
        self.__available_tags[name].internal = request_data.internal
        self.app.db.update()

        if name != request_data.name_new:
            self.__available_tags[request_data.name_new] = self.__available_tags[name]
            del self.__available_tags[name]

        return response_data

    def delete(self, name: str) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            occurrences: list[str]

            class Config:
                anystr_strip_whitespace = True

        request_data = RequestData.model_validate(request.json)
        response_data = {}

        for rid in request_data.occurrences:
            requirement = self.app.db.get_object(Requirement, rid)
            requirement.tags.pop(name)
        self.app.db.update()

        self.__available_tags.pop(name)
        self.__store()

        return response_data


register_api(api_blueprint, TagsApi)
