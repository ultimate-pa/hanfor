""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import argparse
from typing import Union, Set

from copy import deepcopy
from flask import json

import boogie_parsing
import csv
import datetime
import html
import itertools
import logging
import pickle
import random
import re
import shlex
import os

from colorama import Fore, Style
from flask_assets import Bundle, Environment

from reqtransformer import VarImportSessions, VariableCollection
from svm_pattern_classifier import SvmPatternClassifier
from terminaltables import DoubleTable

here = os.path.dirname(os.path.realpath(__file__))
default_scope_options = '''
    <option value="NONE">None</option>
    <option value="GLOBALLY">Globally</option>
    <option value="BEFORE">Before "{P}"</option>
    <option value="AFTER">After "{P}"</option>
    <option value="BETWEEN">Between "{P}" and "{Q}"</option>
    <option value="AFTER_UNTIL">After "{P}" until "{Q}"</option>
    '''
default_pattern_options = '''
    <option value="NotFormalizable">None</option>
    <optgroup label="Occurence">
    <option value="Invariant">it is always the case that if "{R}" holds, then "{S}"
        holds as well</option>
    <option value="Absence">it is never the case that "{R}" holds</option>
    <option value="Universality">it is always the case that "{R}" holds</option>
    <option value="Existence">"{R}" eventually holds</option>
    <option value="BoundedExistence">transitions to states in which "{R}" holds
        occur at most twice</option>
    </optgroup>
    <optgroup label="Order">
    <option value="Precedence">it is always the case that if "{R}" holds then "{S}"
        previously held</option>
    <option value="PrecedenceChain1-2">it is always the case that if "{R}" holds
        and is succeeded by "{S}", then "{T}" previously held</option>
    <option value="PrecedenceChain2-1">it is always the case that if "{R}" holds then "{S}"
        previously held and was preceded by "{T}"</option>
    <option value="Response">it is always the case that if "{R}" holds then "{S}"
        eventually holds</option>
    <option value="ResponseChain1-2">it is always the case that if "{R}" holds then "{S}"
        eventually holds and is succeeded by "{T}"</option>
    <option value="ResponseChain2-1">it is always the case that if "{R}" holds and is
        succeeded by "{S}", then "{T}" eventually holds after "{S}"</option>
    <option value="ConstrainedChain">it is always the case that if "{R}" holds then "{S}"
        eventually holds and is succeeded by "{T}", where "{U}" does not hold between "{S}" and "{T}"</option>
    </optgroup>
    <optgroup label="Real-time">
    <option value="MinDuration">it is always the case that once "{R}" becomes satisfied,
        it holds for at least "{S}" time units</option>
    <option value="MaxDuration">it is always the case that once "{R}" becomes satisfied,
        it holds for less than "{S}" time units</option>
    <option value="BoundedRecurrence">it is always the case that "{R}" holds at least every
        "{S}" time units</option>
    <option value="BoundedResponse">it is always the case that if "{R}" holds, then "{S}"
        holds after at most "{T}" time units</option>
    <option value="BoundedInvariance">it is always the case that if "{R}" holds, then "{S}"
        holds for at least "{T}" time units</option>
    <option value="TimeConstrainedMinDuration">it is always the case that if {R} holds for at least {S} time units,
        then {T} holds afterwards for at least {U} time units</option>
    <option value="TimeConstrainedInvariant">it is always the case that if {R} holds for at least {S} time units,
        then {T} holds afterwards</option>
    <option value="ConstrainedTimedExistence">it is always the case that if {R} holds,
        then {S} holds after at most {T} time units for at least {U} time units</option>
    <option value="Toggle1">it is always the case that if {R} holds then {S} toggles {T}</option>
    <option value="Toggle2">it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later</option>
    </optgroup>
    <optgroup label="not_formalizable">
    <option value="NotFormalizable">// not formalizable</option>
    </optgroup>
    '''


def pickle_dump_obj_to_file(obj, filename):
    """ Pickle-dumps given object to file.

    :param obj: Python object
    :type obj: object
    :param filename: Path to output file
    :type filename: str
    """
    with open(filename, mode='wb') as out_file:
        pickle.dump(obj, out_file)


def pickle_load_from_dump(filename):
    """ Loads python object from pickle dump file.

    :param filename: Path to the pickle dump
    :type filename: str
    :return: Object dumped in file
    :rtype: object
    """
    if os.path.getsize(filename) > 0:
        with open(filename, mode='rb') as f:
            return pickle.load(f)


def get_filenames_from_dir(input_dir):
    """ Returns the list of filepaths for all files in input_dir.

    :param input_dir: Location of the input directory
    :type input_dir: str
    :return: List of file locations [<input_dir>/<filename>, ...]
    :rtype: list
    """
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]


def load_requirement_by_id(id, app):
    """ Loads requirement from session folder if it exists.

    :param id: requirement_id
    :type id: str
    :param app: The flask app.
    :rtype: Requirement
    """
    filepath = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(id))
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return pickle_load_from_dump(filepath)
    logging.info('Requirement `{}` at `{}` not found'.format(id, filepath))


def get_formalization_template(templates_folder, requirement, formalization_id, formalization):
    result = {'success': True}

    result['html'] = formalization_html(
        templates_folder,
        formalization_id,
        default_scope_options,
        default_pattern_options,
        formalization
    )

    return result


