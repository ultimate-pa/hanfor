""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import datetime
import logging
import os
import sys

import re
import subprocess
import uuid
import utils

from static_utils import get_filenames_from_dir, pickle_dump_obj_to_file, choice, pickle_load_from_dump
from flask import Flask, render_template, request, jsonify, url_for, make_response, send_file, json, session
from flask_debugtoolbar import DebugToolbarExtension
from functools import wraps, update_wrapper
import reqtransformer
from guesser.Guess import Guess
from reqtransformer import RequirementCollection, Requirement, VariableCollection, Formalization, Variable, Scope, \
    ScopedPattern, Pattern, VarImportSession, VarImportSessions
from guesser.guesser_registerer import REGISTERED_GUESSERS

from ressources import Report, Tag


# Create the app
app = Flask(__name__)
app.config.from_object('config')

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


@app.route('/api/<resource>/<command>', methods=['GET', 'POST', 'DELETE'])
@nocache
def api(resource, command):
    resources = [
        'req',
        'var',
        'stats',
        'tag',
        'meta',
        'logs',
        'req_search',
        'report'
    ]
    commands = [
        'get',
        'gets',
        'set',
        'update',
        'delete',
        'new_formalization',
        'new_constraint',
        'del_formalization',
        'del_tag',
        'del_var',
        'multi_update',
        'var_import_info',
        'get_available_guesses',
        'add_formalization_from_guess',
        'multi_add_top_guess',
        'get_constraints_html',
        'del_constraint',
        'add_new_enum',
        'get_enumerators',
        'start_import_session',
        'gen_req'
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
            requirement = Requirement.load_requirement_by_id(id, app)
            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

            result = requirement.to_dict()
            result['formalizations_html'] = utils.formalizations_to_html(app, requirement.formalizations)
            result['available_vars'] = var_collection.get_available_var_names_list(
                used_only=False,
                exclude_types={'ENUM'}
            )

            if requirement:
                return jsonify(result)

        # Get all requirements
        if command == 'gets':
            filenames = get_filenames_from_dir(app.config['REVISION_FOLDER'])
            result = dict()
            result['data'] = list()
            for filename in filenames:
                try:
                    req = Requirement.load(filename)
                    result['data'].append(req.to_dict())
                except:
                    continue
            return jsonify(result)

        # Update a requirement
        if command == 'update' and request.method == 'POST':
            id = request.form.get('id', '')
            requirement = Requirement.load_requirement_by_id(id, app)
            error = False
            error_msg = ''

            if requirement:
                logging.debug('Updating requirement: {}'.format(requirement.rid))

                new_status = request.form.get('status', '')
                if requirement.status != new_status:
                    requirement.status = new_status
                    utils.add_msg_to_flask_session_log(
                        app, 'Set status to `{}` for requirement'.format(new_status), id
                    )
                    logging.debug('Requirement status set to `{}`'.format(requirement.status))

                new_tag_set = set(t.strip() for t in request.form.get('tags', '').split(','))
                if requirement.tags != new_tag_set:
                    added_tags = new_tag_set - requirement.tags
                    removed_tags = requirement.tags - new_tag_set
                    requirement.tags = new_tag_set
                    if added_tags:
                        utils.add_msg_to_flask_session_log(
                            app, 'Added tags `{}` to requirement'.format(', '.join(added_tags)), id
                        )
                        logging.debug(
                            'Added tags `{}` to requirement `{}`'.format(', '.join(added_tags), requirement.tags)
                        )
                    if removed_tags:
                        utils.add_msg_to_flask_session_log(
                            app, 'Removed tags `{}` from requirement'.format(', '.join(removed_tags)), id
                        )
                        logging.debug(
                            'Removed tags `{}` from requirement `{}`'.format(', '.join(removed_tags), requirement.tags)
                        )

                # Update formalization.
                if request.form.get('update_formalization') == 'true':
                    formalizations = json.loads(request.form.get('formalizations', ''))
                    logging.debug('Updated Formalizations: {}'.format(formalizations))
                    try:
                        requirement.update_formalizations(formalizations, app)
                        utils.add_msg_to_flask_session_log(app, 'Updated requirement formalization', id)
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
                    requirement.store()
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
                        app, 'Adding tag `{}` to requirements.'.format(
                            add_tag
                        ),
                        rid_list=rid_list
                    )
                if len(remove_tag) > 0:
                    log_msg += ', removing Tag `{}` (is present)'.format(remove_tag)
                    utils.add_msg_to_flask_session_log(
                        app, 'Removing tag `{}` from requirements.'.format(
                            remove_tag
                        ),
                        rid_list=rid_list
                    )
                if len(set_status) > 0:
                    log_msg += ', set Status=`{}`.'.format(set_status)
                    utils.add_msg_to_flask_session_log(
                        app, 'Set status to `{}` for requirements. '.format(
                            set_status
                        ),
                        rid_list=rid_list
                    )
                logging.info(log_msg)

                for rid in rid_list:
                    requirement = Requirement.load_requirement_by_id(rid, app)
                    if requirement is not None:
                        logging.info('Updating requirement `{}`'.format(rid))
                        requirement.tags.discard(remove_tag)
                        requirement.tags.add(add_tag)
                        if set_status:
                            requirement.status = set_status
                        requirement.store()

            return jsonify(result)

        # Add a new empty formalization
        if command == 'new_formalization' and request.method == 'POST':
            id = request.form.get('id', '')
            requirement = Requirement.load_requirement_by_id(id, app)  # type: Requirement
            formalization_id, formalization = requirement.add_empty_formalization()
            requirement.store()
            utils.add_msg_to_flask_session_log(app, 'Added new Formalization to requirement', id)
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
            requirement = Requirement.load_requirement_by_id(requirement_id, app)
            requirement.delete_formalization(formalization_id, app)
            requirement.store()
            utils.add_msg_to_flask_session_log(app, 'Deleted formalization from requirement', requirement_id)
            result['html'] = utils.formalizations_to_html(app, requirement.formalizations)
            return jsonify(result)

        # Get available guesses.
        if command == 'get_available_guesses' and request.method == 'POST':
            result = {'success': True}
            requirement_id = request.form.get('requirement_id', '')
            requirement = Requirement.load_requirement_by_id(requirement_id, app)
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

                tmp_guesses = sorted(tmp_guesses, key=Guess.eval_score)
                guesses = list()
                for g in tmp_guesses:
                    if type(g) is list:
                        guesses += g
                    else:
                        guesses.append(g)

                for score, scoped_pattern, mapping in guesses:
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
            requirement = Requirement.load_requirement_by_id(requirement_id, app)
            formalization_id, formalization = requirement.add_empty_formalization()
            # Add add content to the formalization.
            requirement.update_formalization(
                formalization_id=formalization_id,
                scope_name=scope,
                pattern_name=pattern,
                mapping=mapping,
                app=app
            )
            requirement.store()
            utils.add_msg_to_flask_session_log(app, 'Added formalization guess to requirement', requirement_id)

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
            insert_mode = request.form.get('insert_mode', 'append')
            if len(requirement_ids) > 0:
                requirement_ids = json.loads(requirement_ids)
            else:
                result['success'] = False
                result['errormsg'] = 'No requirements selected.'

            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
            for req_id in requirement_ids:
                requirement = Requirement.load_requirement_by_id(req_id, app)
                if requirement is not None:
                    logging.info('Add top guess to requirement `{}`'.format(req_id))
                    tmp_guesses = list()
                    for guesser in REGISTERED_GUESSERS:
                        try:
                            guesser_instance = guesser(requirement, var_collection, app)
                            guesser_instance.guess()
                            tmp_guesses += guesser_instance.guesses
                            tmp_guesses = sorted(tmp_guesses, key=Guess.eval_score)
                            if len(tmp_guesses) > 0:
                                if type(tmp_guesses[0]) is Guess:
                                    top_guesses = [tmp_guesses[0]]
                                elif type(tmp_guesses[0]) is list:
                                    top_guesses = tmp_guesses[0]
                                else:
                                    raise TypeError('Type: `{}` not supported as guesses'.format(type(tmp_guesses[0])))
                                if insert_mode == 'override':
                                    for f_id in requirement.formalizations.keys():
                                        requirement.delete_formalization(f_id, app)
                                for score, scoped_pattern, mapping in top_guesses:
                                    formalization_id, formalization = requirement.add_empty_formalization()
                                    # Add add content to the formalization.
                                    requirement.update_formalization(
                                        formalization_id=formalization_id,
                                        scope_name=scoped_pattern.scope.name,
                                        pattern_name=scoped_pattern.pattern.name,
                                        mapping=mapping,
                                        app=app
                                    )
                                    requirement.store()
                        except ValueError as e:
                            result['success'] = False
                            result['errormsg'] = 'Could not determine a guess: '
                            result['errormsg'] += e.__str__()
            utils.add_msg_to_flask_session_log(app, 'Added top guess to requirements', rid_list=requirement_ids)

            return jsonify(result)

    if resource == 'var':
        # Get available variables
        result = {
            'success': False,
            'errormsg': 'sorry, request not supported.'
        }
        if command == 'gets':
            result = {'data': utils.get_available_vars(app, full=True)}
        elif command == 'update':
            result = utils.update_variable_in_collection(app, request)
        elif command == 'var_import_info':
            result = utils.varcollection_diff_info(app, request)
            varcollection_consistency_check(app)
        elif command == 'multi_update':
            logging.info('Multi edit Variables.')
            result = {'success': True, 'errormsg': ''}

            # Get user Input.
            change_type = request.form.get('change_type', '').strip()
            var_list = request.form.get('selected_vars', '')
            delete = request.form.get('del', 'false')
            if len(var_list) > 0:
                var_list = json.loads(var_list)
            else:
                result['success'] = False
                result['errormsg'] = 'No variables selected.'

            # Update all requirements given by the rid_list
            if result['success']:
                if len(change_type) > 0: # Change the var type.
                    logging.debug('Change type to `{}`.\nAffected Vars:\n{}'.format(change_type, '\n'.join(var_list)))
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
                    logging.info('Deleting variables.\nAffected Vars:\n{}'.format('\n'.join(var_list)))
                    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
                    for var_name in var_list:
                        try:
                            logging.debug('Deleting `{}`'.format(var_name))
                            var_collection.del_var(var_name)
                        except KeyError:
                            logging.debug('Variable `{}` not found'.format(var_list))
                    var_collection.store()

            return jsonify(result)
        elif command == 'new_constraint':
            result = {'success': True, 'errormsg': ''}
            var_name = request.form.get('name', '').strip()

            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
            var_collection.add_new_constraint(var_name=var_name)
            var_collection.store()
            result['html'] = utils.formalizations_to_html(app, var_collection.collection[var_name].constraints)
            return jsonify(result)
        elif command == 'get_constraints_html':
            result = {
                'success': True,
                'errormsg': '',
                'html': '<p>No constraints set.</p>',
                'type_inference_errors': dict()
            }
            var_name = request.form.get('name', '').strip()
            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
            try:
                var = var_collection.collection[var_name]
                var_dict = var.to_dict(var_collection.var_req_mapping)
                result['html'] = utils.formalizations_to_html(app, var.constraints)
                result['type_inference_errors'] = var_dict['type_inference_errors']
            except AttributeError:
                pass

            return jsonify(result)
        elif command == 'del_constraint':
            result = {'success': True, 'errormsg': ''}
            var_name = request.form.get('name', '').strip()
            constraint_id = request.form.get('constraint_id', '').strip()

            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
            var_collection.del_constraint(var_name=var_name, constraint_id=int(constraint_id))
            var_collection.collection[var_name].reload_constraints_type_inference_errors(var_collection)
            var_collection.store()
            result['html'] = utils.formalizations_to_html(app, var_collection.collection[var_name].get_constraints())
            return jsonify(result)
        elif command == 'del_var':
            result = {'success': True, 'errormsg': ''}
            var_name = request.form.get('name', '').strip()

            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
            try:
                logging.debug('Deleting `{}`'.format(var_name))
                success = var_collection.del_var(var_name)
                if not success:
                    result = {'success': False, 'errormsg': 'Variable is used and thus cannot be deleted.'}
                var_collection.store()
            except KeyError:
                logging.debug('Variable `{}` not found'.format(var_name))
                result = {'success': False, 'errormsg': 'Variable not found.'}
            return jsonify(result)
        elif command == 'add_new_enum':
            result = {'success': True, 'errormsg': ''}
            enum_name = request.form.get('name', '').strip()
            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

            if len(enum_name) == 0 or not re.match('^[a-zA-Z0-9_-]+$', enum_name):
                result = {
                    'success': False,
                    'errormsg': 'Illegal enum name. Must Be at least 1 Char and only alphanum + { -, _}'
                }
            elif var_collection.var_name_exists(enum_name):
                result = {
                    'success': False,
                    'errormsg': '`{}` is already existing.'.format(enum_name)
                }
            else:
                new_enum = Variable(enum_name, 'ENUM', None)
                logging.debug('Adding new Enum `{}` to Variable collection.'.format(enum_name))
                var_collection.collection[enum_name] = new_enum
                var_collection.store()
                return jsonify(result)
        elif command == 'get_enumerators':
            result = {'success': True, 'errormsg': ''}
            enumerators = []
            enum_name = request.form.get('name', '').strip()
            var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

            for other_var_name, other_var in var_collection.collection.items():
                if (len(other_var_name) > len(enum_name)
                    and other_var_name.startswith(enum_name)
                        and other_var.type == 'ENUMERATOR'):
                    enumerators.append((other_var_name, other_var.value))
            try:
                enumerators.sort(key=lambda x: float(x[1]))
            except Exception as e:
                logging.info('Cloud not sort ENUMERATORS: {}'.format(e))


            result['enumerators'] = enumerators

            return jsonify(result)
        elif command == 'start_import_session':
            result = {'success': True, 'errormsg': ''}
            # create a new import session.
            source_session_name = request.form.get('sess_name', '').strip()
            source_revision_name = request.form.get('sess_revision', '').strip()

            result['session_id'] = utils.varcollection_create_new_import_session(
                app=app,
                source_session_name=source_session_name,
                source_revision_name=source_revision_name
            )

            if result['session_id'] < 0:
                result['success'] = False
                result['errormsg'] = 'Could not create the import session.'

            return jsonify(result)
        elif command == 'gen_req':
            filename = utils.generate_req_file(app, variables_only=True)

            response = make_response(send_file(filename))
            basename = os.path.basename(filename)
            response.headers["Content-Disposition"] = \
                "attachment;" \
                "filename*=UTF-8''{utf_filename}".format(
                    utf_filename=basename
                )
            os.remove(filename)
            return response

        return jsonify(result)

    if resource == 'stats':
        # Get all stats
        if command == 'gets':
            data = utils.get_statistics(app)
            return jsonify(data)

    if resource == 'tag':
        return Tag(app, request).apply_request()

    if resource == 'meta':
        if command == 'get':
            return jsonify(utils.MetaSettings(app.config['META_SETTTINGS_PATH']).__dict__)

    if resource == 'logs':
        if command == 'get':
            return utils.get_flask_session_log(app, html=True)

    if resource == 'req_search':
        if command == 'update':
            return jsonify(utils.update_req_search(app, request)), 200
        if command == 'delete':
            return jsonify(utils.update_req_search(app, request, delete=True)), 200

    if resource == 'report':
            return Report(app, request).apply_request()

    return jsonify({
        'success': False,
        'errormsg': 'sorry, could not parse your request.'
    }), 200


