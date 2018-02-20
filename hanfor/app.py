""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import sys

import boogie_parsing
import datetime
import logging
import os
import utils

from flask import Flask, render_template, request, jsonify, url_for, make_response, send_file, json
from flask_debugtoolbar import DebugToolbarExtension
from flask_restful import reqparse, abort, Api, Resource
from functools import wraps, update_wrapper
import reqtransformer
from reqtransformer import RequirementCollection, Requirement, VariableCollection, Formalization, Variable, Scope, \
    ScopedPattern, Pattern

# Create the app
app = Flask(__name__)
app.config.from_object('config')
api = Api(app)
app.wsgi_app = utils.PrefixMiddleware(app.wsgi_app, prefix=app.config['URL_PREFIX'])
HERE = os.path.dirname(os.path.realpath(__file__))
boogie_parser = boogie_parsing.get_parser_instance()


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


@app.route('/api/<resource>/<command>', methods=['GET', 'POST'])
@nocache
def api(resource, command):
    resources = [
        'req',
        'var',
        'stats'
    ]
    commands = [
        'get',
        'gets',
        'set',
        'update',
        'delete',
        'predict_pattern',
        'new_formalization'
    ]
    if resource not in resources or command not in commands:
        return jsonify({'msg': 'sorry, request not supported.'}), 400

    if resource == 'req':
        # Get a single requirement.
        if command == 'get' and request.method == 'GET':
            id = request.args.get('id', '')
            requirement = utils.load_requirement_by_id(id, app)
            var_collection = utils.pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])  # type:
            # VariableCollection
            result = requirement.to_dict()
            result['formalizations_html'] = utils.formalizations_to_html(app, requirement.formalizations)
            result['available_vars'] = var_collection.get_available_vars_list()
            if requirement:
                return jsonify(result)

        # Get all requirements
        if command == 'gets':
            filenames = utils.get_filenames_from_dir(app.config['SESSION_FOLDER'])
            result = dict()
            result['data'] = list()
            for filename in filenames:
                req = utils.pickle_load_from_dump(filename)  # type: Requirement
                if type(req) is Requirement:
                    result['data'].append(req.to_dict())
            return jsonify(result)

        # Update a requirement
        if command == 'update' and request.method == 'POST':
            id = request.form.get('id', '')
            requirement = utils.load_requirement_by_id(id, app)  # type: Requirement
            error = False
            error_msg = ''

            if requirement:
                logging.debug('Updating requirement: {}'.format(requirement.rid))
                requirement.status = request.form.get('status', '')
                logging.debug('Requirement status set to `{}`'.format(requirement.status))
                requirement.tags = set(t.strip() for t in request.form.get('tags', '').split(','))
                logging.debug('Requirement tags set to `{}`'.format(requirement.tags))

                # Update formalization.
                if request.form.get('update_formalization') == 'true':
                    formalizations = json.loads(request.form.get('formalizations', ''))
                    logging.debug('Updated Formalizations: {}'.format(formalizations))
                    try:
                        requirement.update_formalizations(formalizations, app)
                    except KeyError as e:
                        error = True
                        error_msg = 'Could not set formalization: Missing expression/variable for {}'.format(e)
                else:
                    logging.debug('Skipping formalization update.')

                if error:
                    logging.error('We got an error parsing the expressions: {}. Omitting requirement update.'.format(
                        error_msg))
                    return jsonify({
                        'success': False,
                        'errormsg': error_msg
                    })
                else:
                    utils.store_requirement(requirement, app)
                    return jsonify(requirement.to_dict()), 200

        # Predict the scoped Pattern of a requirement
        # TODO: Learn by considering the formalized. Improve data munging.
        if command == 'predict_pattern' and request.method == 'POST':
            id = request.form.get('id', '')
            reset = request.form.get('reset', '')
            requirement = utils.load_requirement_by_id(id, app)
            result = requirement.to_dict()
            predicted_options = utils.predict_scoped_pattern_to_options(requirement, reset)
            result['scopes'] = predicted_options['scopes']
            result['patterns'] = predicted_options['patterns']
            if requirement:
                return jsonify(result)

        # Add a new empty formalization
        if command == 'new_formalization' and request.method == 'POST':
            id = request.form.get('id', '')
            requirement = utils.load_requirement_by_id(id, app)  # type: Requirement
            formalization_id, formalization = requirement.add_empty_formalization()
            utils.store_requirement(requirement, app)
            result = utils.get_formalization_template(
                app.config['TEMPLATES_FOLDER'],
                requirement,
                formalization_id,
                formalization
            )
            return jsonify(result)

    if resource == 'var':
        # Get available variables
        if command == 'gets':
            return jsonify({'data': utils.get_available_vars(app, parser=boogie_parser, full=True)})
        if command == 'update':
            result = utils.update_variable_in_collection(app, request)

            return jsonify(result)

    if resource == 'stats':
        # Get all stats
        if command == 'gets':
            data = utils.get_statistics(app)
            return jsonify(data)

    return jsonify({'msg': 'sorry, could not parse your request.'}), 400


