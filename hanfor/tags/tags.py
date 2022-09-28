import logging
import os
from dataclasses import dataclass, field
from typing import Type

from flask import Blueprint, render_template, request, jsonify, Response, current_app, make_response
from flask.views import MethodView
from flask_pydantic import validate
from pydantic import BaseModel

import defaults
from configuration.tags import STANDARD_TAGS
from reqtransformer import Requirement
from static_utils import get_filenames_from_dir
from utils import MetaSettings

BUNDLE_JS = 'dist/tags-bundle.js'
blueprint = Blueprint('tags', __name__, template_folder='templates', url_prefix='/tags')
api_blueprint = Blueprint('api_tags', __name__, url_prefix='/api/tags')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('tags/tags.html', BUNDLE_JS=BUNDLE_JS)


class RequestData(BaseModel):
    id: int
    data: str


@dataclass
class Tag:
    name: str
    color: str
    internal: bool
    description: str
    used_by: list = field(default_factory=list)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('tags_api')
    bp.add_url_rule('/', defaults={'tag_name': None}, view_func=view, methods=['GET'])
    bp.add_url_rule('/<string:command>', view_func=view, methods=['POST'])
    bp.add_url_rule('/<string:tag_name>', view_func=view, methods=['GET', 'PUT', 'PATCH', 'DELETE'])


class TagsApi(MethodView):
    def __init__(self):
        self.app = current_app
        self.meta_settings = MetaSettings(self.app.config['META_SETTINGS_PATH'])
        self.filenames = get_filenames_from_dir(self.app.config['REVISION_FOLDER'])
        self._available_tags: dict[str, Tag] = self.__initial_tags()
        self.__load()
        self.sort_used_by_field()

    def __initial_tags(self) -> dict[str, Tag]:
        tags = [Tag('Type_inference_error', defaults.Color.BS_DANGER.value, True, ""),
                Tag('incomplete_formalization', defaults.Color.BS_WARNING.value, True, ""),
                Tag('has_formalization', defaults.Color.BS_SUCCESS.value, True, ""),
                Tag('unknown_type', defaults.Color.BS_DANGER.value, True, "")]
        return {v.name: v for v in tags}

    def sort_used_by_field(self):
        for tag in self._available_tags.keys():
            self._available_tags.get(tag).used_by.sort()

    def _get(self, tag_name):
        if tag_name not in self._available_tags:
            self.add(tag_name)
        return self._available_tags[tag_name]

    def add_if_new(self, tag_name: str):
        if tag_name not in self._available_tags:
            self.add(tag_name)

    def add(self, tag_name: str, tag_color: str = defaults.Color.BS_INFO.value, tag_internal: bool = False, tag_description: str = ""):
        self._available_tags[tag_name] = Tag(tag_name, tag_color, tag_internal, tag_description)
        self.__store()

    def __store(self):
        self.meta_settings['tag_colors'] = {t.name: t.color for _, t in self._available_tags.items()}
        self.meta_settings['tag_internal'] = {t.name: t.internal for _, t in self._available_tags.items()}
        self.meta_settings['tag_descriptions'] = {t.name: t.description for _, t in self._available_tags.items()}
        self.meta_settings.update_storage()

    def __load(self):
        for tag, color in self.meta_settings["tag_colors"].items():
            self._available_tags[tag] = Tag(name=tag, color=color, description=self.meta_settings["tag_descriptions"][tag],
                                            internal=self.meta_settings["tag_internal"][tag])
        for filename in self.filenames:
            try:
                req = Requirement.load(filename)
            except TypeError:
                continue
            for tag in req.tags:
                self._get(tag).used_by.append(req.rid)

    def get(self, tag_name):
        return jsonify([tag for tag in self._available_tags.values()])

    def post(self, command):
        response = {}

        if request.view_args['command'] == 'update':
            tag_name = request.form.get('name', '').strip()
            tag_name_old = request.form.get('name_old', '').strip()
            occurences = request.form.get('occurences', '').strip().split(',')
            color = request.form.get('color', defaults.Color.BS_INFO.value).strip()
            description = request.form.get('description', '').strip()
            internal = request.form.get('internal', False) == "true"

            if tag_name != tag_name_old:
                logging.info(f'Update Tag `{tag_name_old}` to new name `{tag_name}`')
                # TODO: Check if this is needed.
                response['has_changes'] = True

            if len(occurences) > 0:
                # Todo: only rebuild if we have a merge.
                response['rebuild_table'] = True
                for rid in occurences:
                    filepath = os.path.join(self.app.config['REVISION_FOLDER'], f'{rid}.pickle')
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        requirement = Requirement.load(filepath)
                        logging.info(f'Update tags in requirement `{requirement.rid}`')
                        comment = requirement.tags.pop(tag_name_old)
                        requirement.tags[tag_name] = comment
                        requirement.store()

            self.add(tag_name, color, internal, description)

            response['data'] = {
                'name': tag_name,
                'used_by': occurences,
                'color': color,
                'description': description,
                'internal': internal
            }

            return response

    def delete(self, tag_name):
        response = {}

        tag_name = request.form.get('name', '').strip()
        occurences = request.form.get('occurences', '').strip().split(',')
        logging.info(f'Delete Tag `{tag_name}`')
        response['has_changes'] = True

        if len(occurences) > 0:
            response['rebuild_table'] = True
            for rid in occurences:
                filepath = os.path.join(self.app.config['REVISION_FOLDER'], f'{rid}.pickle')
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    requirement = Requirement.load(filepath)
                    logging.info(f'Delete tag `{tag_name}` in requirement `{requirement.rid}`')
                    requirement.tags.pop(tag_name)
                    requirement.store()
        self._available_tags.pop(tag_name)
        self.__store()

        return response

    def add_standard_tags(self):
        response = {}

        logging.info(f'Adding standard Tags...')
        for name, properties in STANDARD_TAGS.items():
            self.add(name, properties["color"], properties["internal"], properties["description"])
        response['has_changes'] = True
        return response


    #def get(self, id: int) -> str | dict | tuple | Response:
    #    return f'HTTP GET for id `{id}` received.'

    #def post(self) -> str | dict | tuple | Response:
    #    data = RequestData.parse_obj(request.form)
    #    return f'HTTP POST received.'

    #def put(self, id: int) -> str | dict | tuple | Response:
    #    return f'HTTP PUT for id `{id}` received.'

    #def patch(self, id: int) -> str | dict | tuple | Response:
    #    return f'HTTP PATCH for id `{id}` received.'

    #def delete(self, id: int) -> str | dict | tuple | Response:
    #    return f'HTTP DELETE for id `{id}` received.'


register_api(api_blueprint, TagsApi)