@app.route('/variable_import/<id>', methods=['GET'])
@nocache
def variable_import(id):
    return render_template('variable-import-session.html', id=id)


@app.route('/variable_import/api/<session_id>/<command>', methods=['GET', 'POST'])
@nocache
def var_import_session(session_id, command):
    result = {
        'success': False,
        'errormsg': 'Command not found'
    }

    var_import_sessions = VarImportSessions.load_for_app(app)

    if command == 'get_var':
        result = dict()
        name = request.form.get('name', '')
        which_collection = request.form.get('which_collection', '')

        try:
            var_collection = var_import_sessions.import_sessions[int(session_id)]
            if which_collection == 'source_link':
                var_collection = var_collection.source_var_collection
            if which_collection == 'target_link':
                var_collection = var_collection.target_var_collection
            if which_collection == 'result_link':
                var_collection = var_collection.result_var_collection
            result = var_collection.collection[name].to_dict(var_collection.var_req_mapping)
        except Exception as e:
            logging.info('Could not load var: {} from import session: {}'.format(name, session_id))

        return jsonify(result), 200

    if command == 'get_table_data':
        result = dict()
        try:
            result = {'data': var_import_sessions.import_sessions[int(session_id)].to_datatables_data()}
        except Exception as e:
            logging.info('Could not load session with id: {} ({})'.format(session_id, e))
            raise e

        return jsonify(result), 200

    if command == 'store_table':
        rows = json.loads(request.form.get('rows', ''))
        try:
            logging.info('Store changes for variable import session: {}'.format(session_id))
            var_import_sessions.import_sessions[int(session_id)].store_changes(rows)
            var_import_sessions.store()
            result['success'] = True
        except Exception as e:
            logging.info('Could not store table: {}'.format(e))
            result['success'] = False
            result['errormsg'] = 'Could not store: {}'.format(e)

        return jsonify(result), 200

    if command == 'store_variable':
        row = json.loads(request.form.get('row', ''))
        try:
            logging.info('Store changes for variable "{}" of import session: {}'.format(row['name'], session_id))
            var_import_sessions.import_sessions[int(session_id)].store_variable(row)
            var_import_sessions.store()
            result['success'] = True
        except Exception as e:
            logging.info('Could not store table: {}'.format(e))
            result['success'] = False
            result['errormsg'] = 'Could not store: {}'.format(e)
        return jsonify(result), 200

    if command == 'apply_import':
        try:
            logging.info('Apply import for variable import session: {}'.format(session_id))
            var_import_sessions.import_sessions[int(session_id)].apply_constraint_selection()
            var_import_sessions.store()
            new_collection = var_import_sessions.import_sessions[int(session_id)].result_var_collection
            new_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
            varcollection_consistency_check(app)
            result['success'] = True
        except Exception as e:
            logging.info('Could not apply import: {}'.format(e))
            result['success'] = False
            result['errormsg'] = 'Could not apply import: {}'.format(e)

        return jsonify(result), 200

    if command == 'delete_me':
        try:
            logging.info('Deleting variable import session id: {}'.format(session_id))
            del var_import_sessions.import_sessions[int(session_id)]
            var_import_sessions.store()
            result['success'] = True
        except Exception as e:
            error_msg = 'Could not delete session with id {} due to: {}'.format(session_id, e)
            logging.info(error_msg)
            result['success'] = False
            result['errormsg'] = error_msg

        return jsonify(result), 200

    return jsonify(result), 200