@app.route('/<site>')
def site(site):
    available_sites = [
        'help',
        'statistics',
        'variables',
        'tools'
    ]
    if site in available_sites:
        return render_template('{}.html'.format(site))
    else:
        return render_template('404.html'), 404


@app.route('/')
def index():
    query = {
        'command': request.args.get('command', 'default'),
        'q': request.args.get('q', ''),
        'col': request.args.get('col', '')
    }
    return render_template('index.html', query=query)


def varcollection_consistency_check(app):
    logging.info('Check varcollection consistency.')
    try:
        var_collection = utils.pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    except ModuleNotFoundError:
        # The "old" var_collection before the refactoring.
        sys.modules['reqtransformer.reqtransformer'] = reqtransformer
        sys.modules['reqtransformer.patterns'] = reqtransformer

        var_collection = utils.pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
        vars_to_collection = list()
        for name, var in var_collection.items():
            vars_to_collection.append({'name': name, 'type': var.type, 'value': var.value})
        del sys.modules['reqtransformer.reqtransformer']
        del sys.modules['reqtransformer.patterns']

        new_var_collection = VariableCollection()
        for var in vars_to_collection:
            new_var_collection.collection[var['name']] = Variable(var['name'], var['type'], var['value'])
        new_var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
        logging.info('Migrated old collection.')


def requirements_consistency_check(app):
    logging.info('Check requirements consistency.')
    filenames = utils.get_filenames_from_dir(app.config['SESSION_FOLDER'])
    var_collection = utils.pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    result = dict()
    result['data'] = list()
    count = 0
    for filename in filenames:
        try:
            req = utils.pickle_load_from_dump(filename)  # type: Requirement
            if type(req) == Requirement:
                changes = False
                if req.formalizations is None:
                    req.formalizations = list()
                    changes = True
                if type(req.type_in_csv) is tuple:
                    changes = True
                    req.type_in_csv = req.type_in_csv[0]
                if type(req.csv_row) is tuple:
                    changes = True
                    req.csv_row = req.csv_row[0]
                if type(req.description) is tuple:
                    changes = True
                    req.description = req.description[0]
                if changes:
                    count += 1
                    utils.store_requirement(req, app)
        except ModuleNotFoundError:
            # The "old" requirements before the refactoring.
            sys.modules['reqtransformer.reqtransformer'] = reqtransformer
            sys.modules['reqtransformer.patterns'] = reqtransformer
            req = utils.pickle_load_from_dump(filename)  # type: Requirement

            # gather data from old requirement.
            rid = req.rid
            csv_row = req.csv_row
            description = req.description
            formalization = req.formalization
            expressions = dict()
            if req.pattern_variables is not None:
                for key, var in req.pattern_variables.items():
                    expressions[key] = var.name
            pos_in_csv = req.position_in_csv_row
            scoped_pattern = req.scoped_pattern
            if scoped_pattern is not None:
                scope = str(scoped_pattern.scope.name)
                pattern = str(scoped_pattern.pattern)
                pattern_name = scoped_pattern.pattern.name
            status = req.status
            tags = req.tags
            type_in_csv = req.type_in_csv

            # Remove the modules hack so the next picke dump will use the correct module.
            del sys.modules['reqtransformer.reqtransformer']
            del sys.modules['reqtransformer.patterns']

            # Create the corresponding new Requirement
            new_requirement = Requirement(
                rid=rid,
                description=description,
                type_in_csv=type_in_csv,
                csv_row=csv_row,
                pos_in_csv=pos_in_csv
            )
            if scoped_pattern is not None:
                # Create Formalization
                formalization = Formalization()
                formalization.scoped_pattern = ScopedPattern(
                    Scope[scope], Pattern(name=pattern_name)
                )
                # set parent
                formalization.belongs_to_requirement = rid
                # Parse and set the expressions.
                formalization.set_expressions_mapping(
                    mapping=expressions,
                    variable_collection=var_collection,
                    app=app,
                    rid=rid
                )
                new_requirement.formalizations.append(formalization)
            new_requirement.status = status
            new_requirement.tags = tags
            utils.pickle_dump_obj_to_file(new_requirement, filename)
            count += 1

    if count > 0:
        logging.info('Done with consistency check. Repaired {} requirements'.format(count))