def formalization_html(templates_folder, formalization_id, scope_options, pattern_options, formalization):
    # Load template.
    html_template = ''
    with open(os.path.join(templates_folder, 'formalization.html'), mode='r') as f:
        html_template += '\n'.join(f.readlines())

    # Set values
    html_template = html_template.replace('__formalization_text__', formalization.get_string())
    html_template = html_template.replace('__formal_id__', '{}'.format(formalization_id))
    form_desc = formalization.get_string()
    if len(form_desc) < 10:  # Add hint to open if desc is short.
        form_desc += '... (click to open)'
    html_template = html_template.replace('__formal_desc__', form_desc)

    # Selected scope and pattern:
    if formalization.scoped_pattern is not None:
        scope = formalization.scoped_pattern.get_scope_slug()
        pattern = formalization.scoped_pattern.get_pattern_slug()
        scope_options = scope_options.replace('value="{}"'.format(scope), 'value="{}" selected'.format(scope))
        pattern_options = pattern_options.replace('value="{}"'.format(pattern), 'value="{}" selected'.format(pattern))
    html_template = html_template.replace('__scope_options__', scope_options)
    html_template = html_template.replace('__pattern__options__', pattern_options)

    # Expressions
    for key, value in formalization.expressions_mapping.items():
        html_template = html_template.replace(
            '__expr_{}_content__'.format(key), '{}'.format(html.escape(str(value.raw_expression))))

    # Unset remaining vars.
    html_template = re.sub(r'__expr_._content__', '', html_template)

    return html_template


def store_requirement(requirement, app):
    """ Store a requirement.

    :param requirement: requirement to store
    :type requirement: Requirement
    :param app: The flask app.
    :type app:
    """
    filepath = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(requirement.rid))
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return pickle_dump_obj_to_file(requirement, filepath)


def formalizations_to_html(app, formalizations):
    result = ''
    for index, formalization in formalizations.items():
        result += formalization_html(
            app.config['TEMPLATES_FOLDER'],
            index,
            default_scope_options,
            default_pattern_options,
            formalization
        )
    return result


def choice(choices, default):
    """ Asks the user which string he wants from a list of strings.
    Returns the selected string.

    :param choices: List of choices (one choice is a string)
    :type choices: list
    :param default: One element from the choices list.
    :type default: str
    :return: The choice selected by the user.
    :rtype: str
    """
    idx = 0
    data = list()
    for choice in choices:
        if choice == default:
            data.append([
                '{}-> {}{}'.format(Fore.GREEN, idx, Style.RESET_ALL),
                '{}{}{}'.format(Fore.GREEN, choice, Style.RESET_ALL)
            ])
        else:
            data.append([idx, choice])
        idx = idx + 1

    table = DoubleTable(data, title='Choices')
    table.inner_heading_row_border = False
    print(table.table)

    while True:
        last_in = input('{}[Choice or Enter for {} -> default{}]> {}'.format(
            Fore.LIGHTBLUE_EX,
            Fore.GREEN,
            Fore.LIGHTBLUE_EX,
            Style.RESET_ALL))

        if len(last_in) == 0:
            return default

        choice, *args = shlex.split(last_in)
        if len(args) > 0:
            print('What did you mean?')
            continue

        try:
            choice = int(choice)
        except ValueError:
            print('Illegal choice "' + str(choice) + '", choose again')
            continue

        if choice >= 0 and choice < idx:
            return choices[choice]

        print('Illegal choice "' + str(choice) + '", choose again')


def get_available_vars(app, full=True):
    var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    result = var_collection.get_available_vars_list(used_only=not full)

    return result


def varcollection_diff_info(app, request):
    """ Collect diff info of current and requested var collection.
        * Number of var in the requested var collection
        * Number of new vars in the requested var collection.


    :param request: API request
    :return: {'tot_vars': int, 'new_vars': int}
    :rtype: dict
    """
    current_var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    req_path = os.path.join(
        app.config['SESSION_BASE_FOLDER'],
        request.form.get('sess_name').strip(),
        request.form.get('sess_revision').strip(),
        'session_variable_collection.pickle'
    )
    requested_var_collection = pickle_load_from_dump(req_path)

    numb_new_vars = len(
        set(requested_var_collection.collection.keys()).difference(current_var_collection.collection.keys())
    )

    result = {
        'tot_vars': len(requested_var_collection.collection),
        'new_vars': numb_new_vars
    }

    return result


def varcollection_create_new_import_session(app, source_session_name, source_revision_name):
    """ Creates a new blank variable collection import session.
    Returns the associated session_id or -1 if the creation fails.

    :param app: Current flask app.
    :param source_session_name:
    :param source_revision_name:
    """
    current_var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    source_var_collection_path = os.path.join(
        app.config['SESSION_BASE_FOLDER'],
        source_session_name,
        source_revision_name,
        'session_variable_collection.pickle'
    )
    source_var_collection = VariableCollection.load(source_var_collection_path)

    # load import_sessions
    var_import_sessions_path = os.path.join(app.config['SESSION_BASE_FOLDER'], 'variable_import_sessions.pickle')
    try:
        var_import_sessions = VarImportSessions.load(var_import_sessions_path)
    except FileNotFoundError:
        var_import_sessions = VarImportSessions(path=var_import_sessions_path)
        var_import_sessions.store()

    session_id = var_import_sessions.create_new_session(
        source_collection=source_var_collection,
        target_collection=current_var_collection
    )

    return session_id


