from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.tag_mapper.tag_mapper import TagMapperAddon
from hanfor_flask import current_app

tag_mapper_api_namespace = Namespace(
    "AI Addon: Tag Mapper", "Assign tags to requirements via AI prompts", path="/tag-mapper", ordered=True
)

_handle_disabled = AiAddonAbstractClass.handle_disabled(tag_mapper_api_namespace)


def _get_addon() -> TagMapperAddon:
    return current_app.ai_addons.get_addon("tag_mapper", TagMapperAddon)


@tag_mapper_api_namespace.route("/mappings")
class ApiTagMapperMappings(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.OK, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        """List all mappings."""
        return _get_addon().get_mappings(), HTTPStatus.OK

    @tag_mapper_api_namespace.response(HTTPStatus.OK, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        """Add a new (empty) mapping - used by the 'Add Mapping' button."""
        payload = request.get_json(force=True, silent=True) or {}
        mapping = _get_addon().add_mapping(tag=payload.get("tag", ""), prompt=payload.get("prompt", ""))
        return mapping, HTTPStatus.OK


@tag_mapper_api_namespace.route("/mappings/<int:mapping_id>")
class ApiTagMapperMapping(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def delete(self, mapping_id: int):
        _get_addon().delete_mapping(mapping_id)
        return None, HTTPStatus.NO_CONTENT


@tag_mapper_api_namespace.route("/mappings/<int:mapping_id>/update")
class ApiTagMapperMappingUpdate(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.OK, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self, mapping_id: int):
        """Sync a single row's current tag/prompt before running it."""
        payload = request.get_json(force=True, silent=True) or {}
        mapping = _get_addon().update_mapping(mapping_id, payload.get("tag", ""), payload.get("prompt", ""))
        if mapping is None:
            return {"message": "Mapping not found"}, HTTPStatus.NOT_FOUND
        return mapping, HTTPStatus.OK


@tag_mapper_api_namespace.route("/save")
class ApiTagMapperSave(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        """Write the current in-memory mappings to configuration/tag_mapper_config.py."""
        _get_addon().save_configuration()
        return None, HTTPStatus.NO_CONTENT


@tag_mapper_api_namespace.route("/run/<int:mapping_id>")
class ApiTagMapperRun(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self, mapping_id: int):
        _get_addon().run_mapping(mapping_id)
        return None, HTTPStatus.NO_CONTENT


@tag_mapper_api_namespace.route("/run-all")
class ApiTagMapperRunAll(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        _get_addon().run_all()
        return None, HTTPStatus.NO_CONTENT


@tag_mapper_api_namespace.route("/selection")
class ApiTagMapperSelection(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.OK, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        return _get_addon().get_selected_provider_model(), HTTPStatus.OK

    @tag_mapper_api_namespace.response(HTTPStatus.OK, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        payload = request.get_json(force=True, silent=True) or {}
        selection = _get_addon().set_selected_provider_model(payload.get("provider"), payload.get("model"))
        return selection, HTTPStatus.OK


@tag_mapper_api_namespace.route("/tags")
class ApiTagMapperTags(Resource):
    @tag_mapper_api_namespace.response(HTTPStatus.OK, "Success")
    @tag_mapper_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        payload = request.get_json(force=True, silent=True) or {}
        result = _get_addon().create_tag(payload.get("name", "").strip())
        return result, HTTPStatus.OK
