import os
from dataclasses import dataclass, field
from typing import Type

from flask import Blueprint, Response, current_app, jsonify, render_template, request
from flask.views import MethodView
from pydantic import BaseModel

from configuration.tags import STANDARD_TAGS
from defaults import Color
from reqtransformer import Requirement
from static_utils import get_filenames_from_dir
from utils import MetaSettings

BUNDLE_JS = 'dist/tags-bundle.js'
blueprint = Blueprint('tags', __name__, template_folder='templates', url_prefix='/tags')
api_blueprint = Blueprint('api_tags', __name__, url_prefix='/api/tags')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('tags/index.html', BUNDLE_JS=BUNDLE_JS)


@dataclass
class Tag:
    name: str
    color: str
    internal: bool
    description: str
    used_by: list = field(default_factory=list)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('tags_api')
    bp.add_url_rule('/', defaults={'name': None}, view_func=view, methods=['GET'])
    bp.add_url_rule('/<string:command>', view_func=view, methods=['POST'])
    bp.add_url_rule('/<string:name>', view_func=view, methods=['GET', 'PUT', 'PATCH', 'DELETE'])


class TagsApi(MethodView):
    INIT_TAGS = {
        'Type_inference_error': {'color': Color.BS_DANGER.value, 'internal': True, 'description': ''},
        'incomplete_formalization': {'color': Color.BS_WARNING.value, 'internal': True, 'description': ''},
        'has_formalization': {'color': Color.BS_SUCCESS.value, 'internal': True, 'description': ''},
        'unknown_type': {'color': Color.BS_DANGER.value, 'internal': True, 'description': ''}
    }

    def __init__(self):
        self.app = current_app
        self.meta_settings = MetaSettings(self.app.config['META_SETTINGS_PATH'])
        self.filenames = get_filenames_from_dir(self.app.config['REVISION_FOLDER'])
        self.__available_tags: dict[str, Tag] = {k: Tag(k, **v) for k, v in self.INIT_TAGS.items()}
        self.__load()

    def __load(self):
        for tag_name in self.meta_settings['tag_colors']:
            self.__available_tags[tag_name] = Tag(
                name=tag_name,
                color=self.meta_settings['tag_colors'][tag_name],
                description=self.meta_settings['tag_descriptions'][tag_name],
                internal=self.meta_settings['tag_internal'][tag_name])

        for filename in self.filenames:
            try:
                req = Requirement.load(filename)
            except TypeError:
                continue

            for tag_name in req.tags:
                self.add_if_new(tag_name)
                self.__available_tags[tag_name].used_by.append(req.rid)

        for tag in self.__available_tags.values():
            tag.used_by.sort()

    def __store(self):
        self.meta_settings['tag_colors'] = {t.name: t.color for _, t in self.__available_tags.items()}
        self.meta_settings['tag_internal'] = {t.name: t.internal for _, t in self.__available_tags.items()}
        self.meta_settings['tag_descriptions'] = {t.name: t.description for _, t in self.__available_tags.items()}
        self.meta_settings.update_storage()

    def add_if_new(self, tag_name: str) -> None:
        if tag_name not in self.__available_tags:
            self.add(tag_name)

    def add(self, tag_name: str, tag_color: str = Color.BS_INFO.value, tag_internal: bool = False,
            tag_description: str = '') -> None:
        self.__available_tags[tag_name] = Tag(tag_name, tag_color, tag_internal, tag_description)
        self.__store()

    def get(self, name: str | None) -> str | dict | tuple | Response:
        response_data = jsonify([tag for tag in self.__available_tags.values()])

        if name is not None:
            if name in self.__available_tags:
                # TODO this is not working when called by http request
                response_data = self.__available_tags[name]
            else:
                response_data = {}

        return response_data

    def post(self, command: str) -> str | dict | tuple | Response:
        response_data = {}

        match command:
            case 'add_standard':
                for name, properties in STANDARD_TAGS.items():
                    self.add(name, properties["color"], properties["internal"], properties["description"])
            case _:
                raise ValueError(f'Unknown command `{command}`.')

        return response_data

    def put(self, name: str) -> str | dict | tuple | Response:
        raise NotImplementedError

    def patch(self, name: str) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            name_new: str = ''
            occurrences: list[str] = []
            color: str = Color.BS_INFO.value
            description: str = ''
            internal: bool = False

            class Config:
                anystr_strip_whitespace = True

        request_data = RequestData.parse_obj(request.json)
        response_data = {}

        for rid in request_data.occurrences:
            filepath = os.path.join(self.app.config['REVISION_FOLDER'], f'{rid}.pickle')
            if os.path.exists(filepath) and os.path.isfile(filepath):
                requirement = Requirement.load(filepath)
                comment = requirement.tags.pop(name)
                requirement.tags[request_data.name_new] = comment
                requirement.store()

        self.__available_tags.pop(name)
        self.add(request_data.name_new, request_data.color, request_data.internal, request_data.description)

        return response_data

    def delete(self, name: str) -> str | dict | tuple | Response:
        class RequestData(BaseModel):
            occurrences: list[str]

            class Config:
                anystr_strip_whitespace = True

        request_data = RequestData.parse_obj(request.json)
        response_data = {}

        for rid in request_data.occurrences:
            filepath = os.path.join(self.app.config['REVISION_FOLDER'], f'{rid}.pickle')
            if os.path.exists(filepath) and os.path.isfile(filepath):
                requirement = Requirement.load(filepath)
                requirement.tags.pop(name)
                requirement.store()

        self.__available_tags.pop(name)
        self.__store()

        return response_data


register_api(api_blueprint, TagsApi)
