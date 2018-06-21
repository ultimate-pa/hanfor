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

from flask import Flask, render_template, request, jsonify, url_for, make_response, send_file, json, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_restful import reqparse, abort, Api, Resource
from functools import wraps, update_wrapper
import reqtransformer
from reqtransformer import RequirementCollection, Requirement, VariableCollection, Formalization, Variable, Scope, \
    ScopedPattern, Pattern
from guesser.guesser_registerer import REGISTERED_GUESSERS

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


@app.route('/api/table/colum_defs', methods=['GET'])
@nocache
def table_api():
    result = utils.get_datatable_additional_cols(app)

    return jsonify(result)


@app.route('/api/<resource>/<command>', methods=['GET', 'POST'])
@nocache
def api(resource, command):
    resources = [
        'req',
        'var',
        'stats',
        'tag',
        'meta',
        'logs'
    ]
    commands = [
        'get',
        'gets',
        'set',
        'update',
        'delete',
        'predict_pattern',
        'new_formalization',
        'new_constraint',
        'del_formalization',
        'del_tag',
        'multi_update',
        'var_import_info',
        'var_import_collection',
        'get_available_guesses',
        'add_formalization_from_guess',
        'multi_add_top_guess'
    ]
    if resource not in resources or command not in commands:
        return jsonify({
            'success': False,
            'errormsg': 'sorry, request not supported.'
        }), 200

    if resource == 'req':
        # Get a single requirement.
        if command == 'get' and request.method == 'GET':
            id = request.args.get('id', '')
            requirement = utils.load_requirement_by_id(id, app)  # type: Requirement
            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

            result = requirement.to_dict()
            result['formalizations_html'] = utils.formalizations_to_html(app, requirement.formalizations)
            result['available_vars'] = var_collection.get_available_var_names_list(used_only=False)

            if requirement:
                return jsonify(result)

        # Get all requirements
        if command == 'gets':
            filenames = utils.get_filenames_from_dir(app.config['REVISION_FOLDER'])
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
            row_idx = request.form.get('row_idx', '')
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
                        utils.add_msg_to_flask_session_log(session, 'Updated requirement', id)
                    except KeyError as e:
                        error = True
                        error_msg = 'Could not set formalization: Missing expression/variable for {}'.format(e)
                    except Exception as e:
                        error = True
                        error_msg = 'Could not parse formalization: `{}`'.format(e)
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

        # Multi Update Tags or Status.
        if command == 'multi_update':
            logging.info('Multi edit requirements.')
            result = {'success': True, 'errormsg': ''}

            # Get user Input
            add_tag = request.form.get('add_tag', '').strip()
            remove_tag = request.form.get('remove_tag', '').strip()
            set_status = request.form.get('set_status', '').strip()
            rid_list = request.form.get('selected_ids', '')
            logging.debug(rid_list)
            if len(rid_list) > 0:
                rid_list = json.loads(rid_list)
            else:
                result['success'] = False
                result['errormsg'] = 'No requirements selected.'

            # Check if the status is valid.
            available_status = ['Todo', 'Review', 'Done']
            if len(set_status) > 0 and set_status not in available_status:
                result['success'] = False
                result['errormsg'] = 'Status `{}` not supported.\nChoose from `{}`'.format(
                    set_status, ', '.join(available_status))

            # Update all requirements given by the rid_list
            if result['success']:
                log_msg = 'Update {} requirements.'.format(len(rid_list))
                if len(add_tag) > 0:
                    log_msg += ' Adding tag `{}`'.format(add_tag)
                    utils.add_msg_to_flask_session_log(
                        session, 'Adding tag `{}` to requirements.'.format(
                            add_tag
                        ),
                        rid_list=rid_list
                    )
                if len(remove_tag) > 0:
                    log_msg += ', removing Tag `{}` (is present)'.format(remove_tag)
                    utils.add_msg_to_flask_session_log(
                        session, 'Removing tag `{}` from requirements.'.format(
                            remove_tag
                        ),
                        rid_list=rid_list
                    )
                if len(set_status) > 0:
                    log_msg += ', set Status=`{}`.'.format(set_status)
                    utils.add_msg_to_flask_session_log(
                        session, 'Set status to `{}` for requirements. '.format(
                            set_status
                        ),
                        rid_list=rid_list
                    )
                logging.info(log_msg)

                for rid in rid_list:
                    requirement = utils.load_requirement_by_id(rid, app)  # type: Requirement
                    if requirement is not None:
                        logging.info('Updating requirement `{}`'.format(rid))
                        requirement.tags.discard(remove_tag)
                        requirement.tags.add(add_tag)
                        if set_status:
                            requirement.status = set_status
                        utils.store_requirement(requirement, app)

            return jsonify(result)

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
            utils.add_msg_to_flask_session_log(session, 'Added new Formalization to requirement', id)
            result = utils.get_formalization_template(
                app.config['TEMPLATES_FOLDER'],
                requirement,
                formalization_id,
                formalization
            )
            return jsonify(result)

        # Delete a formalization
        if command == 'del_formalization' and request.method == 'POST':
            result = dict()
            formalization_id = request.form.get('formalization_id', '')
            requirement_id = request.form.get('requirement_id', '')
            requirement = utils.load_requirement_by_id(requirement_id, app)  # type: Requirement
            requirement.delete_formalization(formalization_id, app)
            utils.store_requirement(requirement, app)
            utils.add_msg_to_flask_session_log(session, 'Deleted formalization from requirement', requirement_id)
            result['html'] = utils.formalizations_to_html(app, requirement.formalizations)
            return jsonify(result)

        # Get available guesses.
        if command == 'get_available_guesses' and request.method == 'POST':
            result = {'success': True}
            requirement_id = request.form.get('requirement_id', '')
            requirement = utils.load_requirement_by_id(requirement_id, app)  # type: Requirement
            if requirement is None:
                result['success'] = False
                result['errormsg'] = 'Requirement `{}` not found'.format(requirement_id)
            else:
                result['available_guesses'] = list()
                tmp_guesses = list()
                var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

                for guesser in REGISTERED_GUESSERS:
                    try:
                        guesser_instance = guesser(requirement, var_collection, app)
                        guesser_instance.guess()
                        tmp_guesses += guesser_instance.guesses
                    except ValueError as e:
                        result['success'] = False
                        result['errormsg'] = 'Could not determine a guess: '
                        result['errormsg'] += e.__str__()

                tmp_guesses = sorted(tmp_guesses, key=lambda guess: guess[0])
                for score, scoped_pattern, mapping in tmp_guesses:
                    result['available_guesses'].append(
                        {
                            'scope': scoped_pattern.scope.name,
                            'pattern': scoped_pattern.pattern.name,
                            'mapping': mapping,
                            'string': scoped_pattern.get_string(mapping)
                        }
                    )

            return jsonify(result)

        if command == 'add_formalization_from_guess' and request.method == 'POST':
            requirement_id = request.form.get('requirement_id', '')
            scope = request.form.get('scope', '')
            pattern = request.form.get('pattern', '')
            mapping = request.form.get('mapping', '')
            mapping = json.loads(mapping)

            # Add an empty Formalization.
            requirement = utils.load_requirement_by_id(requirement_id, app)  # type: Requirement
            formalization_id, formalization = requirement.add_empty_formalization()
            # Add add content to the formalization.
            requirement.update_formalization(
                formalization_id=formalization_id,
                scope_name=scope,
                pattern_name=pattern,
                mapping=mapping,
                app=app
            )
            utils.store_requirement(requirement, app)
            utils.add_msg_to_flask_session_log(session, 'Added formalization guess to requirement', requirement_id)

            result = utils.get_formalization_template(
                app.config['TEMPLATES_FOLDER'],
                requirement,
                formalization_id,
                requirement.formalizations[formalization_id]
            )

            return jsonify(result)

        if command == 'multi_add_top_guess' and request.method == 'POST':
            result = {'success': True}
            requirement_ids = request.form.get('selected_ids', '')
            if len(requirement_ids) > 0:
                requirement_ids = json.loads(requirement_ids)
            else:
                result['success'] = False
                result['errormsg'] = 'No requirements selected.'

            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
            for req_id in requirement_ids:
                requirement = utils.load_requirement_by_id(req_id, app)  # type: Requirement
                if requirement is not None:
                    logging.info('Add top guess to requirement `{}`'.format(req_id))
                    tmp_guesses = list()
                    for guesser in REGISTERED_GUESSERS:
                        try:
                            guesser_instance = guesser(requirement, var_collection, app)
                            guesser_instance.guess()
                            tmp_guesses += guesser_instance.guesses
                            tmp_guesses = sorted(tmp_guesses, key=lambda guess: guess[0])
                            if len(tmp_guesses) > 0:
                                score, scoped_pattern, mapping = tmp_guesses[0]
                                formalization_id, formalization = requirement.add_empty_formalization()
                                # Add add content to the formalization.
                                requirement.update_formalization(
                                    formalization_id=formalization_id,
                                    scope_name=scoped_pattern.scope.name,
                                    pattern_name=scoped_pattern.pattern.name,
                                    mapping=mapping,
                                    app=app
                                )
                                utils.store_requirement(requirement, app)
                        except ValueError as e:
                            result['success'] = False
                            result['errormsg'] = 'Could not determine a guess: '
                            result['errormsg'] += e.__str__()
            utils.add_msg_to_flask_session_log(session, 'Added top guess to requirements', rid_list=requirement_ids)

            return jsonify(result)

    if resource == 'var':
        # Get available variables
        result = {
            'success': False,
            'errormsg': 'sorry, request not supported.'
        }
        if command == 'gets':
            result = {'data': utils.get_available_vars(app, parser=boogie_parser, full=True)}
        elif command == 'update':
            result = utils.update_variable_in_collection(app, request)
        elif command == 'var_import_info':
            result = utils.varcollection_diff_info(app, request)
        elif command == 'var_import_collection':
            result = utils.varcollection_import_collection(app, request)
        elif command == 'multi_update':
            logging.info('Multi edit Variables.')
            result = {'success': True, 'errormsg': ''}

            # Get user Input.
            change_type = request.form.get('change_type', '').strip()
            var_list = request.form.get('selected_vars', '')
            delete = request.form.get('del', 'false')
            if len(var_list) > 0:
                var_list = json.loads(var_list)
            if len(change_type) > 0:
                logging.debug('Change type to `{}`.\nAffected Vars:\n{}'.format(change_type, '\n'.join(var_list)))
            if delete == 'true':
                logging.debug('Deleting variables.\nAffected Vars:\n{}'.format(change_type, '\n'.join(var_list)))
            else:
                result['success'] = False
                result['errormsg'] = 'No variables selected.'

            # Update all requirements given by the rid_list
            if result['success']:
                # Change the var type.
                if len(change_type) > 0:
                    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
                    for var_name in var_list:
                        try:
                            logging.debug('Set type for `{}` to `{}`. Formerly was `{}`'.format(
                                var_name,
                                change_type,
                                var_collection.collection[var_name].type
                            ))
                            var_collection.collection[var_name].type = change_type
                        except KeyError:
                            logging.debug('Variable `{}` not found'.format(var_list))
                    var_collection.store()
                if delete == 'true':
                    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
                    for var_name in var_list:
                        try:
                            logging.debug('Deleting `{}`'.format(var_name))
                            if var_name not in var_collection.var_req_mapping \
                                    or len(var_collection.var_req_mapping[var_name]) == 0:
                                # Delete if var not used.
                                var_collection.collection.pop(var_name, None)
                                var_collection.var_req_mapping.pop(var_name, None)
                        except KeyError:
                            logging.debug('Variable `{}` not found'.format(var_list))
                    var_collection.store()
            return jsonify(result)
        elif command == 'new_constraint':
            result = {'success': True, 'errormsg': ''}
            result['html'] = "<p>Hallo... </p>"
            return jsonify(result)

        return jsonify(result)

    if resource == 'stats':
        # Get all stats
        if command == 'gets':
            data = utils.get_statistics(app)
            return jsonify(data)

    if resource == 'tag':
        # Get all tags
        if command == 'gets':
            return jsonify({'data': utils.get_available_tags(app)})
        if command == 'update':
            return jsonify(utils.update_tag(app, request))
        if command == 'del_tag':
            return jsonify(utils.update_tag(app, request, delete=True))

    if resource == 'meta':
        if command == 'get':
            return jsonify(utils.MetaSettings(app.config['META_SETTTINGS_PATH']).__dict__)

    if resource == 'logs':
        if command == 'get':
            return utils.get_flask_session_log(session, html=True)

    return jsonify({
        'success': False,
        'errormsg': 'sorry, could not parse your request.'
    }), 200


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
        if site == 'variables':
            available_sessions = utils.get_stored_session_names(
                app.config['SESSION_BASE_FOLDER'],
                only_names=True,
                with_revisions=True
            )
            return render_template(
                '{}.html'.format(site),
                available_sessions=available_sessions,
                current_session=app.config['SESSION_TAG'],
                current_revision=app.config['USING_REVISION']
            )
        else:
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
    default_cols = [
        {'name': 'Pos', 'target': 1},
        {'name': 'Id', 'target': 2},
        {'name': 'Description', 'target': 3},
        {'name': 'Type', 'target': 4},
        {'name': 'Tags', 'target': 5},
        {'name': 'Status', 'target': 6},
        {'name': 'Formalization', 'target': 7}
    ]
    additional_cols = utils.get_datatable_additional_cols(app)['col_defs']
    return render_template('index.html', query=query, additional_cols=additional_cols, default_cols=default_cols)