def get_available_tags(app):
    """ Returns a list of all available tags.
    One list entry is: {
        'name': <tag_name>
        'used_by': [rids of requirement using this tag]
    }

    :rtype: list
    """
    # For each requirement:

    filenames = get_filenames_from_dir(app.config['REVISION_FOLDER'])
    collected_tags = dict()
    meta_settings = MetaSettings(app.config['META_SETTTINGS_PATH'])

    def get_color(tag_name):
        col = '#5bc0de'
        try:
            col = meta_settings['tag_colors'][tag_name]
        except KeyError:
            pass
        return col

    for filename in filenames:
        req = pickle_load_from_dump(filename)
        if type(req).__name__ == 'Requirement':
            for tag in req.tags:
                if len(tag) == 0:
                    continue
                if tag not in collected_tags.keys():
                    collected_tags[tag] = {
                        'name': tag,
                        'used_by': list(),
                        'color': get_color(tag)
                    }
                collected_tags[tag]['used_by'].append(req.rid)

    return [tag for tag in collected_tags.values()]


def update_req_search(app, request, delete=False):
    """ Update a search query.
    A search query will be used as presets for requirements search in the frontend.

    :param delete: If true remove the search query
    """
    search_query = request.form.get('query', '').strip()

    result = {
        'success': True
    }

    if len(search_query) > 0:
        meta_settings = MetaSettings(app.config['META_SETTTINGS_PATH'])
        if not delete:
            # Store the search query into meta settings.
            if 'available_search_strings' not in meta_settings:
                meta_settings['available_search_strings'] = list()
            meta_settings['available_search_strings'].append(search_query)
        elif search_query in meta_settings['available_search_strings']:
            # delete query.
            meta_settings['available_search_strings'].remove(search_query)
        meta_settings.update_storage()

    return result

def update_tag(app, request, delete=False):
    """ Update a tag.
    The request should contain a form:
        name -> the new tag name
        name_old -> the name of the tag before.
        occurences -> Ids of requirements using this tag.

        :param delete: Should the tag be just deleted? (Default false).
        :type delete: bool
        :param app: the running flask app
        :type app: Flask
        :param request: A form request
        :type request: flask.Request
        :return: Dictionary containing changed data and request status information.
        :rtype: dict
        """

    # Get properties from request
    tag_name = request.form.get('name', '').strip()
    tag_name_old = request.form.get('name_old', '').strip()
    occurences = request.form.get('occurences', '').strip().split(',')
    color = request.form.get('color', '#5bc0de').strip()  # Default = #5bc0de

    result = {
        'success': True,
        'has_changes': False,
        'rebuild_table': False,
        'data': {
            'name': tag_name,
            'used_by': occurences,
            'color': color
        }
    }

    # Delete the tag.
    if delete:
        logging.info('Delete Tag `{}`'.format(tag_name_old, tag_name))
        result['has_changes'] = True

        if len(occurences) > 0:
            result['rebuild_table'] = True
            for rid in occurences:
                filepath = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(rid))
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    requirement = pickle_load_from_dump(filepath)
                    logging.info('Delete tag `{}` in requirement `{}`'.format(tag_name, requirement.rid))
                    requirement.tags.discard(tag_name)
                    store_requirement(requirement, app)
    # Rename the tag.
    elif tag_name_old != tag_name:
        logging.info('Update Tag `{}` to new name `{}`'.format(tag_name_old, tag_name))
        result['has_changes'] = True

        if len(occurences) > 0:
            # Todo: only rebuild if we have a merge.
            result['rebuild_table'] = True
            for rid in occurences:
                filepath = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(rid))
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    requirement = pickle_load_from_dump(filepath)
                    logging.info('Update tags in requirement `{}`'.format(requirement.rid))
                    requirement.tags.discard(tag_name_old)
                    requirement.tags.add(tag_name)
                    store_requirement(requirement, app)

    # Store the color into meta settings.
    meta_settings = MetaSettings(app.config['META_SETTTINGS_PATH'])
    if 'tag_colors' not in meta_settings:
        meta_settings['tag_colors'] = dict()
    meta_settings['tag_colors'][tag_name] = color
    meta_settings.update_storage()

    return result