@app.route('/<site>')
def site(site):
    available_sites = [
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
            running_import_sessions = VarImportSessions.load_for_app(app).info()
            return render_template(
                '{}.html'.format(site),
                available_sessions=available_sessions,
                running_import_sessions=running_import_sessions
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
    if hasattr(exception, 'code') and exception.code in range(300, 308):
        return exception
    app.logger.error('Unhandled Exception: {}'.format(exception))
    logging.exception(exception)

    return jsonify({
        'success': False,
        'errormsg': 'Unhandled Exception: {}'.format(exception)
    })


def update_var_usage(var_collection):
    var_collection.refresh_var_usage(app)
    var_collection.req_var_mapping = var_collection.invert_mapping(var_collection.var_req_mapping)
    var_collection.refresh_var_constraint_mapping()
    var_collection.store()


def varcollection_version_migrations(app, args):
    # Migrate from old Hanfor versions
    try:
        VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
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

        new_var_collection = VariableCollection(path=app.config['SESSION_VARIABLE_COLLECTION'])
        for var in vars_to_collection:
            new_var_collection.collection[var['name']] = Variable(var['name'], var['type'], var['value'])
        new_var_collection.store()
        logging.info('Migrated old collection.')


def varcollection_consistency_check(app, args=None):
    logging.info('Check Variables for consistency.')
    # Update usages and constraint type check.
    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
    if args is not None and args.reload_type_inference:
        var_collection.reload_type_inference_errors_in_constraints()

    update_var_usage(var_collection)
    var_collection.reload_script_results(app)
    var_collection.store()


def requirements_version_migrations(app, args):
    logging.info('Check requirements consistency.')
    filenames = get_filenames_from_dir(app.config['REVISION_FOLDER'])
    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
    result = dict()
    result['data'] = list()
    count = 0

    for filename in filenames:
        try:
            try:
                req = Requirement.load(filename)
            except TypeError:
                continue
            changes = False
            if req.formalizations is None:
                req.formalizations = dict()
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
                for formalization in req.formalizations.values():
                    tmp = formalization.type_inference_errors
            except:
                logging.info('Update type inference results for `{}`'.format(req.rid))
                req.reload_type_inference(var_collection, app)
            if args.reload_type_inference:
                req.reload_type_inference(var_collection, app)
            if changes:
                count += 1
                req.store()
        except ImportError:
            # The "old" requirements before the refactoring.
            logging.info('Migrate old requirement from `{}`'.format(filename))
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
                new_requirement.add_formalization(formalization)
            new_requirement.status = status
            new_requirement.tags = tags
            new_requirement.my_path = filename
            new_requirement.store()
            count += 1

    if count > 0:
        logging.info('Done with consistency check. Repaired {} requirements'.format(count))

    update_var_usage(var_collection)


def create_revision(args, base_revision_name):
    """ Create new revision.

    :param args: Parser arguments
    :param base_revision_name: Name of revision the created will be based on. Creates initial revision_0 if none given.
    :return: None
    """
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
        csv_file=args.input_csv,
        input_encoding='utf8',
        base_revision_headers=base_revision_settings
    )

    # Store Requirements as pickeled objects to the session dir.
    os.makedirs(app.config['REVISION_FOLDER'], exist_ok=True)
    for index, req in enumerate(requirement_collection.requirements):  # type: Requirement
        filename = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(req.rid))
        req.store(filename)

    # Generate the session dict: Store some meta information.
    session = dict()
    session['csv_input_file'] = args.input_csv
    session['csv_fieldnames'] = requirement_collection.csv_meta['fieldnames']
    session['csv_id_header'] = requirement_collection.csv_meta['id_header']
    session['csv_formal_header'] = requirement_collection.csv_meta['formal_header']
    session['csv_type_header'] = requirement_collection.csv_meta['type_header']
    session['csv_desc_header'] = requirement_collection.csv_meta['desc_header']
    session['csv_dialect'] = requirement_collection.csv_meta['dialect']
    pickle_dump_obj_to_file(session, app.config['SESSION_STATUS_PATH'])

    # No need to merge anything if we created only the base revision
    if revision_name == 'revision_0':
        return

    # Merge the old revision into the new revision
    logging.info('Merging `{}` into `{}`.'.format(base_revision_name, revision_name))
    old_reqs = dict()
    for filename in get_filenames_from_dir(base_revision_folder):
        try:
            r = Requirement.load(filename)
            old_reqs[r.rid] = {
                'req': r,
                'path': filename
            }
        except TypeError:
            continue
        except Exception as e:
            raise e
    new_reqs = dict()
    for filename in get_filenames_from_dir(app.config['REVISION_FOLDER']):
        try:
            r = Requirement.load(filename)  # type: Requirement
            new_reqs[r.rid] = {
                'req': r,
                'path': filename
            }
        except TypeError:
            continue
        except Exception as e:
            raise e

    # Compare diff for the requirements.
    for rid in new_reqs.keys():
        # Tag newly introduced requirements.
        if rid not in old_reqs.keys():
            logging.info('Add newly introduced requirement `{}`'.format(rid))
            new_reqs[rid]['req'].tags.add('{}_to_{}_new_requirement'.format(base_revision_name, revision_name))
            continue
        # Migrate tags and status.
        new_reqs[rid]['req'].tags = old_reqs[rid]['req'].tags
        new_reqs[rid]['req'].status = old_reqs[rid]['req'].status

        if new_reqs[rid]['req'].csv_row != old_reqs[rid]['req'].csv_row:
            logging.info(
                'CSV entry changed. Add `revision_data_changed` tag to `{}`.'.format(rid)
            )
            new_reqs[rid]['req'].tags.add('{}_to_{}_data_changed'.format(base_revision_name, revision_name))

        if new_reqs[rid]['req'].description != old_reqs[rid]['req'].description:
            logging.info(
                'Description changed. Add `description_changed` tag to `{}`.'.format(rid)
            )
            new_reqs[rid]['req'].tags.add('{}_to_{}_description_changed'.format(base_revision_name, revision_name))
            new_reqs[rid]['req'].status = 'Todo'

        # If the new formalization is empty: just migrate the formalization.
        #  - Tag with `migrated_formalization` if the description changed.
        if len(new_reqs[rid]['req'].formalizations) == 0 and len(old_reqs[rid]['req'].formalizations) == 0:
            pass
        elif len(new_reqs[rid]['req'].formalizations) == 0 and len(old_reqs[rid]['req'].formalizations) > 0:
            logging.info('Migrate formalization for `{}`'.format(rid))
            new_reqs[rid]['req'].formalizations = old_reqs[rid]['req'].formalizations
            if new_reqs[rid]['req'].description != old_reqs[rid]['req'].description:
                logging.info(
                    'Add `migrated_formalization` tag to `{}`, status to `Todo` since description changed'.format(rid))
                new_reqs[rid]['req'].tags.add(
                    '{}_to_{}_migrated_formalization'.format(base_revision_name, revision_name)
                )
                new_reqs[rid]['req'].status = 'Todo'
        elif len(new_reqs[rid]['req'].formalizations) == 0 and len(old_reqs[rid]['req'].formalizations) > 0:
            logging.error('Parsing of the requirement not supported.')
            raise NotImplementedError

        new_reqs[rid]['req'].revision_diff = old_reqs[rid]['req']

    # Store the updated requirements for the new revision.
    logging.info('Store merge changes to revision `{}`'.format(revision_name))
    for r in new_reqs.values():
        r['req'].store(r['path'])

    # Store the variables collection in the new revision.
    logging.info('Migrate variables from `{}` to `{}`'.format(base_revision_name, revision_name))
    base_var_collection = VariableCollection.load(base_revision_var_collectioin_path)
    base_var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])


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