def varcollection_consistency_check(app):
    logging.info('Check varcollection consistency.')
    try:
        var_collection = utils.pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    except ImportError:
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


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: {}'.format(error))
    logging.error(error)

    return jsonify({
        'success': False,
        'errormsg': 'Server Error: {}'.format(error)
    })


@app.errorhandler(Exception)
def unhandled_exception(exception):
    app.logger.error('Unhandled Exception: {}'.format(exception))
    logging.exception(exception)

    return jsonify({
        'success': False,
        'errormsg': 'Unhandled Exception: {}'.format(exception)
    })


def requirements_consistency_check(app, args):
    logging.info('Check requirements consistency.')
    filenames = utils.get_filenames_from_dir(app.config['REVISION_FOLDER'])
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
                # Derive type inference errors if not set.
                try:
                    for formalization in req.formalizations:
                        tmp = formalization.type_inference_errors
                except:
                    logging.info('Update type inference results for `{}`'.format(req.rid))
                    req.reload_type_inference(var_collection, app)
                if args.reload_type_inference:
                    req.reload_type_inference(var_collection, app)
                if changes:
                    count += 1
                    utils.store_requirement(req, app)
        except ImportError:
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


def create_revision(input_csv, base_revision_name):
    # Create initial revision if no base revision is given
    if not base_revision_name:
        revision_name = 'revision_0'
        base_revision_settings = None
    # Revision based on a existing revision
    else:
        new_revision_count = max([int(name.split('_')[1]) for name in utils.get_available_revisions(app.config)]) + 1
        revision_name = 'revision_{}'.format(new_revision_count)
        base_revision_folder = os.path.join(
            app.config['SESSION_FOLDER'],
            base_revision_name
        )
        base_revision_var_collectioin_path = os.path.join(
            base_revision_folder,
            'session_variable_collection.pickle'
        )
        base_revision_settings = utils.pickle_load_from_dump(
            os.path.join(
                base_revision_folder,
                'session_status.pickle'
            )
        )

    if base_revision_name and base_revision_name not in utils.get_available_revisions(app.config):
        logging.error('Base revision `{}` not found in `{}`'.format(base_revision_name, app.config['SESSION_FOLDER']))
        raise FileNotFoundError

    app.config['USING_REVISION'] = revision_name
    app.config['REVISION_FOLDER'] = os.path.join(
        app.config['SESSION_FOLDER'],
        revision_name
    )
    app.config['SESSION_VARIABLE_COLLECTION'] = os.path.join(
        app.config['REVISION_FOLDER'],
        'session_variable_collection.pickle'
    )
    app.config['SESSION_STATUS_PATH'] = os.path.join(
        app.config['REVISION_FOLDER'],
        'session_status.pickle'
    )
    # Load requirements from .csv file and store them into separate requirements.
    requirement_collection = RequirementCollection()
    requirement_collection.create_from_csv(
        csv_file=input_csv,
        input_encoding='utf8',
        base_revision_headers=base_revision_settings
    )

    # Store Requirements as pickeled objects to the session dir.
    os.makedirs(app.config['REVISION_FOLDER'], exist_ok=True)
    for index, req in enumerate(requirement_collection.requirements):  # type: Requirement
        filename = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(req.rid))
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
    utils.pickle_dump_obj_to_file(session, app.config['SESSION_STATUS_PATH'])

    # No need to merge anything if we created only the base revision
    if revision_name == 'revision_0':
        return

    # Merge the old revision into the new revision
    logging.info('Merging `{}` into `{}`.'.format(base_revision_name, revision_name))
    old_reqs = dict()
    for filename in utils.get_filenames_from_dir(base_revision_folder):
        r = utils.pickle_load_from_dump(filename)  # type: Requirement
        if type(r) is Requirement:
            old_reqs[r.rid] = {
                'req': r,
                'path': filename
            }
    new_reqs = dict()
    for filename in utils.get_filenames_from_dir(app.config['REVISION_FOLDER']):
        r = utils.pickle_load_from_dump(filename)  # type: Requirement
        if type(r) is Requirement:
            new_reqs[r.rid] = {
                'req': r,
                'path': filename
            }
    # Compare diff for the requirements.
    for rid in new_reqs.keys():
        # Tag newly introduced requirements.
        if rid not in old_reqs.keys():
            logging.info('Add newly introduced requirement `{}`'.format(rid))
            new_reqs[rid]['req'].tags.add('new_in_{}'.format(revision_name))
            continue
        # Migrate tags and status.
        new_reqs[rid]['req'].tags = old_reqs[rid]['req'].tags
        new_reqs[rid]['req'].status = old_reqs[rid]['req'].status

        # If the new formalization is empty: just migrate the formalization.
        #  - Tag with `migrated_formalization` if the description changed.
        if len(new_reqs[rid]['req'].formalizations) == 0:
            logging.info('Migrate formalization for `{}`'.format(rid))
            new_reqs[rid]['req'].formalizations = old_reqs[rid]['req'].formalizations
            if new_reqs[rid]['req'].description != old_reqs[rid]['req'].description:
                logging.info(
                    'Add `migrated_formalization` tag to `{}`, status to `Todo` since description changed'.format(rid))
                new_reqs[rid]['req'].tags.add('migrated_formalization')
                new_reqs[rid]['req'].status = 'Todo'
        # Handle existing formalizations
        else:
            # Todo: Resolve formalization conflicts.
            raise NotImplementedError

    # Store the updated requirements for the new revision.
    logging.info('Store merge changes to new `{}`'.format(revision_name))
    for r in new_reqs.values():
        utils.pickle_dump_obj_to_file(r['req'], r['path'])

    # Store the variables collection in the new revision.
    logging.info('Migrate variables from `{}` to `{}`'.format(base_revision_name, revision_name))
    utils.pickle_dump_obj_to_file(
        utils.pickle_load_from_dump(base_revision_var_collectioin_path),
        app.config['SESSION_VARIABLE_COLLECTION']
    )


