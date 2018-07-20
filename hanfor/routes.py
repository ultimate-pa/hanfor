import datetime
from functools import wraps, update_wrapper

from flask import render_template, make_response, current_app

from hanfor import db
from hanfor.models import Variable, Expression


def nocache(view):
    """ Decorator for a flask view. If applied this will prevent caching.

    """
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@app.route('/dododod')
def dododod():
    vars = Variable.query.all()
    result = '\n'.join([str(var) + '</br>' for var in vars])
    result += '<br>'
    expressions = Expression.query.all()
    result += '\n'.join([str(exp) + '</br>' for exp in expressions])
    for expression in expressions:
        result += '<br>Expr: {} with vars: {} => {}'.format(
            expression.string,
            [var.name for var in expression.variables],
            expression
        )
    return result


@app.route('/add_expression/<string>')
def add_expression(string):
    exp = Expression(string).parse_expression()
    result = 'okay'
    return result


@app.route('/api/tools/<command>', methods=['GET', 'POST'])
@nocache
def tools_api(command):
    filter_list = request.form.get('selected_requirement_ids', '')
    if len(filter_list) > 0:
        filter_list = json.loads(filter_list)
    else:
        filter_list = None

    if command == 'req_file':
        filename = utils.generate_req_file(app, filter_list=filter_list)

        response = make_response(send_file(filename))
        basename = os.path.basename(filename)
        response.headers["Content-Disposition"] = \
            "attachment;" \
            "filename*=UTF-8''{utf_filename}".format(
                utf_filename=basename
            )
        os.remove(filename)
        return response

    if command == 'csv_file':
        filename = utils.generate_csv_file(app, filter_list=filter_list)

        response = make_response(send_file(filename))
        basename = os.path.basename(filename)
        response.headers["Content-Disposition"] = \
            "attachment;" \
            "filename*=UTF-8''{utf_filename}".format(
                utf_filename=basename
            )
        os.remove(filename)
        return response


@app.route('/<site>')
def site(site):
    available_sites = [
        'autocomplete',
        'help',
        'statistics',
        'variables',
        'tags'
    ]
    if site in available_sites:
            return render_template('{}.html'.format(site))
    else:
        return render_template('404.html'), 404


@app.route('/')
def index():
    query = dict()
    default_cols = [
        {'name': 'Pos', 'target': 1},
        {'name': 'Id', 'target': 2},
        {'name': 'Description', 'target': 3},
        {'name': 'Type', 'target': 4},
        {'name': 'Tags', 'target': 5},
        {'name': 'Status', 'target': 6},
        {'name': 'Formalization', 'target': 7}
    ]
    additional_cols = {'col_defs': list()}
    return render_template('index.html', query=query, additional_cols=additional_cols, default_cols=default_cols)