def user_request_new_revision(args):
    """ Asks the user about the base revision and triggers create_revision with the user choice.

    :param args:
    """
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
    base_revision_choice = choice(available_revisions, 'revision_0')
    create_revision(args, base_revision_choice)


def set_session_config_vars(args, HERE):
    """ Initialize variables for current session.

    :param args: Parsed arguments.
    """
    app.config['SESSION_TAG'] = args.tag
    if app.config['SESSION_BASE_FOLDER'] is None:
        app.config['SESSION_FOLDER'] = os.path.join(HERE, 'data', app.config['SESSION_TAG'])
    else:
        app.config['SESSION_FOLDER'] = os.path.join(app.config['SESSION_BASE_FOLDER'], app.config['SESSION_TAG'])


def init_var_collection():
    """ Creates a new empty VariableCollection if non is existent for current session.

    """
    if not os.path.exists(app.config['SESSION_VARIABLE_COLLECTION']):
        var_collection = VariableCollection(path=app.config['SESSION_VARIABLE_COLLECTION'])
        var_collection.store()


def init_import_sessions():
    # Check for Import sessions
    var_import_sessions_path = os.path.join(app.config['SESSION_BASE_FOLDER'], 'variable_import_sessions.pickle')
    try:
        VarImportSessions.load(var_import_sessions_path)
    except FileNotFoundError:
        var_import_sessions = VarImportSessions(path=var_import_sessions_path)
        var_import_sessions.store()


