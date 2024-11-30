from dataclasses import dataclass, field
from typing import Type

from hanfor_flask import current_app
from flask import Blueprint, Response, jsonify, render_template, request, abort
from flask.views import MethodView
from pydantic import BaseModel

from configuration.tags import STANDARD_TAGS
from defaults import Color

from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField, DatabaseNonSavedField
from uuid import uuid4
from static_utils import SessionValue

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
    uuid: str = field(default_factory=lambda: str(uuid4()))

    def __hash__(self):
        return hash(self.uuid)


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
        "Ultimate_raw_data": {"color": Color.BS_GRAY.value, "internal": False, "description": ""},
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
                # add initial tag to SessionValues
            if not self.app.db.key_in_table(SessionValue, f"TAG_{name}"):
                self.app.db.add_object(SessionValue(f"TAG_{name}", self.__available_tags[name]))

        # create used by relation
        for req in self.app.db.get_objects("Requirement").values():  # type: "Requirement"
            for tag in req.tags:
                self.__available_tags[tag.name].used_by.append(req.rid)

        for tag in self.__available_tags.values():
            tag.used_by.sort()

    def add_if_new(self, tag_name: str) -> None:
        if tag_name not in self.__available_tags:
            self.add(tag_name)

    def add(
        self, tag_name: str, tag_color: str = Color.BS_INFO.value, tag_internal: bool = False, tag_description: str = ""
    ) -> None:
        t = Tag(tag_name, tag_color, tag_internal, tag_description)
        self.app.db.add_object(t)
        self.__available_tags[tag_name] = t

    def tag_exists(self, name: str) -> bool:
        return name in self.__available_tags

    def get_tag(self, name: str) -> Tag:
        return self.__available_tags[name]

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
                str_strip_whitespace = True

        request_data = RequestData.model_validate(request.json)
        response_data = {}

        tag = self.__available_tags[name]
        tag.name = request_data.name_new
        tag.color = request_data.color
        tag.description = request_data.description
        tag.internal = request_data.internal
        self.app.db.update()

        if name != request_data.name_new:
            self.__available_tags[request_data.name_new] = self.__available_tags[name]
            del self.__available_tags[name]

        return response_data

    def delete(self, name: str) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            occurrences: list[str]

            class Config:
                str_strip_whitespace = True

        request_data = RequestData.model_validate(request.json)
        response_data = {}

        if name not in self.__available_tags:
            abort(404, f'No Tag with name: "{name}"')
        tag = self.__available_tags[name]
        for rid in request_data.occurrences:
            if rid == "":
                continue
            requirement = self.app.db.get_object("Requirement", rid)
            requirement.tags.pop(tag)
        self.app.db.update()

        current_app.db.remove_object(tag)
        self.__available_tags.pop(name)

        return response_data


register_api(api_blueprint, TagsApi)
