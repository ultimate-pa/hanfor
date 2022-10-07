import math
import random
from collections import defaultdict
from typing import Type

from flask import Blueprint, render_template, Response, current_app
from flask.views import MethodView

from reqtransformer import Requirement, VariableCollection
from static_utils import get_filenames_from_dir

BUNDLE_JS = 'dist/statistics-bundle.js'
blueprint = Blueprint('statistics', __name__, template_folder='templates', url_prefix='/statistics')
api_blueprint = Blueprint('api_statistics', __name__, url_prefix='/api/statistics')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('statistics/index.html', BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('statistics_api')
    bp.add_url_rule('/', view_func=view, methods=['GET'])


class StatisticsApi(MethodView):
    def __init__(self):
        self.app = current_app
        self.filenames = get_filenames_from_dir(self.app.config['REVISION_FOLDER'])

    def get(self) -> str | dict | tuple | Response:
        return self.fetch_statistics()

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
        var_nodes_weight = defaultdict(int)
        req_nodes = set()

        for name, used_by in var_collection.var_req_mapping.items():
            if var_collection.get_type(name) == "CONST": continue
            var_nodes[name] = "#%06x" % random.randint(0, 0xFFFFFF)
            var_nodes_weight[name] += len(used_by)
            for req in used_by: req_nodes.add(req)

        # limit the percentage of connections of a variable to something meaningful (e.g. < 40%)
        var_clutter_cutoff = .4 * len(req_nodes)
        reqnum = len(req_nodes)

        for var, color in var_nodes.items():
            node_size = 10 + (290 * (var_nodes_weight[var] / len(req_nodes)))
            data['variable_graph'].append({'data': {'id': var, 'size': int(node_size), 'color': color,
                                                    "calculatedrepulsion": 100 + (((
                                                            var_nodes_weight[var] / var_clutter_cutoff)) * 7000)}})
        for req in req_nodes:
            data['variable_graph'].append({'data': {'id': req, 'size': 20, 'color': '#000000',
                                                    "calculatedrepulsion": "1000"}})

        for var, used_by in var_collection.var_req_mapping.items():
            if var_collection.get_type(var) == "CONST": continue
            if var_nodes_weight[var] > var_clutter_cutoff: continue
            for user in used_by:
                data['variable_graph'].append(
                    {
                        'data': {'id': var + "_" + user, 'source': var, 'target': user,
                                 "color": var_nodes[var],
                                 # space nodes further away from crowded nodes; give more space if more nodes are there
                                 "calculatedlength": 100 + (
                                         ((var_nodes_weight[var] / var_clutter_cutoff)) * reqnum * 10),
                                 # if we are at a crowded node, allow more jiggeling
                                 "calculatedelasticity": math.log(
                                     ((var_nodes_weight[var] / var_clutter_cutoff)) * reqnum)}
                    }
                )

        # most used variables
        for count, name in var_usage:
            data['top_variable_names'].append(name)
            data['top_variables_counts'].append(count)
            data['top_variable_colors'].append("#%06x" % random.randint(0, 0xFFFFFF))

        return data


register_api(api_blueprint, StatisticsApi)