def init_meta_settings():
    """ Initializes META_SETTTINGS_PATH and creates a new meta_settings dict, if none is existent.

    """
    app.config['META_SETTTINGS_PATH'] = os.path.join(app.config['SESSION_FOLDER'], 'meta_settings.pickle')
    if not os.path.exists(app.config['META_SETTTINGS_PATH']):
        meta_settings = dict()
        meta_settings['tag_colors'] = dict()
        pickle_dump_obj_to_file(meta_settings, app.config['META_SETTTINGS_PATH'])


def init_frontend_logs():
    """ Initializes FRONTEND_LOGS_PATH and creates a new frontend_logs dict, if none is existent.

        """
    app.config['FRONTEND_LOGS_PATH'] = os.path.join(app.config['SESSION_FOLDER'], 'frontend_logs.pickle')
    if not os.path.exists(app.config['FRONTEND_LOGS_PATH']):
        frontend_logs = dict()
        frontend_logs['hanfor_log'] = list()
        pickle_dump_obj_to_file(frontend_logs, app.config['FRONTEND_LOGS_PATH'])


def user_choose_start_revision():
    """ Asks the user which revision should be loaded if there is more than one revision.
    :rtype: str
    :return: revision name
    """
    available_revisions = utils.get_available_revisions(app.config)
    revision_choice = 'revision_0'
    # Start the first revision if there is only one.
    if len(available_revisions) == 1:
        revision_choice = available_revisions[0]
    # If there is no revision it means probably that this is an old hanfor version.
    # ask the user to migrate.
    elif len(available_revisions) == 0:
        print('No revisions found. You might use a deprecated session version without revision support.')
        print('Is that true and should I migrate this session?')
        migrate_session = choice(['yes', 'no'], 'no')
        if migrate_session == 'yes':
            file_paths = [
                path for path in get_filenames_from_dir(app.config['SESSION_FOLDER'])
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
        revision_choice = choice(available_revisions, available_revisions[-1])
    return revision_choice


def set_app_config_paths(args, HERE):
    app.config['SCRIPT_UTILS_PATH'] = os.path.join(HERE, 'script_utils')
    app.config['TEMPLATES_FOLDER'] = os.path.join(HERE, 'templates')


def startup_hanfor(args, HERE):
    """ Setup session Variables and parse startup arguments

    :param args:
    """
    set_session_config_vars(args, HERE)
    set_app_config_paths(args, HERE)

    # Create a new revision if requested.
    if args.revision:
        user_request_new_revision(args)
    else:
        # If there is no session with given tag: Create a new (initial) revision.
        if not os.path.exists(app.config['SESSION_FOLDER']):
            create_revision(args, None)
        # If this is a already existing session, ask the user which revision to start.
        else:
            revision_choice = user_choose_start_revision()
            logging.info('Loading session `{}` at `{}`'.format(app.config['SESSION_TAG'], revision_choice))
            load_revision(revision_choice)

    # Set used csv entry into config.
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])  # type: dict
    app.config['CSV_INPUT_FILE'] = os.path.basename(session_dict['csv_input_file'])
    app.config['CSV_INPUT_FILE_path'] = session_dict['csv_input_file']

    # Initialize variables collection, import session, meta settings.
    init_var_collection()
    init_import_sessions()
    init_meta_settings()
    init_frontend_logs()

    # Run version migrations
    varcollection_version_migrations(app, args)
    requirements_version_migrations(app, args)

    # Run consistency checks.
    varcollection_consistency_check(app, args)


