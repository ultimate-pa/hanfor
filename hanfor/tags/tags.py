from hanfor_flask import current_app
from flask import Blueprint, render_template, request
from flask_restx import Resource, Namespace
from dataclasses import asdict

from lib_core.data import Tag, Requirement
from lib_core.api_models import TagModel, TagListModel, TagRequestModel, ErrorMessageModel
from configuration.tags import STANDARD_TAGS

BUNDLE_JS = "dist/tags-bundle.js"
blueprint = Blueprint("tags", __name__, template_folder="templates", url_prefix="/tags")

api = Namespace("Tags", "Tag api Description", path="/tags", ordered=True)


@blueprint.route("", methods=["GET"])
def index():
    return render_template("tags/index.html", BUNDLE_JS=BUNDLE_JS)


@api.route("")
class ApiTags(Resource):
    @api.response(200, "Success", TagListModel)
    def get(self):
        """Get all Tags"""
        update_variables_used_by()
        tmp = current_app.db.get_objects(Tag)
        return [asdict(v) for v in tmp.values()], 200

    @api.expect(TagRequestModel)
    @api.response(200, "Success", TagModel)
    @api.response(400, "Bad Request", ErrorMessageModel)
    def post(self):
        """Create new Tag"""
        data = request.json
        if "name" not in data or "color" not in data or "description" not in data or "internal" in data:
            return {"error": "Bad Request", "message": "Malformed data"}, 400
        name = data["name"].strip()
        color = data["color"].strip()
        internal = bool(data["internal"])
        description = data["description"].strip()
        if name in [t.name for t in current_app.db.get_objects(Tag).values()]:
            return {"error": "Bad Request", "message": "Name exist already"}, 400
        tag = Tag(name, color, internal, description)
        current_app.db.add_object(tag)
        return asdict(tag), 200


@api.route("/<string:tag_id>")
class ApiTag(Resource):
    @api.response(200, "Success", TagModel)
    @api.response(404, "Not Found")
    def get(self, tag_id: str):
        """Get all Tags"""
        if current_app.db.key_in_table(Tag, tag_id):
            update_variables_used_by()
            return asdict(current_app.db.get_object(Tag, tag_id)), 200
        return None, 404

    @api.expect(TagRequestModel)
    @api.response(200, "Success", TagModel)
    @api.response(400, "Bad Request", ErrorMessageModel)
    @api.response(404, "Not Found")
    def put(self, tag_id: str):
        """Override Tag data"""
        if not current_app.db.key_in_table(Tag, tag_id):
            return None, 404
        tag = current_app.db.get_object(Tag, tag_id)
        data = request.json
        if "name" not in data or "color" not in data or "description" not in data or "internal" not in data:
            return {"error": "Bad Request", "message": "Malformed data"}, 400
        if tag.mutable:
            name = data["name"].strip()
        else:
            name = tag.name
        color = data["color"].strip()
        internal = bool(data["internal"])
        description = data["description"].strip()

        if name in [t.name for t in current_app.db.get_objects(Tag).values() if t.uuid != tag.uuid]:  # type: Tag
            return {"error": "Bad Request", "message": "Name exist already"}, 400
        tag.name = name
        tag.color = color
        tag.internal = internal
        tag.description = description
        current_app.db.update()
        return asdict(tag), 200

    @api.expect(TagRequestModel)
    @api.response(200, "Success", TagModel)
    @api.response(404, "Not Found")
    def patch(self, tag_id: str):
        """Update given fields of the Tag"""
        if not current_app.db.key_in_table(Tag, tag_id):
            return None, 404
        tag = current_app.db.get_object(Tag, tag_id)
        data = request.json
        if tag.mutable and "name" in data:
            tag.name = data["name"]
        if "color" in data:
            tag.color = data["color"]
        if "description" in data:
            tag.description = data["description"]
        if "internal" in data:
            tag.internal = data["internal"]
        current_app.db.update()
        return asdict(tag), 200

    @api.response(204, "Success")
    @api.response(403, "Forbidden")
    def delete(self, tag_id: str):
        """Delete Tag"""
        # ask if it should be deleted from all requirements
        if current_app.db.key_in_table(Tag, tag_id):
            tag = current_app.db.get_object(Tag, tag_id)
            if not tag.mutable:
                return None, 403
            for r in current_app.db.get_objects(Requirement).values():  # type: Requirement
                if tag in r.tags:
                    r.tags.pop(tag)
            current_app.db.update()
            current_app.db.remove_object(tag)
        return None, 204


@api.route("/add_standard")
class ApiAddStandardTags(Resource):
    @api.response(204, "Success")
    def post(self):
        """Add standard tags"""
        existing_tag_names: set[str] = {t.name for t in current_app.db.get_objects(Tag).values()}
        for name, properties in STANDARD_TAGS.items():
            if name not in existing_tag_names:
                existing_tag_names.add(name)
                current_app.db.add_object(
                    Tag(name, properties["color"], properties["internal"], properties["description"]), delay_update=True
                )
        current_app.db.update()
        return None, 204


def update_variables_used_by():
    for t in current_app.db.get_objects(Tag).values():  # type: Tag
        t.used_by.clear()
    for r in current_app.db.get_objects(Requirement).values():  # type: Requirement
        for t in r.tags.keys():
            t.used_by.append(r.rid)