def update_variable_in_collection(app, request):
    """ Update a single variable. The request should contain a form:
        name -> the new name of the var.
        name_old -> the name of the var before.
        type -> the new type of the var.
        type_old -> the old type of the var.
        occurences -> Ids of requirements using this variable.

    :param app: the running flask app
    :type app: Flask
    :param request: A form request
    :type request: flask.Request
    :return: Dictionary containing changed data and request status information.
    :rtype: dict
    """
    # Get properties from request
    var_name = request.form.get('name', '').strip()
    var_name_old = request.form.get('name_old', '').strip()
    var_type = request.form.get('type', '').strip()
    var_type_old = request.form.get('type_old', '').strip()
    var_const_val = request.form.get('const_val', '').strip()
    var_const_val_old = request.form.get('const_val_old', '').strip()
    occurrences = request.form.get('occurrences', '').strip().split(',')
    enumerators = json.loads(request.form.get('enumerators', ''));

    var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    result = {
        'success': True,
        'has_changes': False,
        'type_changed': False,
        'name_changed': False,
        'rebuild_table': False,
        'data': {
            'name': var_name,
            'type': var_type,
            'used_by': occurrences,
            'const_val': var_const_val
        }
    }

    # Check for changes
    if (var_type_old != var_type
        or var_name_old != var_name
        or var_const_val_old != var_const_val
            or request.form.get('updated_constraints') == 'true'):
        logging.info('Update Variable `{}`'.format(var_name_old))
        result['has_changes'] = True
        reload_type_inference = False

        # Update type.
        if var_type_old != var_type:
            logging.info('Change type from `{}` to `{}`.'.format(var_type_old, var_type))
            var_collection.collection[var_name_old].type = var_type
            result['type_changed'] = True
            reload_type_inference = True

        # Update constraints.
        if request.form.get('updated_constraints') == 'true':
            constraints = json.loads(request.form.get('constraints', ''))
            logging.debug('Update Variable Constraints')
            try:
                var_collection = var_collection.collection[var_name_old].update_constraints(
                    constraints,
                    app,
                    var_collection
                )
                result['rebuild_table'] = True
            except KeyError as e:
                result['success'] = False
                result['error_msg'] = 'Could not set constraint: Missing expression/variable for {}'.format(e)
            except Exception as e:
                result['success'] = False
                result['error_msg'] = 'Could not parse formalization: `{}`'.format(e)
        else:
            logging.debug('Skipping variable Constraints update.')

        # update name.
        if var_name_old != var_name:
            logging.debug('Change name of var `{}` to `{}`'.format(var_name_old, var_name))
            #  Case: New name which does not exist -> remove the old var and replace in reqs ocurring.
            if var_name not in var_collection:
                logging.debug('`{}` is a new var name. Rename the var, replace occurences.'.format(
                    var_name
                ))
                # Rename the var (Copy to new name and remove the old item. Rename it)
                var_collection.rename(var_name_old, var_name, app)

            else:  # Case: New name exists. -> Merge the two vars into one. -> Complete rebuild.
                if var_collection.collection[var_name_old].type != var_collection.collection[var_name].type:
                    result['success'] = False
                    result['errormsg'] = 'To merge two variables the types must be identical. {} != {}'.format(
                        var_collection.collection[var_name_old].type,
                        var_collection.collection[var_name].type
                    )
                    return result
                logging.debug('`{}` is an existing var name. Merging the two vars. '.format(var_name))
                # var_collection.merge_vars(var_name_old, var_name, app)
                var_collection.rename(var_name_old, var_name, app)
                result['rebuild_table'] = True
                reload_type_inference = True

            # delete the old.
            # Update the requirements using this var.
            if len(occurrences) > 0:
                rename_variable_in_expressions(app, occurrences, var_name_old, var_name)

            result['name_changed'] = True

        # Update const value.
        if var_const_val_old != var_const_val:
            logging.info('Change value from `{}` to `{}`.'.format(var_const_val_old, var_const_val))
            var_collection.collection[var_name].value = var_const_val
            result['val_changed'] = True

        logging.info('Store updated variables.')
        var_collection.refresh_var_constraint_mapping()
        var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
        logging.info('Update derived types by parsing affected formalizations.')
        if reload_type_inference and var_name in var_collection.var_req_mapping:
            for rid in var_collection.var_req_mapping[var_name]:
                requirement = load_requirement_by_id(rid, app)
                if requirement:
                    requirement.reload_type_inference(var_collection, app)

    if var_type == 'ENUM':
        for enumerator_name, enumerator_value in enumerators:
            if len(enumerator_name) == 0 and len(enumerator_value) == 0:
                continue
            if len(enumerator_name) == 0 or not re.match('^[a-zA-Z0-9_-]+$', enumerator_name):
                result = {
                    'success': False,
                    'errormsg': 'Enumerator name `{}` not valid'.format(enumerator_name)
                }
                break
            try:
                int(enumerator_value)
            except:
                result = {
                    'success': False,
                    'errormsg': 'Enumerator value `{}` for enumerator `{}` not valid'.format(
                        enumerator_value, enumerator_name
                    )
                }
                break

            enumerator_name = '{}_{}'.format(var_name, enumerator_name)
            # Add new enumerators to the var_collection
            if not var_collection.var_name_exists(enumerator_name):
                var_collection.add_var(enumerator_name)

            var_collection.collection[enumerator_name].type = 'ENUMERATOR'
            var_collection.collection[enumerator_name].value = enumerator_value

        var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])

    return result


def rename_variable_in_expressions(app, occurences, var_name_old, var_name):
    """ Updates (replace) the variables in the requirement expressioins.

    :param app: Flask app (used for session).
    :type app: Flask
    :param occurences: Requirement ids to be taken into account.
    :type occurences: list (of str)
    :param var_name_old: The current name in the expressions.
    :type var_name_old: str
    :param var_name: The new name.
    :type var_name: str
    """
    logging.debug('Update requirements using old var `{}` to `{}`'.format(var_name_old, var_name))
    for rid in occurences:
        filepath = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(rid))
        if os.path.exists(filepath) and os.path.isfile(filepath):
            requirement = pickle_load_from_dump(filepath)  # type: Requirement
            # replace in every formalization
            for index, formalization in requirement.formalizations.items():
                for key, expression in formalization.expressions_mapping.items():
                    if var_name_old not in expression.raw_expression:
                        continue
                    new_expression = boogie_parsing.replace_var_in_expression(
                        expression=expression.raw_expression,
                        old_var=var_name_old,
                        new_var=var_name
                    )
                    requirement.formalizations[index].expressions_mapping[key].raw_expression = new_expression
                    requirement.formalizations[index].expressions_mapping[key].used_variables.discard(var_name_old)
                    requirement.formalizations[index].expressions_mapping[key].used_variables.add(var_name)
            logging.debug('Updated variables in requirement id: `{}`.'.format(requirement.rid))
            store_requirement(requirement, app)