def fetch_hanfor_version():
    """ Get `git describe --always --tags` and store to HANFOR_VERSION

    """
    try:
        app.config['HANFOR_VERSION'] = subprocess.check_output(
            ['git', 'describe', '--always', '--tags']).decode("utf-8").strip()
        app.config['HANFOR_COMMIT_HASH'] = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD']).decode("utf-8").strip()
    except Exception as e:
        logging.info('Could not get Hanfor version. Is git installed and Hanfor run from its repo?: {}'.format(e))
        app.config['HANFOR_VERSION'] = '?'
        app.config['HANFOR_COMMIT_HASH'] = '?'


def get_app_options():
    """ Returns Flask runtime options.

    :rtype: dict
    """
    app_options = {
        'host': app.config['HOST'],
        'port': app.config['PORT']
    }

    if app.config['PYCHARM_DEBUG']:
        app_options["debug"] = False
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    return app_options


if __name__ == '__main__':
    utils.setup_logging(app)
    app.wsgi_app = utils.PrefixMiddleware(app.wsgi_app, prefix=app.config['URL_PREFIX'])
    HERE = os.path.dirname(os.path.realpath(__file__))

    app.debug = app.config['DEBUG_MODE']
    if app.config['DEBUG_MODE']:
        toolbar = DebugToolbarExtension(app)

    fetch_hanfor_version()
    utils.register_assets(app)

    # Parse python args and startup hanfor session.
    args = utils.HanforArgumentParser(app).parse_args()
    startup_hanfor(args, HERE)

    # Run the app
    app.run(**get_app_options())
