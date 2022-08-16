import logging
import os

from defaults import Color
from reqtransformer import Requirement
from ressources import Ressource
from static_utils import get_filenames_from_dir
from configuration.tags import STANDARD_TAGS


class Tags(Ressource):

    def __init__(self, app, request):
        super().__init__(app, request)
        self.filenames = get_filenames_from_dir(self.app.config['REVISION_FOLDER'])
        self._available_tags = dict()
        self.load_available_tags()
        self.sort_used_by_field()

    def load_available_tags(self):
        for tag, color in self.meta_settings["tag_colors"].items():
            self._available_tags[tag] = {
                'name': tag,
                'used_by': list(),
                'color': color,
                'description': self.meta_settings["tag_descriptions"][tag],
                'internal': self.meta_settings["tag_internal"][tag]
            }
        for filename in self.filenames:
            try:
                req = Requirement.load(filename)
            except TypeError:
                continue
            for tag in req.tags:
                self._available_tags[tag]['used_by'].append(req.rid)

    def sort_used_by_field(self):
        for tag in self._available_tags.keys():
            self._available_tags[tag]['used_by'].sort()

    def __get_metaconfig_property(self, key: str, tag_name: str, default):
        if tag_name in self.meta_settings[key]:
            return self.meta_settings[key][tag_name]
        return default

    def add(self, tag_name: str, tag_color: str = Color.BS_INFO.value, tag_internal: bool = False, tag_description: str = ""):
        if tag_name not in self._available_tags:
            self.meta_settings['tag_colors'][tag_name] = tag_color
            self.meta_settings['tag_descriptions'][tag_name] = tag_description
            self.meta_settings['tag_internal'][tag_name] = tag_internal
            self.meta_settings.update_storage()

    @property
    def available_tags(self):
        return self._available_tags

    def GET(self):
        self.response.data = [tag for tag in self.available_tags.values()]

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
        self.meta_settings["tag_colors"].pop(tag_name)
        self.meta_settings.update_storage()

    def add_standard_tags(self):
        logging.info(f'Adding standard Tags...')
        for name, properties in STANDARD_TAGS.items():
            self.add(name, properties["color"], properties["internal"], properties["description"])
        self.response['has_changes'] = True
        return self.response
