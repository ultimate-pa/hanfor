import logging
import os

from reqtransformer import Requirement
from ressources import Ressource
from static_utils import get_filenames_from_dir


class Tag(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)
        self.filenames = get_filenames_from_dir(self.app.config['REVISION_FOLDER'])
        self._available_tags = dict()
        self.load_available_tags()
        self.sort_used_by_field()

    def load_available_tags(self):
        for filename in self.filenames:
            try:
                req = Requirement.load(filename)
            except TypeError:
                continue
            for tag in req.tags:
                if len(tag) == 0:
                    continue
                if tag not in self._available_tags.keys():
                    self._available_tags[tag] = {
                        'name': tag,
                        'used_by': list(),
                        'color': self.get_tag_color(tag),
                        'description': self.get_tag_desc(tag)
                    }
                self._available_tags[tag]['used_by'].append(req.rid)

    def sort_used_by_field(self):
        for tag in self._available_tags.keys():
            self._available_tags[tag]['used_by'].sort()

    def get_tag_color(self, tag_name):
        col = '#5bc0de'
        try:
            col = self.meta_settings['tag_colors'][tag_name]
        except KeyError:
            pass
        return col

    def get_tag_desc(self, tag_name):
        desc = ''
        try:
            desc = self.meta_settings['tag_descriptions'][tag_name]
        except KeyError:
            pass
        return desc

    @property
    def available_tags(self):
        return self._available_tags

    def GET(self):
        """ Fetch a list of all available reports.
        """
        self.response.data = [tag for tag in self.available_tags.values()]

    def POST(self):
        if self.request.view_args['command'] == 'update':
            tag_name = self.request.form.get('name', '').strip()
            tag_name_old = self.request.form.get('name_old', '').strip()
            occurences = self.request.form.get('occurences', '').strip().split(',')
            color = self.request.form.get('color', '#5bc0de').strip()  # Default = #5bc0de
            description = self.request.form.get('description', '').strip()

            if tag_name != tag_name_old:
                logging.info('Update Tag `{}` to new name `{}`'.format(tag_name_old, tag_name))
                self.response['has_changes'] = True

            if len(occurences) > 0:
                # Todo: only rebuild if we have a merge.
                self.response['rebuild_table'] = True
                for rid in occurences:
                    filepath = os.path.join(self.app.config['REVISION_FOLDER'], '{}.pickle'.format(rid))
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        requirement = Requirement.load(filepath)
                        logging.info('Update tags in requirement `{}`'.format(requirement.rid))
                        comment = requirement.tags.pop(tag_name_old)
                        requirement.tags[tag_name] = comment
                        requirement.store()

            # Store the color into meta settings.
            if 'tag_colors' not in self.meta_settings:
                self.meta_settings['tag_colors'] = dict()
            self.meta_settings['tag_colors'][tag_name] = color

            # Store the tag description into meta settings.
            if 'tag_descriptions' not in self.meta_settings:
                self.meta_settings['tag_descriptions'] = dict()
            self.meta_settings['tag_descriptions'][tag_name] = description
            self.meta_settings.update_storage()
            self.response.data = {
                'name': tag_name,
                'used_by': occurences,
                'color': color,
                'description': description
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
