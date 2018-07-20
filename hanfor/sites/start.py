from flask import jsonify, g, render_template, request
from hanfor import db
from hanfor.sites import bp
from hanfor.utils.nocache_decorator import nocache


@bp.route('/', methods=['GET'])
def start():
    query = {
        'command': request.args.get('command', 'default'),
        'q': request.args.get('q', ''),
        'col': request.args.get('col', '')
    }
    default_cols = [
        {'name': 'Pos', 'target': 1},
        {'name': 'Id', 'target': 2},
        {'name': 'Description', 'target': 3},
        {'name': 'Type', 'target': 4},
        {'name': 'Tags', 'target': 5},
        {'name': 'Status', 'target': 6},
        {'name': 'Formalization', 'target': 7}
    ]
    # @TODO: additional col defs
    # additional_cols = utils.get_datatable_additional_cols(app)['col_defs']
    additional_cols = []
    return render_template('index.html', query=query, additional_cols=additional_cols, default_cols=default_cols)