def rename_variable_in_constraints(app, occurences, var_name_old, var_name, variable_collection):
    """ Renames the variable in

    :param app:
    :param occurences:
    :param var_name_old:
    :param var_name:
    :param variable_collection:
    """
    if var_name_old in variable_collection.collection.keys():
        pass



def get_statistics(app):
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
    requirement_filenames = get_filenames_from_dir(app.config['REVISION_FOLDER'])
    # Gather requirements statistics
    for requirement_filename in requirement_filenames:
        requirement = pickle_load_from_dump(requirement_filename)
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
    var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
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

    return data


def get_requirements(input_dir, filter_list=None, invert_filter=False):
    """ Load all requirements from session folder and return in a list.

    :param tag: Session tag
    :type tag: str
    :param filter: A list of requirement IDs to be included in the result. All if not set.
    :type filter: list (of strings)
    :param invert_filter: Exclude filter
    :type invert_filter: bool
    """
    filenames = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    ]
    filenames.sort()
    requirements = list()

    def should_be_in_result(req) -> bool:
        if filter_list is None:
            return True
        return (req.rid in filter_list) != invert_filter

    for filename in filenames:
        req = pickle_load_from_dump(filename)  # type: Requirement
        if hasattr(req, 'rid'):
            if should_be_in_result(req):
                logging.debug('Adding {} to results.'.format(req.rid))
                requirements.append(req)

    return requirements


def generate_csv_file(app, output_file=None, filter_list=None, invert_filter=False):
    """ Generates the csv file for a session by tag.

    :param tag: Session tag
    :type tag: str
    :param output_file: Where to store the file
    :type output_file: str
    :param filter: A list of requirement IDs to be included in the result. All if not set.
    :type filter: list (of strings)
    :param invert_filter: Exclude filter
    :type invert_filter: bool
    :return: Output file location on success.
    :rtype: str
    """
    # Get requirements
    tag_col_name = 'Hanfor_Tags'
    requirements = get_requirements(app.config['REVISION_FOLDER'], filter_list=filter_list, invert_filter=invert_filter)

    # get session status
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])  # type: dict

    # Generate Output filename.
    if not output_file:
        output_file = os.path.join(app.config['SESSION_FOLDER'], '{}_{}_out.csv'.format(
            app.config['SESSION_TAG'],
            app.config['USING_REVISION']
        ))

    # Add Formalization col if not existent in input CSV.
    for csv_key in [session_dict['csv_formal_header']]:
        if csv_key not in session_dict['csv_fieldnames']:
            session_dict['csv_fieldnames'].append(csv_key)

    # Add Hanfor Tag col to csv.
    while tag_col_name in session_dict['csv_fieldnames']:
        tag_col_name += '_1'
    session_dict['csv_fieldnames'].append(tag_col_name)

    # Collect data.
    for requirement in requirements:
        requirement.csv_row[session_dict['csv_formal_header']] = requirement.get_formalization_string()
        requirement.csv_row[tag_col_name] = ', '.join(requirement.tags)

    # Write data to file.
    rows = [r.csv_row for r in requirements]
    with open(output_file, mode='w') as out_csv:
        csv.register_dialect('ultimate', delimiter=',')
        writer = csv.DictWriter(out_csv, session_dict['csv_fieldnames'], dialect=session_dict['csv_dialect'])
        writer.writeheader()
        writer.writerows(rows)

    return output_file


def clean_identifier_for_ultimate_parser(slug: str, used_slugs: Set[str]) -> (str, Set[str]):
    """ Clean slug to be sound for ultimate parser.

    :param slug: The slug to be cleaned.
    :param used_slugs: Set of already used slugs.
    :return: (save_slug, used_slugs) save_slug a save to use form of slug. save_slug added to used_slugs.
    """
    # Replace any occurence of [whitespace, `.`, `-`] with `_`
    slug = re.sub(r"[\s+.-]+", '_', slug.strip())

    # Resolve illegal start
    slug = re.sub(r"^[^a-zA-Z]", 'ID_', slug)

    # Resolve duplicates
    # search for the first free suffix.
    if slug in used_slugs:
        suffix = 1
        pad = lambda s: '{}_{}'.format(slug, s)
        while pad(suffix) in used_slugs:
            suffix += 1
        slug = pad(suffix)

    used_slugs.add(slug)

    return slug, used_slugs


