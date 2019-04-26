import itertools
import random

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
        for name, used_by in var_collection.var_req_mapping.items():
            var_usage.append((len(used_by), name))

        var_usage.sort(reverse=True)

        # Create the variable graph
        # Limit the ammount of data.
        if len(var_usage) > 100:
            var_usage = var_usage[:100]
        # First create the edges data.
        edges = dict()
        available_names = [v[1] for v in var_usage]
        for co_occuring_vars in var_collection.req_var_mapping.values():
            name_combinations = itertools.combinations(co_occuring_vars, 2)
            for name_combination in name_combinations:
                name = '_'.join(name_combination)
                if name_combination[0] in available_names and name_combination[1] in available_names:
                    if name not in edges:
                        edges[name] = {'source': name_combination[0], 'target': name_combination[1], 'weight': 0}
                    edges[name]['weight'] += 1

        for count, name in var_usage:
            if count > 0:
                data['variable_graph'].append(
                    {
                        'data': {
                            'id': name,
                            'size': count
                        }

                    }
                )

        for edge, values in edges.items():
            data['variable_graph'].append(
                {
                    'data': {'id': edge, 'source': values['source'], 'target': values['target']}
                }
            )

        if len(var_usage) > 10:
            var_usage = var_usage[:10]

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