def load_revision(revision_id):
    """ Loads a revision to by served by hanfor by setting the config.

    :param revision_id: An existing revision name
    :type revision_id: str
    """
    if revision_id not in utils.get_available_revisions(app.config):
        logging.error('Revision `{}` not found in `{}`'.format(revision_id, app.config['SESSION_FOLDER']))
        raise FileNotFoundError

    app.config['USING_REVISION'] = revision_id
    app.config['REVISION_FOLDER'] = os.path.join(
        app.config['SESSION_FOLDER'],
        revision_id
    )
    app.config['SESSION_VARIABLE_COLLECTION'] = os.path.join(
        app.config['REVISION_FOLDER'],
        'session_variable_collection.pickle'
    )
    app.config['SESSION_STATUS_PATH'] = os.path.join(
        app.config['REVISION_FOLDER'],
        'session_status.pickle'
    )


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

    # Create a new revision.
    if args.revision:
        logging.info('Generating a new revision.')
        available_sessions = utils.get_stored_session_names(app.config['SESSION_BASE_FOLDER'], only_names=True)
        if app.config['SESSION_TAG'] not in available_sessions:
            logging.error('Session `{tag}` not found (in `{sessions_folder}`)'.format(
                tag=app.config['SESSION_TAG'],
                sessions_folder=app.config['SESSION_BASE_FOLDER']
            ))
            raise FileNotFoundError
        # Ask user for base revision.
        available_revisions = utils.get_available_revisions(app.config)
        if len(available_revisions) == 0:
            logging.error('No base revisions found in `{}`.'.format(app.config['SESSION_FOLDER']))
            raise FileNotFoundError
        print('Which revision should I use as a base?')
        base_revision_choice = utils.choice(available_revisions, 'revision_0')
        create_revision(args.input_csv, base_revision_choice)

    # If we should not create a new revision: Create a new session or load a existing session revision.
    else:
        # If there is no session with given tak: Create a new (initial) revision.
        if not os.path.exists(app.config['SESSION_FOLDER']):
            create_revision(args.input_csv, None)

        # If this is a already existing session, ask the user which revision to start.
        else:
            available_revisions = utils.get_available_revisions(app.config)
            # Start the first revision if there is only one.
            if len(available_revisions) == 1:
                revision_choice = available_revisions[0]
            # If there is no revision it means probably that this is an old hanfor version.
            # ask the user to migrate.
            elif len(available_revisions) == 0:
                print('No revisions found. You might use a deprecated session version without revision support.')
                print('Is that true and should I migrate this session?')
                migrate_session = utils.choice(['yes', 'no'], 'no')
                if migrate_session == 'yes':
                    revision_choice = 'revision_0'
                    file_paths = [
                        path for path in utils.get_filenames_from_dir(app.config['SESSION_FOLDER'])
                        if path.endswith('.pickle')
                    ]
                    revision_folder = os.path.join(
                        app.config['SESSION_FOLDER'],
                        revision_choice
                    )
                    logging.info('Create revision folder and copy existing data.')
                    os.makedirs(revision_folder, exist_ok=True)
                    for path in file_paths:
                        new_path = os.path.join(
                            revision_folder,
                            os.path.basename(path)
                        )
                        os.rename(path, new_path)
                else:
                    exit()
            else:
                print('Which revision should I start.')
                available_revisions = sorted(utils.get_available_revisions(app.config))
                revision_choice = utils.choice(available_revisions, available_revisions[-1])
            logging.info('Loading session `{}` at `{}`'.format(app.config['SESSION_TAG'], revision_choice))
            load_revision(revision_choice)

    app.config['TEMPLATES_FOLDER'] = os.path.join(HERE, 'templates')

    # Initialize variables collection.
    if not os.path.exists(app.config['SESSION_VARIABLE_COLLECTION']):
        var_collection = VariableCollection()
        utils.pickle_dump_obj_to_file(var_collection, app.config['SESSION_VARIABLE_COLLECTION'])

    # Initilize meta settings
    app.config['META_SETTTINGS_PATH'] = os.path.join(app.config['SESSION_FOLDER'], 'meta_settings.pickle')
    if not os.path.exists(app.config['META_SETTTINGS_PATH']):
        meta_settings = dict()
        meta_settings['tag_colors'] = dict()
        utils.pickle_dump_obj_to_file(meta_settings, app.config['META_SETTTINGS_PATH'])

    # Run consistency checks.
    varcollection_consistency_check(app)
    requirements_consistency_check(app, args)

    # Run the app
    app_options = {
        'host': app.config['HOST'],
        'port': app.config['PORT']
    }

    if app.config['PYCHARM_DEBUG']:
        app_options["debug"] = False
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    app.run(**app_options)