def generate_req_file(app, output_file=None, filter_list=None, invert_filter=False):
    """ Generate the ulltimate requirements file.

    :param tag: Session tag
    :type tag: str
    :type output_file: str
    :param filter: A list of requirement IDs to be included in the result. All if not set.
    :type filter: list (of strings)
    :param invert_filter: Exclude filter
    :type invert_filter: bool
    :return: Output file location on success.
    :rtype: str
    """
    logging.info('Generating .req file for session {}'.format(app.config['SESSION_TAG']))
    # Get requirements
    requirements = get_requirements(app.config['REVISION_FOLDER'], filter_list=filter_list, invert_filter=invert_filter)

    # get session status
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])  # type: dict

    var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    available_vars = []
    if filter_list is not None:
        # Filter the available vars to only include the ones actually used by a requirement.
        logging.info('Filtering the .req file to only include {} selected requirements.'.format(len(filter_list)))
        logging.debug('Only include req.ids: {}.'.format(filter_list))
        target_set = set(filter_list)
        for var in var_collection.get_available_vars_list(sort_by='name'):
            try:
                used_in = var_collection.var_req_mapping[var['name']]
                if used_in & target_set:
                    available_vars.append(var)
            except:
                logging.debug('Ignoring variable `{}`'.format(var))
    else:
        available_vars = var_collection.get_available_vars_list(sort_by='name')

    available_vars = [var['name'] for var in available_vars]

    # Write to .req file
    if not output_file:
        output_file = os.path.join(
            app.config['SESSION_FOLDER'], '{}_{}_formalized_requirements.req'.format(
                app.config['SESSION_TAG'],
                app.config['USING_REVISION']
            ))
    logging.info('Write to output file: {}'.format(output_file))

    content_list = []
    constants_list = []
    constraints_list = []
    with open(output_file, mode='w') as out_file:
        # Parse variables and variable constraints.
        for var in var_collection.collection.values():
            if var.name in available_vars:
                if var.type in ['CONST', 'ENUMERATOR']:
                    constants_list.append('CONST {} IS {}'.format(var.name, var.value))
                else:
                    content_list.append('Input {} IS {}'.format(
                        var.name,
                        boogie_parsing.BoogieType.reverse_alias(var.type).name
                    ))
                try:
                    for index, constraint in var.constraints.items():
                        if constraint.scoped_pattern is None:
                            continue
                        if constraint.scoped_pattern.get_scope_slug().lower() == 'none':
                            continue
                        if constraint.scoped_pattern.get_pattern_slug() in ['NotFormalizable', 'None']:
                            continue
                        if len(constraint.get_string()) == 0:
                            continue
                        constraints_list.append('Constraint_{}_{}: {}'.format(
                            re.sub(r"\s+", '_', var.name),
                            index,
                            constraint.get_string()
                        ))
                except:
                    pass
        content_list.sort()
        constants_list.sort()
        constraints_list.sort()

        content = '\n'.join(content_list)
        constants = '\n'.join(constants_list)
        constraints = '\n'.join(constraints_list)

        if len(constants) > 0:
            content = '\n\n'.join([constants, content])
        if len(constraints) > 0:
            content = '\n\n'.join([content, constraints])
        content += '\n\n'

        # parse requirement formalizations.
        used_slugs = set()
        for requirement in requirements:  # type: Requirement
            try:
                for index, formalization in requirement.formalizations.items():
                    slug, used_slugs = clean_identifier_for_ultimate_parser(requirement.rid, used_slugs)
                    if formalization.scoped_pattern is None:
                        continue
                    if formalization.scoped_pattern.get_scope_slug().lower() == 'none':
                        continue
                    if formalization.scoped_pattern.get_pattern_slug() in ['NotFormalizable', 'None']:
                        continue
                    if len(formalization.get_string()) == 0:
                        # formalizatioin string is empty if expressions are missing or none set. Ignore in output
                        continue
                    content += '{}_{}: {}\n'.format(
                        slug,
                        index,
                        formalization.get_string()
                    )
            except AttributeError:
                continue
        content += '\n'
        out_file.write(content)

    return output_file


def get_stored_session_names(session_folder=None, only_names=False, with_revisions=False) -> tuple:
    """ Get stored session tags (folder names) including os.stat.
    Returned tuple is (
        (os.stat(), name),
        ...
    )
    If only_names == True the tuple is (
        name_1,
        ...
    )
    If with_with_revisions == True the tuple is (
        {
            name: 'name_1',
            'revisions': [revision_1, ...],
            revisions_stats: {
                revision_1: {
                    name: 'revision_1',
                    last_mod: "%A %d. %B %Y at %X" formatted mtime,
                    num_vars: Number of variables used in this revision.
                }
            }
        },
        ...
    )

    :param session_folder: path to folder
    :type session_folder: str
    :return: tuple  of folder names or stats with names
    :rtype: tuple
    """
    result = ()
    if not session_folder:
        session_folder = os.path.join(here, 'data')

    try:
        result = [
            (os.path.join(session_folder, file_name), file_name)
            for file_name in os.listdir(session_folder)
            if os.path.isdir(os.path.join(session_folder, file_name))
        ]
        if with_revisions:
            result = (
                {
                    'name': entry[1],
                    'revisions': get_available_revisions(None, entry[0]),
                    'revisions_stats': get_revisions_with_stats(entry[0])
                } for entry in result
            )
        elif only_names:
            result = (entry[1] for entry in result)
        else:
            result = ((os.stat(entry[0]), entry[1]) for entry in result)
    except Exception as e:
        logging.error('Could not fetch stored sessions: {}'.format(e))

    return result


