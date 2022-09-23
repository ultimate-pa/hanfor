import logging
import os
from dataclasses import dataclass, field

import defaults
from defaults import Color
from reqtransformer import Requirement
from ressources import Ressource
from static_utils import get_filenames_from_dir
from configuration.tags import STANDARD_TAGS

@dataclass
class Tag:

    name: str
    color: str
    internal: bool
    description: str
    used_by: list = field(default_factory=list)


class Tags(Ressource):

    def __init__(self, app, request):
        super().__init__(app, request)
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

    def get(self, tag_name):
        if tag_name not in self._available_tags:
            self.add(tag_name)
        return self._available_tags[tag_name]

    def add_if_new(self, tag_name: str):
        if tag_name not in self._available_tags:
            self.add(tag_name)

    def add(self, tag_name: str, tag_color: str = Color.BS_INFO.value, tag_internal: bool = False, tag_description: str = ""):
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
                self.get(tag).used_by.append(req.rid)

    def GET(self):
        self.response.data = [tag for tag in self._available_tags.values()]

    def POST(self):
        if self.request.view_args['command'] == 'update':
            tag_name = self.request.form.get('name', '').strip()
            tag_name_old = self.request.form.get('name_old', '').strip()
            occurences = self.request.form.get('occurences', '').strip().split(',')
            color = self.request.form.get('color', Color.BS_INFO.value).strip()
            description = self.request.form.get('description', '').strip()
            internal = self.request.form.get('internal', False) == "true"

            if tag_name != tag_name_old:
                logging.info(f'Update Tag `{tag_name_old}` to new name `{tag_name}`')
                self.response['has_changes'] = True

            if len(occurences) > 0:
                # Todo: only rebuild if we have a merge.
                self.response['rebuild_table'] = True
                for rid in occurences:
                    filepath = os.path.join(self.app.config['REVISION_FOLDER'], f'{rid}.pickle')
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        requirement = Requirement.load(filepath)
                        logging.info(f'Update tags in requirement `{requirement.rid}`')
                        comment = requirement.tags.pop(tag_name_old)
                        requirement.tags[tag_name] = comment
                        requirement.store()

            self.add(tag_name, color, internal, description)

            self.response.data = {
                'name': tag_name,
                'used_by': occurences,
                'color': color,
                'description': description,
                'internal': internal
            }

    def DELETE(self):
        tag_name = self.request.form.get('name', '').strip()
        occurences = self.request.form.get('occurences', '').strip().split(',')
        logging.info(f'Delete Tag `{tag_name}`')
        self.response['has_changes'] = True

        if len(occurences) > 0:
            self.response['rebuild_table'] = True
            for rid in occurences:
                filepath = os.path.join(self.app.config['REVISION_FOLDER'], f'{rid}.pickle')
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    requirement = Requirement.load(filepath)
                    logging.info(f'Delete tag `{tag_name}` in requirement `{requirement.rid}`')
                    requirement.tags.pop(tag_name)
                    requirement.store()
        self._available_tags.pop(tag_name)
        self.__store()

    def add_standard_tags(self):
        logging.info(f'Adding standard Tags...')
        for name, properties in STANDARD_TAGS.items():
            self.add(name, properties["color"], properties["internal"], properties["description"])
        self.response['has_changes'] = True
        return self.response
