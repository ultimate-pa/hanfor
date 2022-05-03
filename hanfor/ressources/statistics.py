import itertools
import random
from collections import defaultdict

from reqtransformer import Requirement, VariableCollection
from ressources import Ressource
from static_utils import get_filenames_from_dir


class Statistics(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)
        self.filenames = get_filenames_from_dir(self.app.config['REVISION_FOLDER'])

    def fetch_statistics(self):
        data = {
            'done': 0,
            'review': 0,
            'todo': 0,
            'total': 0,
            'types': dict(),
            'type_names': list(),
            'type_counts': list(),
            'type_colors': list(),
            'top_variable_names': list(),
            'top_variables_counts': list(),
            'top_variable_colors': list(),
            'variable_graph': list(),
            'tags_per_type': dict(),
            'status_per_type': dict()
        }
        for requirement_filename in self.filenames:
            try:
                requirement = Requirement.load(requirement_filename)
            except TypeError:
                continue
            if hasattr(requirement, 'type_in_csv'):
                data['total'] += 1
                if requirement.status == 'Todo':
                    data['todo'] += 1
                elif requirement.status == 'Review':
                    data['review'] += 1
                elif requirement.status == 'Done':
                    data['done'] += 1
                if requirement.type_in_csv in data['types']:
                    data['types'][requirement.type_in_csv] += 1
                else:
                    data['types'][requirement.type_in_csv] = 1
                    data['tags_per_type'][requirement.type_in_csv] = dict()
                    data['status_per_type'][requirement.type_in_csv] = {'Todo': 0, 'Review': 0, 'Done': 0}
                for tag in requirement.tags:
                    if len(tag) > 0:
                        if tag not in data['tags_per_type'][requirement.type_in_csv]:
                            data['tags_per_type'][requirement.type_in_csv][tag] = 0
                        data['tags_per_type'][requirement.type_in_csv][tag] += 1
                data['status_per_type'][requirement.type_in_csv][requirement.status] += 1

        for name, count in data['types'].items():
            data['type_names'].append(name)
            data['type_counts'].append(count)
            data['type_colors'].append("#%06x" % random.randint(0, 0xFFFFFF))

        # Gather most used variables.
        var_collection = VariableCollection.load(self.app.config['SESSION_VARIABLE_COLLECTION'])
        var_usage = []

        var_nodes = dict()
        req_nodes = set()

        for name, used_by in var_collection.var_req_mapping.items():
            var_nodes[name] = "#%06x" % random.randint(0, 0xFFFFFF)
            for req in used_by: req_nodes.add(req)

        for var, color in var_nodes.items():
            data['variable_graph'].append({'data': {'id': var, 'size': 10, 'color': color}})
        for req in req_nodes:
            data['variable_graph'].append({'data': {'id': req, 'size': 20, 'color': '#000000'}})

        for var, used_by in var_collection.var_req_mapping.items():
            for user in used_by:
                data['variable_graph'].append(
                    {
                        'data': {'id': var + "_" + user, 'source': var, 'target': user,
                                  "color": var_nodes[var]}
                    }
                )

        # most used variables
        for count, name in var_usage:
            data['top_variable_names'].append(name)
            data['top_variables_counts'].append(count)
            data['top_variable_colors'].append("#%06x" % random.randint(0, 0xFFFFFF))

        self.response.data = data

    def GET(self):
        self.fetch_statistics()

    def POST(self):
        raise NotImplementedError

    def DELETE(self):
        raise NotImplementedError