def get_revisions_with_stats(session_path):
    """ Get meta information about available revisions for a given session path.

    Returns a dict with revision name as key for each revision.
    Each item is then a dict like:
        {
            name: 'revision_1',
            last_mod: %A %d. %B %Y at %X formatted mtime,
            num_vars: 9001
        }


    :param session_path: { revision_1: { name: 'revision_1', last_mod: %A %d. %B %Y at %X, num_vars: 9001} ... }
    """
    revisions = get_available_revisions(None, session_path)
    revisions_stats = dict()
    for revision in revisions:
        revision_path = os.path.join(session_path, revision)
        revision_var_collection_path = os.path.join(
            revision_path,
            'session_variable_collection.pickle'
        )
        try:
            num_vars = len(pickle_load_from_dump(revision_var_collection_path).collection)
        except:
            num_vars = -1

        revisions_stats[revision] = {
            'name': revision,
            'last_mod': get_last_edit_from_path(revision_path),
            'num_vars': num_vars
        }
    return revisions_stats


def get_last_edit_from_path(path_str):
    """ Return a human readable form of the last edit (mtime) for a path.

    :param path_str: str to path.
    :return: "%A %d. %B %Y at %X" formatted mtime
    """
    return datetime.datetime.fromtimestamp(os.stat(path_str).st_mtime).strftime("%A %d. %B %Y at %X")


def get_available_revisions(config, folder=None):
    """ Returns available revisions for a given session folder.
    Uses config['SESSION_FOLDER'] if no explicit folder is given.

    :param config:
    :param folder:
    :return:
    """
    result = []

    if folder is None:
        folder = config['SESSION_FOLDER']

    try:
        names = os.listdir(folder)
        result = [name for name in names if os.path.isdir(os.path.join(folder, name))]
    except Exception as e:
        logging.error('Could not fetch stored revisions: {}'.format(e))

    return result


def enable_logging(log_level=logging.ERROR, to_file=False, filename='reqtransformer.log'):
    """ Enable Logging.

    :param log_level: Log level
    :type log_level: int
    :param to_file: Wether output should be stored in a file.
    :type to_file: bool
    :param filename: Filename to log to.
    :type filename: str
    """
    if to_file:
        logging.basicConfig(
            format='%(asctime)s: [%(levelname)s]: %(message)s',
            filename=filename,
            level=log_level)
    else:
        logging.basicConfig(
            format='%(asctime)s: [%(levelname)s]: %(message)s',
            level=log_level)
    logging.debug('Enabled logging.')


def setup_logging(app):
    """ Initializes logging with settings from the config.

    """
    if app.config['LOG_LEVEL'] == 'DEBUG':
        log_level = logging.DEBUG
    elif app.config['LOG_LEVEL'] == 'INFO':
        log_level = logging.INFO
    elif app.config['LOG_LEVEL'] == 'WARNING':
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR

    enable_logging(
        log_level=log_level,
        to_file=app.config['LOG_TO_FILE'],
        filename=app.config['LOG_FILE']
    )


def register_assets(app):
    bundles = {
        'css': Bundle(
            'css/bootstrap.css',
            'css/bootstrap-grid.css',
            'css/bootstrap-reboot.css',
            'css/dataTables.bootstrap4.css',
            'css/select.bootstrap4.css',
            'css/tether.css',
            'css/jquery-ui.css',
            'css/bootstrap-tokenfield.css',
            'css/app.css',
            filters='cssutils',
            output='gen/style.css'
        )
    }

    assets = Environment(app)
    assets.register(bundles)


def get_datatable_additional_cols(app):
    offset = 8  # we have 8 fixed cols.
    result = list()
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])  # type: dict

    for index, name in enumerate(session_dict['csv_fieldnames']):
        result.append(
            {
                'target': index + offset,
                'csv_name': 'csv_data.{}'.format(name),
                'table_header_name': 'csv: {}'.format(name)
            }
        )

    return {'col_defs': result}


def add_msg_to_flask_session_log(session, msg, rid=None, rid_list=None, clear=False, max_msg=50) -> None:
    """ Add a log message for the frontend to the flask session.

    :param max_msg: Max number of messages to keep in the log.
    :param rid_list: A list of affected requirement IDs
    :param rid: Affected requirement id
    :param session: The flask session
    :param msg: Log message string
    :param clear: Turncate the logs if set to true (false on default).
    """
    if clear or 'hanfor_log' not in session:
        session['hanfor_log'] = list()

    template = '[{timestamp}] {message}'

    if rid is not None:
        template += ' <a class="req_direct_link" href="#" data-rid="{rid}">{rid}</a>'

    if rid_list is not None:
        template += ','.join([
            ' <a class="req_direct_link" href="#" data-rid="{rid}">{rid}</a>'.format(rid=rid) for rid in rid_list
        ])

    session['hanfor_log'].append(template.format(
            timestamp=datetime.datetime.now(),
            message=msg,
            rid=rid)
    )

    session.modified = True

    # Remove oldest logs until threshold
    while len(session['hanfor_log']) > max_msg:
        session['hanfor_log'].pop(0)


def get_flask_session_log(session, html=False) -> Union[list, str]:
    """ Get the frontent log messages from flask session.

    :param session: The flask session
    :param html: Return formatted html version.
    :return: list of messages or html string in case `html == True`
    """
    result = list()
    if 'hanfor_log' in session:
        result = session['hanfor_log']

    if html:
        tmp = ''
        for msg in result:
            tmp += '<p>{}</p>'.format(msg)
        result = tmp

    return result