if __name__ == '__main__':
    utils.setup_logging(app)

    # Setup for debug
    app.debug = app.config['DEBUG_MODE']
    if app.config['DEBUG_MODE']:
        toolbar = DebugToolbarExtension(app)
    utils.register_assets(app)

    # Parse python args and init config.
    args = utils.HanforArgumentParser(app).parse_args()
    app.config['SESSION_TAG'] = args.tag
    if app.config['SESSION_BASE_FOLDER'] is None:
        app.config['SESSION_FOLDER'] = os.path.join(HERE, 'data', app.config['SESSION_TAG'])
    else:
        app.config['SESSION_FOLDER'] = os.path.join(app.config['SESSION_BASE_FOLDER'], app.config['SESSION_TAG'])
    app.config['TEMPLATES_FOLDER'] = os.path.join(HERE, 'templates')
    app.config['SESSION_VARIABLE_COLLECTION'] = os.path.join(
        app.config['SESSION_FOLDER'],
        'session_variable_collection.pickle'
    )
    app.config['SESSION_STATUS'] = os.path.join(
        app.config['SESSION_FOLDER'],
        'session_status.pickle'
    )

    # Initialize sessioin if this is a new one.
    if not os.path.exists(app.config['SESSION_FOLDER']):
        # Load requirements from .csv file and store them into separate requirements.
        requirement_collection = RequirementCollection()
        requirement_collection.create_from_csv(csv_file=args.input_csv, input_encoding='utf8')

        # Store Requirements as pickeled objects to the session dir.
        os.makedirs(app.config['SESSION_FOLDER'], exist_ok=True)
        for index, req in enumerate(requirement_collection.requirements):  # type: Requirement
            filename = os.path.join(app.config['SESSION_FOLDER'], '{}.pickle'.format(req.rid))
            utils.pickle_dump_obj_to_file(req, filename)

        # Generate the session dict: Store some meta information.
        session = dict()
        session['csv_input_file'] = args.input_csv
        session['csv_fieldnames'] = requirement_collection.csv_meta['fieldnames']
        session['csv_id_header'] = requirement_collection.csv_meta['id_header']
        session['csv_formal_header'] = requirement_collection.csv_meta['formal_header']
        session['csv_type_header'] = requirement_collection.csv_meta['type_header']
        session['csv_desc_header'] = requirement_collection.csv_meta['desc_header']
        session['csv_dialect'] = requirement_collection.csv_meta['dialect']
        utils.pickle_dump_obj_to_file(session, app.config['SESSION_STATUS'])

    # Initialize variables collection.
    if not os.path.exists(app.config['SESSION_VARIABLE_COLLECTION']):
        var_collection = VariableCollection()
        utils.pickle_dump_obj_to_file(var_collection, app.config['SESSION_VARIABLE_COLLECTION'])

    # Run consistency checks.
    varcollection_consistency_check(app)
    requirements_consistency_check(app)

    # Run the app
    app_options = {
        'host': app.config['HOST'],
        'port': app.config['PORT']

    }
    PYCHARM_DEBUG = False
    if PYCHARM_DEBUG:
        app_options["debug"] = False
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    app.run(**app_options)