def slugify(s):
    """ Normalizes string, converts to lowercase, removes non-alpha characters, and converts spaces to hyphens.

    :param s: string
    :type s: str
    :return: String save for filename
    :rtype: str
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def load_Import_sessions(app):
    """ Open variable import sessions if existing.

    """
    try:
        # load import_sessions
        var_import_sessions_path = os.path.join(
            app.config['SESSION_BASE_FOLDER'],
            'variable_import_sessions.pickle'
        )
        var_import_sessions = VarImportSessions.load(var_import_sessions_path)
    except FileNotFoundError as e:
        logging.info('Import sessions file does not exist.')
        raise e

    return var_import_sessions


class PrefixMiddleware(object):
    ''' Support for url prefixes. '''

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["Sorry, this url does not belong to Hanfor.".encode()]


class ListStoredSessions(argparse.Action):
    """ List available session tags. """

    def __init__(self, option_strings, app, dest, *args, **kwargs):
        self.app = app
        super(ListStoredSessions, self).__init__(
            option_strings=option_strings, dest=dest, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        entries = get_stored_session_names(self.app.config['SESSION_BASE_FOLDER'])
        data = []
        data.append(['Tag', 'Created'])
        for entry in entries:
            date_string = datetime.datetime.fromtimestamp(entry[0].st_mtime).strftime("%A %d. %B %Y at %X")
            data.append([entry[1], date_string])
        print('Stored sessions: ')
        if len(data) > 1:
            print(DoubleTable(data).table)
        else:
            print('No sessions in found.')
        exit(0)


class GenerateScopedPatternTrainingData(argparse.Action):
    """ Generate training data consisting of requirement descriptions with assigned scoped pattern."""
    def __init__(self, option_strings, app, dest, *args, **kwargs):
        self.app = app
        super(GenerateScopedPatternTrainingData, self).__init__(
            option_strings=option_strings, dest=dest, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        # logging.debug(self.app.config)
        entries = get_stored_session_names(self.app.config['SESSION_BASE_FOLDER'])
        result = dict()
        for entry in entries:
            logging.debug('Looking into {}'.format(entry[1]))
            current_session_folder = os.path.join(self.app.config['SESSION_BASE_FOLDER'], entry[1])
            revisions = get_available_revisions(self.app.config, folder=current_session_folder)
            for revision in revisions:
                current_revision_folder = os.path.join(current_session_folder, revision)
                logging.debug('Processing `{}`'.format(current_revision_folder))
                requirements = get_requirements(current_revision_folder)
                logging.debug('Found {} requirements .. fetching the formalized ones.'.format(len(requirements)))
                used_slugs = set()
                for requirement in requirements:
                    try:
                        if len(requirement.description) == 0:
                            continue
                        slug, used_slugs = clean_identifier_for_ultimate_parser(requirement.rid, used_slugs)
                        result[slug] = dict()
                        result[slug]['desc'] = requirement.description
                        for index, formalization in requirement.formalizations.items():
                            if formalization.scoped_pattern is None:
                                continue
                            if formalization.scoped_pattern.get_scope_slug().lower() == 'none':
                                continue
                            if formalization.scoped_pattern.get_pattern_slug() in ['NotFormalizable', 'None']:
                                continue
                            if len(formalization.get_string()) == 0:
                                # formalization string is empty if expressions are missing or none set. Ignore in output
                                continue
                            f_key = 'formalization_{}'.format(index)
                            result[slug][f_key] = dict()
                            result[slug][f_key]['scope'] = formalization.scoped_pattern.get_scope_slug()
                            result[slug][f_key]['pattern'] = formalization.scoped_pattern.get_pattern_slug()
                            result[slug][f_key]['formalization'] = formalization.get_string()
                    except AttributeError:
                        continue
            with open('training_data.json', mode='w', encoding='utf-8') as f:
                json.dump(result, f)
        exit(0)


class HanforArgumentParser(argparse.ArgumentParser):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.add_argument("input_csv", help="Path to the csv to be processed.")
        self.add_argument("tag", help="A tag for the session. Session will be reloaded, if tag exists.")
        self.add_argument(
            "-r", "--revision",
            action="store_true",
            help="Create a new session by updating a existing session with a new csv file."
        )
        self.add_argument(
            "-rti", "--reload_type_inference",
            action="store_true",
            help="Reload the type inference results."
        )
        self.add_argument(
            '-L', '--list_stored_sessions',
            nargs=0,
            help="List the tags of stored sessions..",
            action=ListStoredSessions,
            app=self.app
        )
        self.add_argument(
            '-G', '--generate_scoped_pattern_training_data',
            nargs=0,
            help="Generate training data out of description with assigned scoped pattern.",
            action=GenerateScopedPatternTrainingData,
            app=self.app
        )


class MetaSettings():
    """ Just an auto saving minimal dict. """
    def __init__(self, path):
        self.__dict__ = pickle_load_from_dump(path)  # type: dict
        self.path = path

    def update_storage(self):
        pickle_dump_obj_to_file(self.__dict__, self.path)

    def __contains__(self, item):
        return self.__dict__.__contains__(item)

    def __setitem__(self, key, value):
        self.__dict__.__setitem__(key, value)

    def __getitem__(self, item):
        return self.__dict__.__getitem__(item)
