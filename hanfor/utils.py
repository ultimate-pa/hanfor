""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import argparse
import io
import shutil
from collections import defaultdict
from io import StringIO

import boogie_parsing
import csv
import datetime
import html
import logging
import os
import re
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import PatternFill, Alignment, Font

from flask import json, Response
from flask_assets import Environment

# Here is the first time we use config. Check existence and raise a meaningful exception if not found.
try:
    from config import PATTERNS, PATTERNS_GROUP_ORDER
except ModuleNotFoundError:
    msg = 'Missing a config file. See README.md -> #Setup on how to create one.'
    logging.error(msg)
    raise FileNotFoundError(msg)

from reqtransformer import VarImportSessions, VariableCollection, Requirement, ScriptEvals, RequirementCollection
from static_utils import pickle_dump_obj_to_file, pickle_load_from_dump, replace_prefix, get_filenames_from_dir, \
    hash_file_sha1
from typing import Union, Set, List
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


def config_check(app_config):
    to_ensure_configs = [
        'PATTERNS',
        'PATTERNS_GROUP_ORDER'
    ]
    for to_ensure_config in to_ensure_configs:
        if to_ensure_config not in app_config:
            raise SyntaxError('Could not find {} in config.'.format(to_ensure_config))

    # Check pattern groups set correctly.
    pattern_groups_used = set((pattern['group'] for pattern in app_config['PATTERNS'].values()))
    pattern_groups_set = set((group for group in app_config['PATTERNS_GROUP_ORDER']))

    if not pattern_groups_used == pattern_groups_set:
        if len(pattern_groups_used - pattern_groups_set) > 0:
            raise SyntaxError('No group order set in config for pattern groups {}'.format(
                pattern_groups_used - pattern_groups_set
            ))

    try:
        get_default_pattern_options()
    except Exception as e:
        raise SyntaxError('Could not parse pattern config. Please check your config.py: {}.'.format(e))


def get_default_pattern_options():
    """ Parse the pattern config into the dropdown list options for the frontend

    Returns (str): Options for pattern selection in HTML.

    """
    result = '<option value="NotFormalizable">None</option>'
    opt_group_lists = defaultdict(list)
    opt_groups = defaultdict(str)
    # Collect pattern in groups.
    for name, pattern_dict in PATTERNS.items():
        opt_group_lists[pattern_dict['group']].append(
            (pattern_dict['pattern_order'], name, pattern_dict['pattern'])
        )

    # Sort groups and concatenate pattern options
    for group_name, opt_list in opt_group_lists.items():
        for _, name, pattern in sorted(opt_list):
            option = '<option value="{name}">{pattern}</option>'.format(
                name=name,
                pattern=pattern
            ).replace('{', '"{').replace('}', '}"')
            opt_groups[group_name] += option

    # Enclose pattern options by their groups.
    for group_name in PATTERNS_GROUP_ORDER:
        result += '<optgroup label="{}">'.format(group_name)
        result += opt_groups[group_name]
        result += '</optgroup>'

    return result


def get_formalization_template(templates_folder, requirement, formalization_id, formalization):
    result = {'success': True, 'html': formalization_html(
        templates_folder,
        formalization_id,
        default_scope_options,
        get_default_pattern_options(),
        formalization
    )}

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


def formalizations_to_html(app, formalizations):
    result = ''
    for index, formalization in formalizations.items():
        result += formalization_html(
            app.config['TEMPLATES_FOLDER'],
            index,
            default_scope_options,
            get_default_pattern_options(),
            formalization
        )
    return result


def get_available_vars(app, full=True, fetch_evals=False):
    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
    result = var_collection.get_available_vars_list(used_only=not full)

    if fetch_evals:
        script_results = ScriptEvals.load(path=app.config['SCRIPT_EVAL_RESULTS_PATH']).get_concatenated_evals()
        for variable_data in result:
            if variable_data['name'] in script_results:
                variable_data['script_results'] = script_results[variable_data['name']]

    return result


def varcollection_diff_info(app, request):
    """ Collect diff info of current and requested var collection.
        * Number of var in the requested var collection
        * Number of new vars in the requested var collection.


    :param request: API request
    :return: {'tot_vars': int, 'new_vars': int}
    :rtype: dict
    """
    current_var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
    req_path = os.path.join(
        app.config['SESSION_BASE_FOLDER'],
        request.form.get('sess_name').strip(),
        request.form.get('sess_revision').strip(),
        'session_variable_collection.pickle'
    )
    requested_var_collection = VariableCollection.load(req_path)

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
    current_var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
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


def get_requirements_using_var(requirements: list, var_name: str):
    """ Return a list of requirement ids where var_name is used in at least one formalization.

    :param requirements: list of Requirement.
    :param var_name: Variable name to search for.
    :return: List of affected Requirement ids.
    """
    result_rids = []
    for requirement in requirements:  # type: Requirement
        if requirement.uses_var(var_name):
            result_rids.append(requirement.rid)

    return result_rids


def update_variable_in_collection(app, request):
    """ Update a single variable. The request should contain a form:
        name -> the new name of the var.
        name_old -> the name of the var before.
        type -> the new type of the var.
        type_old -> the old type of the var.
        occurrences -> Ids of requirements using this variable.
        enumerators -> The dict of enumerators

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
    belongs_to_enum = request.form.get('belongs_to_enum', '').strip()
    belongs_to_enum_old = request.form.get('belongs_to_enum_old', '').strip()
    occurrences = request.form.get('occurrences', '').strip().split(',')
    enumerators = json.loads(request.form.get('enumerators', ''))

    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
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
    if (
        var_type_old != var_type
        or var_name_old != var_name
        or var_const_val_old != var_const_val
        or request.form.get('updated_constraints') == 'true'
        or belongs_to_enum != belongs_to_enum_old
    ):
        logging.info('Update Variable `{}`'.format(var_name_old))
        result['has_changes'] = True
        reload_type_inference = False

        # Update type.
        if var_type_old != var_type:
            logging.info('Change type from `{}` to `{}`.'.format(var_type_old, var_type))
            try:
                var_collection.collection[var_name_old].belongs_to_enum = belongs_to_enum
                var_collection.set_type(var_name_old, var_type)
            except TypeError as e:
                result = {
                    'success': False,
                    'errormsg': str(e)
                }
                return result
            result['type_changed'] = True
            reload_type_inference = True

        # Update const value.
        if var_const_val_old != var_const_val:
            try:
                if var_type == 'ENUMERATOR_INT':
                    int(var_const_val)
                if var_type in ['ENUMERATOR_REAL']:
                    float(var_const_val)
            except Exception as e:
                result = {
                    'success':  False,
                    'errormsg': 'Enumerator value `{}` for {} `{}` not valid: {}'.format(
                        var_const_val, var_type, var_name, e
                    )
                }
                return result
            logging.info('Change value from `{}` to `{}`.'.format(var_const_val_old, var_const_val))
            var_collection.collection[var_name].value = var_const_val
            result['val_changed'] = True

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
            affected_enumerators = []
            logging.debug('Change name of var `{}` to `{}`'.format(var_name_old, var_name))
            #  Case: New name which does not exist -> remove the old var and replace in reqs ocurring.
            if var_name not in var_collection:
                logging.debug('`{}` is a new var name. Rename the var, replace occurences.'.format(
                    var_name
                ))
                # Rename the var (Copy to new name and remove the old item. Rename it)
                affected_enumerators = var_collection.rename(var_name_old, var_name, app)

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
                affected_enumerators = var_collection.rename(var_name_old, var_name, app)
                result['rebuild_table'] = True
                reload_type_inference = True

            # Update the requirements using this var.
            if len(occurrences) > 0:
                rename_variable_in_expressions(app, occurrences, var_name_old, var_name)

            for (old_enumerator_name, new_enumerator_name) in affected_enumerators:
                # Todo: Implement this more eff.
                # Todo: Refactor Formalizations to use hashes as vars and fetch them in __str__ from the var collection.
                requirements = get_requirements(app.config['REVISION_FOLDER'])
                affected_requirements = get_requirements_using_var(requirements, old_enumerator_name)
                rename_variable_in_expressions(
                    app,
                    affected_requirements,
                    old_enumerator_name,
                    new_enumerator_name
                )

            result['name_changed'] = True

        # Change ENUM parent.
        if belongs_to_enum != belongs_to_enum_old and var_type in ['ENUMERATOR_INT', 'ENUMERATOR_REAL']:
            logging.debug('Change enum parent of enumerator `{}` to `{}`'.format(var_name, belongs_to_enum))
            if belongs_to_enum not in var_collection:
                result['success'] = False
                result['errormsg'] = 'The new ENUM parent `{}` does not exist.'.format(
                    belongs_to_enum
                )
                return result
            if var_collection.collection[belongs_to_enum].type != replace_prefix(var_type, 'ENUMERATOR', 'ENUM'):
                result['success'] = False
                result['errormsg'] = 'The new ENUM parent `{}` is not an {} (is `{}`).'.format(
                    belongs_to_enum,
                    replace_prefix(var_type, 'ENUMERATOR', 'ENUM'),
                    var_collection.collection[belongs_to_enum].type
                )
                return result
            new_enumerator_name = replace_prefix(var_name, belongs_to_enum_old, '')
            new_enumerator_name = replace_prefix(new_enumerator_name, '_', '')
            new_enumerator_name = replace_prefix(new_enumerator_name, '', belongs_to_enum + '_')
            if new_enumerator_name in var_collection:
                result['success'] = False
                result['errormsg'] = 'The new ENUM parent `{}` already has a ENUMERATOR `{}`.'.format(
                    belongs_to_enum,
                    new_enumerator_name
                )
                return result

            var_collection.collection[var_name].belongs_to_enum = belongs_to_enum
            var_collection.rename(var_name, new_enumerator_name, app)

        logging.info('Store updated variables.')
        var_collection.refresh_var_constraint_mapping()
        var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
        logging.info('Update derived types by parsing affected formalizations.')
        if reload_type_inference and var_name in var_collection.var_req_mapping:
            for rid in var_collection.var_req_mapping[var_name]:
                requirement = Requirement.load_requirement_by_id(rid, app)
                if requirement:
                    requirement.reload_type_inference(var_collection, app)

    if var_type in ['ENUM_INT', 'ENUM_REAL']:
        new_enumerators = []
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
                if var_type == 'ENUM_INT':
                    int(enumerator_value)
                if var_type == 'ENUM_REAL':
                    float(enumerator_value)
            except Exception as e:
                result = {
                    'success':  False,
                    'errormsg': 'Enumerator value `{}` for enumerator `{}` not valid: {}'.format(
                        enumerator_value, enumerator_name, e
                    )
                }
                break

            enumerator_name = '{}_{}'.format(var_name, enumerator_name)
            # Add new enumerators to the var_collection
            if not var_collection.var_name_exists(enumerator_name):
                var_collection.add_var(enumerator_name)
                new_enumerators.append(enumerator_name)

            var_collection.collection[enumerator_name].set_type('ENUMERATOR_{}'.format(var_type[5:]))
            var_collection.collection[enumerator_name].value = enumerator_value
            var_collection.collection[enumerator_name].belongs_to_enum = var_name

        var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])

        if len(new_enumerators) > 0:
            var_collection.reload_script_results(app, new_enumerators)

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
            requirement = Requirement.load(filepath)
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
            requirement.store(filepath)


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


def get_requirements(input_dir, filter_list=None, invert_filter=False):
    """ Load all requirements from session folder and return in a list.
    Orders the requirements based on their position in the CSV used to create the session (pos_in_csv).

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

    def should_be_in_result(req) -> bool:
        if filter_list is None:
            return True
        return (req.rid in filter_list) != invert_filter

    requirements = list()
    for filename in filenames:
        try:
            req = Requirement.load(filename)
        except TypeError:
            continue
        if hasattr(req, 'rid'):
            if should_be_in_result(req):
                logging.debug('Adding {} to results.'.format(req.rid))
                requirements.append(req)

    # We want to preserve the order of the generated CSV relative to the origin CSV.
    requirements.sort(key=lambda x: x.pos_in_csv)

    return requirements


def generate_csv_file_content(app, filter_list=None, invert_filter=False):
    """ Generates the csv file content for a session.

    :param app: Current hanfor app for context.
    :type app: Flaskapp
    :param output_file: Where to store the file
    :type output_file: str
    :param filter_list: (Optional) A list of requirement IDs to be included in the result. All if not set.
    :type filter_list: list (of strings)
    :param invert_filter: Exclude filter
    :type invert_filter: bool
    :return: CSV content
    :rtype: str
    """
    # Get requirements
    requirements = get_requirements(app.config['REVISION_FOLDER'], filter_list=filter_list, invert_filter=invert_filter)

    # get session status
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])  # type: dict

    # Add Formalization col if not existent in input CSV.
    for csv_key in [session_dict['csv_formal_header']]:
        if csv_key not in session_dict['csv_fieldnames']:
            session_dict['csv_fieldnames'].append(csv_key)

    # Add Hanfor Tag col to csv.
    # TODO: remove static column names and replace with config via user startup config dialog.
    tag_col_name = 'Hanfor_Tags'
    status_col_name = 'Hanfor_Status'
    for col_name in [tag_col_name, status_col_name]:
        if col_name not in session_dict['csv_fieldnames']:
            session_dict['csv_fieldnames'].append(col_name)

    # Update csv row of requirements to use their latest formalization and tags.
    for requirement in requirements:
        requirement.csv_row[session_dict['csv_formal_header']] = requirement.get_formalizations_json()
        requirement.csv_row[tag_col_name] = ', '.join(requirement.tags)
        requirement.csv_row[status_col_name] = requirement.status

    # Write data to file.
    rows = [r.csv_row for r in requirements]
    with StringIO() as out_csv:
        csv.register_dialect('ultimate', delimiter=',')
        writer = csv.DictWriter(out_csv, session_dict['csv_fieldnames'], dialect=session_dict['csv_dialect'])
        writer.writeheader()
        writer.writerows(rows)
        result = out_csv.getvalue()

    return result


def generate_xls_file_content(app, filter_list: List[str] = None, invert_filter: bool = False) -> io.BytesIO:
    """ Generates the xlsx file content for a session."""
    requirements = get_requirements(app.config['REVISION_FOLDER'], filter_list=filter_list, invert_filter=invert_filter)
    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])

    # create  styles
    MULTILINE = Alignment(vertical="top", wrap_text=True)
    BOLD = Font(bold=True)
    WHITE = Font(color="FFFFFF", bold=True)
    FILLED = PatternFill(fill_type="solid", start_color="2a6ebb", end_color="2a6ebb")
    META = PatternFill(fill_type="solid", start_color="004a99", end_color="004a99")
    #create excel template
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.title = "Requirements"

    HEADER_OFFSET = 4
    def make_header(work_sheet):
        work_sheet.freeze_panes = "A4"
        for c in range(1, 10):
            for r in range(1, 3):
                work_sheet.cell(r, c).fill = META
        work_sheet.cell(1, 2, value= "HANFOR Report")
        work_sheet.cell(1, 2).font = WHITE
        work_sheet.cell(1, 3, value=session_dict['csv_input_file'])
        work_sheet.cell(1, 3).font = Font(color="FFFFFF")
        for c in range(1, 10):
            work_sheet.cell(HEADER_OFFSET - 1, c).fill = FILLED
            work_sheet.cell(HEADER_OFFSET - 1, c).font = WHITE
    make_header(work_sheet)


    # Set column widths and headings
    work_sheet.column_dimensions['A'].width = 5
    work_sheet.cell(HEADER_OFFSET - 1, 1, value="Index")
    work_sheet.column_dimensions['B'].width = 20
    work_sheet.cell(HEADER_OFFSET - 1, 2, value="ID")
    work_sheet.column_dimensions['C'].width = 80
    work_sheet.cell(HEADER_OFFSET - 1, 3, value="Description")
    work_sheet.cell(HEADER_OFFSET - 1, 4, value="Type")
    work_sheet.column_dimensions['E'].width = 40
    work_sheet.cell(HEADER_OFFSET - 1, 5, value="Tags")
    work_sheet.cell(HEADER_OFFSET - 1, 6, value="Status")
    work_sheet.column_dimensions['G'].width = 160
    work_sheet.cell(HEADER_OFFSET - 1, 7, value="Formalisation")

    for i, requirement in enumerate(requirements):
        for c in range(1, 8):
            # Note: setting styles is ordering-sensitive so set styles FIRST
            work_sheet.cell(HEADER_OFFSET + i, c).alignment = MULTILINE
        work_sheet.cell(HEADER_OFFSET + i, 1, requirement.pos_in_csv)
        work_sheet.cell(HEADER_OFFSET + i, 2).font = BOLD
        work_sheet.cell(HEADER_OFFSET + i, 2, requirement.rid)
        work_sheet.cell(HEADER_OFFSET + i, 3, requirement.description)
        work_sheet.cell(HEADER_OFFSET + i, 4, requirement.type_in_csv)
        work_sheet.cell(HEADER_OFFSET + i, 5, "".join([f"{tag}: \n" for tag in requirement.tags]))
        work_sheet.cell(HEADER_OFFSET + i, 6, requirement.status)
        work_sheet.cell(HEADER_OFFSET + i, 7,
                         "\n".join([f.get_string() for f in requirement.formalizations.values()]))

    # make severity sheet
    tag_sheet = work_book.create_sheet("Findings")
    make_header(tag_sheet)
    tag_sheet.column_dimensions['A'].width = 5
    tag_sheet.cell(HEADER_OFFSET - 1, 1, value="Index")
    tag_sheet.column_dimensions['B'].width = 20
    tag_sheet.cell(HEADER_OFFSET - 1, 2, value="ID")
    tag_sheet.cell(HEADER_OFFSET - 1, 3, value="Description")
    tag_sheet.column_dimensions['C'].width = 80
    tag_sheet.column_dimensions['D'].width = 20
    tag_sheet.cell(HEADER_OFFSET - 1, 4, value="Tag")
    tag_sheet.column_dimensions['E'].width = 60
    tag_sheet.cell(HEADER_OFFSET - 1, 5, value="Comment (Analysis)")
    tag_sheet.column_dimensions['F'].width = 10
    tag_sheet.cell(HEADER_OFFSET - 1, 6, value="Accept")
    tag_sheet.column_dimensions['G'].width = 15
    tag_sheet.cell(HEADER_OFFSET - 1, 7, value="Value")
    tag_sheet.column_dimensions['H'].width = 80
    tag_sheet.cell(HEADER_OFFSET - 1, 8, value="Comment (Review)")

    accept_state_validator = DataValidation(type="list", formula1='"TODO ,Accept,Decline,Inquery"', allow_blank=False)
    tag_sheet.add_data_validation(accept_state_validator)
    accept_state_validator.add("F4:F1048576")
    issue_value_validator = DataValidation(type="list",
          formula1='"TODO, 0 (no value),1 (nice to have),2 (useful),3 (possible desaster)"', allow_blank=True)
    tag_sheet.add_data_validation(issue_value_validator)
    issue_value_validator.add("G4:G1048576")


    for i, (req, tag) in enumerate([(req, tag) for req in requirements for tag in req.tags]):
        for c in range(1, 8):
            tag_sheet.cell(HEADER_OFFSET + i, c).alignment = MULTILINE
        tag_sheet.cell(HEADER_OFFSET + i, 1, req.pos_in_csv)
        tag_sheet.cell(HEADER_OFFSET + i, 2).font = BOLD
        tag_sheet.cell(HEADER_OFFSET + i, 2, req.rid)
        tag_sheet.cell(HEADER_OFFSET + i, 3, req.description)
        tag_sheet.cell(HEADER_OFFSET + i, 4, tag)
        tag_sheet.cell(HEADER_OFFSET + i, 5, "") # Tags do currently not have comments
        tag_sheet.cell(HEADER_OFFSET + i, 6, "TODO")
        tag_sheet.cell(HEADER_OFFSET + i, 7, "TODO")


    # make sheet with variables
    var_sheet = work_book.create_sheet("Variables")
    make_header(var_sheet)
    var_sheet.column_dimensions['A'].width = 40
    var_sheet.cell(HEADER_OFFSET - 1, 1, value="Name")
    var_sheet.column_dimensions['B'].width = 80
    var_sheet.column_dimensions['C'].width = 5
    var_sheet.cell(HEADER_OFFSET - 1, 2, value="Type")
    var_sheet.column_dimensions['D'].width = 180
    var_sheet.cell(HEADER_OFFSET - 1, 4, value="Invarianten")

    for i, var in enumerate(var_collection.collection.values()):
        for c in range(1, 8):
            var_sheet.cell(HEADER_OFFSET + i, c).alignment = MULTILINE
        var_sheet.cell(HEADER_OFFSET + i, 1, var.name)
        var_sheet.cell(HEADER_OFFSET + i, 1).font = BOLD
        var_sheet.cell(HEADER_OFFSET + i, 2, var.type)
        var_sheet.cell(HEADER_OFFSET + i, 3, "E" if var.belongs_to_enum else "")
        var_sheet.cell(HEADER_OFFSET + i, 4, "\n".join([c.get_string() for c in var.get_constraints().values()]))

    work_book.active = tag_sheet
    buffer = io.BytesIO()
    work_book.save(buffer)
    return buffer


def clean_identifier_for_ultimate_parser(slug: str, used_slugs: Set[str]) -> (str, Set[str]):
    """ Clean slug to be sound for ultimate parser.

    :param slug: The slug to be cleaned.
    :param used_slugs: Set of already used slugs.
    :return: (save_slug, used_slugs) save_slug a save to use form of slug. save_slug added to used_slugs.
    """
    # Replace any occurence of [whitespace, `.`, `-`] with `_`
    slug = re.sub(r"[\s+.-]+", '_', slug.strip())

    # Resolve illegal start by prepending the slug with ID_ in case it does not start with a letter.
    slug = re.sub(r"^([^a-zA-Z])", r'ID_\1', slug)

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


def generate_req_file_content(app, filter_list=None, invert_filter=False, variables_only=False):
    """ Generate the content (string) for the ultimate requirements file.
        :param app: Current app.
        :type app: FlaskApp
        :param filter_list: A list of requirement IDs to be included in the result. All if not set.
        :type filter_list: list (of strings)
        :param invert_filter: Exclude filter
        :type invert_filter: bool
        :type invert_filter: bool
        :param variables_only: If true, only variables and no requirements will be included.
        :return: Content for the req file.
        :rtype: str
        """
    logging.info('Generating .req file content for session {}'.format(app.config['SESSION_TAG']))
    # Get requirements
    requirements = get_requirements(app.config['REVISION_FOLDER'], filter_list=filter_list, invert_filter=invert_filter)

    var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
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

    content_list = []
    constants_list = []
    constraints_list = []

    # Parse variables and variable constraints.
    for var in var_collection.collection.values():
        if var.name in available_vars:
            if var.type in ['CONST', 'ENUMERATOR_INT', 'ENUMERATOR_REAL']:
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
    if not variables_only:
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

    return content


def get_stored_session_names(session_folder, only_names=False, with_revisions=False) -> tuple:
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

    Args:
        session_folder (str): path to hanfor data folder.
        only_names (bool): Only return the names (tags).
        with_revisions (bool): Recurse also into the available revisions.

    Returns:
        tuple: Only folder names or stats with names.
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
            num_vars = len(VariableCollection.load(revision_var_collection_path).collection)
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


def add_msg_to_flask_session_log(app, msg, rid=None, rid_list=None, clear=False, max_msg=50) -> None:
    """ Add a log message for the frontend_logs.

    :param max_msg: Max number of messages to keep in the log.
    :param rid_list: A list of affected requirement IDs
    :param rid: Affected requirement id
    :param app: The flask app
    :param msg: Log message string
    :param clear: Turncate the logs if set to true (false on default).
    """
    session = pickle_load_from_dump(app.config['FRONTEND_LOGS_PATH'])  # type: dict
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

    # Remove oldest logs until threshold
    while len(session['hanfor_log']) > max_msg:
        session['hanfor_log'].pop(0)

    pickle_dump_obj_to_file(session, app.config['FRONTEND_LOGS_PATH'])


def get_flask_session_log(app, html=False) -> Union[list, str]:
    """ Get the frontent log messages from frontend_logs.

    :param app: The flask app
    :param html: Return formatted html version.
    :return: list of messages or html string in case `html == True`
    """
    session = pickle_load_from_dump(app.config['FRONTEND_LOGS_PATH'])  # type: dict
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


def generate_file_response(content, name, mimetype='text/plain'):
    response = Response(
        content,
        mimetype=mimetype
    )
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{name}"
    return response


def get_requirements_in_folder(folder_path):
        result = dict()
        for filename in get_filenames_from_dir(folder_path):
            try:
                r = Requirement.load(filename)
                result[r.rid] = {
                    'req': r,
                    'path': filename
                }
            except TypeError:
                continue
            except Exception as e:
                raise e
        return result


def init_var_collection(app):
    """ Creates a new empty VariableCollection if non is existent for current session.

    """
    if not os.path.exists(app.config['SESSION_VARIABLE_COLLECTION']):
        var_collection = VariableCollection(path=app.config['SESSION_VARIABLE_COLLECTION'])
        var_collection.store()


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
        entries = get_stored_session_names(self.app.config['SESSION_BASE_FOLDER'], with_revisions=True)
        data = [['Tag', 'Revision', 'Last Modified']]
        for entry in entries:
            revisions = list()
            for name, values in entry['revisions_stats'].items():
                revisions.append((name, values['last_mod']))
            revisions.sort()
            if len(revisions) > 0:
                data.append([entry['name'], revisions[0][0], revisions[0][1]])
                for i in range(1, len(revisions)):
                    data.append(['', revisions[i][0], revisions[i][1]])
            else:
                data.append([entry['name'], '', ''])
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
        self.add_argument("tag", help="A tag for the session. Session will be reloaded, if tag exists.")
        self.add_argument("-c", "--input_csv", help="Path to the csv to be processed.")
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
        self.add_argument(
            '-hd', '--headers',
            type=str,
            help='Header Definition of the form --header=\'{ "csv_id_header": "ID", "csv_desc_header": "Description", "csv_formal_header": "Hanfor_Formalization", "csv_type_header" : "Type"}\', must be valid json.',
            default=None
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


class Revision:
    def __init__(self, app, args, base_revision_name):
        self.app = app
        self.args = args
        self.base_revision_name = base_revision_name
        self.is_initial_revision = True
        self.base_revision_folder = None
        self.base_revision_settings = None
        self.base_revision_var_collectioin_path = None
        self.available_sessions = None
        self.requirement_collection = None

        self._set_is_initial_revision()
        self._set_revision_name()
        self._set_base_revision_folder()
        self._set_base_revision_settings()
        self._set_base_revision_var_collection_path()

    def create_revision(self):
        self._check_base_revision_available()
        self._set_config_vars()
        self._set_available_sessions()
        self._create_revision_folder()
        if self.is_initial_revision:
            try:
                init_var_collection(self.app)
            except Exception as e:
                logging.error('Could not create initial variable Collection: {}'.format(e))
                self._revert_and_cleanup()
                raise e
        self._try_save(self._load_from_csv, 'Could not read CSV')
        self._try_save(self._store_requirements, 'Could not store requirements')
        self._try_save(self._generate_session_dict, 'Could not generate session')
        if not self.is_initial_revision:
            self._try_save(self._merge_with_base_revision, ' Could not merge with base session')

    def _try_save(self, what, error_msg):
        """ Safely run a method. Cleanup the revision in case of a exception.

        Args:
            what: Method to run.
            error_msg: Message in case of failure.
        """
        try:
            what()
        except Exception as e:
            logging.error('Abort creating revision. {msg}: {error}'.format(
                msg=error_msg,
                error=type(e)
            ))
            self._revert_and_cleanup()
            raise e

    def _set_revision_name(self):
        if not self.base_revision_name:
            logging.info('No revisions for `{}`. Creating initial revision.'.format(self.args.tag))
            self.revision_name = 'revision_0'
        # Revision based on a existing revision
        else:
            new_revision_count = max(
                [int(name.split('_')[1]) for name in get_available_revisions(self.app.config)]) + 1
            self.revision_name = 'revision_{}'.format(new_revision_count)

    def _set_base_revision_settings(self):
        if not self.is_initial_revision:
            self.base_revision_settings = pickle_load_from_dump(
                os.path.join(
                    self.base_revision_folder,
                    'session_status.pickle'
                )
            )

    def _set_base_revision_folder(self):
        if not self.is_initial_revision:
            self.base_revision_folder = os.path.join(
                self.app.config['SESSION_FOLDER'],
                self.base_revision_name
            )

    def _set_is_initial_revision(self):
        if self.base_revision_name:
            self.is_initial_revision = False

    def _set_base_revision_var_collection_path(self):
        if not self.is_initial_revision:
            self.base_revision_var_collectioin_path = os.path.join(
                self.base_revision_folder,
                'session_variable_collection.pickle'
            )

    def _set_config_vars(self):
        self.app.config['USING_REVISION'] = self.revision_name
        self.app.config['REVISION_FOLDER'] = os.path.join(
            self.app.config['SESSION_FOLDER'],
            self.revision_name
        )
        self.app.config['SESSION_VARIABLE_COLLECTION'] = os.path.join(
            self.app.config['REVISION_FOLDER'],
            'session_variable_collection.pickle'
        )
        self.app.config['SESSION_STATUS_PATH'] = os.path.join(
            self.app.config['REVISION_FOLDER'],
            'session_status.pickle'
        )

    def _check_base_revision_available(self):
        if not self.is_initial_revision and self.base_revision_name not in get_available_revisions(self.app.config):
            logging.error(
                'Base revision `{}` not found in `{}`'.format(
                    self.base_revision_name, self.app.config['SESSION_FOLDER']
                )
            )
            raise FileNotFoundError

    def _set_available_sessions(self):
        self.available_sessions = get_stored_session_names(
            self.app.config['SESSION_BASE_FOLDER'],
            with_revisions=True
        )

    def _load_from_csv(self):
        # Load requirements from .csv file and store them into separate requirements.
        if self.args.input_csv is None:
            HanforArgumentParser(self.app).error('Creating an (initial) revision requires -c INPUT_CSV')
        self.requirement_collection = RequirementCollection()
        self.requirement_collection.create_from_csv(
            csv_file=self.args.input_csv,
            app=self.app,
            input_encoding='utf8',
            base_revision_headers=self.base_revision_settings,
            user_provided_headers=(json.loads(self.args.headers) if self.args.headers else None),
            available_sessions=self.available_sessions
        )

    def _create_revision_folder(self):
        os.makedirs(self.app.config['REVISION_FOLDER'], exist_ok=True)

    def _revert_and_cleanup(self):
        logging.info('Reverting revision creation.')
        if self.is_initial_revision:
            logging.debug(
                'Revert initialized session folder. Deleting: `{}`'.format(self.app.config['SESSION_FOLDER']))
            shutil.rmtree(self.app.config['SESSION_FOLDER'])
        else:
            logging.debug(
                'Revert initialized revision folder. Deleting: `{}`'.format(self.app.config['REVISION_FOLDER']))
            shutil.rmtree(self.app.config['REVISION_FOLDER'])

    def _store_requirements(self):
        for index, req in enumerate(self.requirement_collection.requirements):  # type: Requirement
            filename = os.path.join(self.app.config['REVISION_FOLDER'], '{}.pickle'.format(req.rid))
            req.store(filename)

    def _generate_session_dict(self):
        # Generate the session dict: Store some meta information.
        session = dict()
        session['csv_input_file'] = self.args.input_csv
        session['csv_fieldnames'] = self.requirement_collection.csv_meta['fieldnames']
        session['csv_id_header'] = self.requirement_collection.csv_meta['id_header']
        session['csv_formal_header'] = self.requirement_collection.csv_meta['formal_header']
        session['csv_type_header'] = self.requirement_collection.csv_meta['type_header']
        session['csv_desc_header'] = self.requirement_collection.csv_meta['desc_header']
        session['csv_hash'] = hash_file_sha1(self.args.input_csv)
        pickle_dump_obj_to_file(session, self.app.config['SESSION_STATUS_PATH'])

    def _merge_with_base_revision(self):
        # Merge the old revision into the new revision
        logging.info('Merging `{}` into `{}`.'.format(self.base_revision_name, self.revision_name))
        old_reqs = get_requirements_in_folder(self.base_revision_folder)
        new_reqs = get_requirements_in_folder(self.app.config['REVISION_FOLDER'])

        # Diff the new requirements against the old ones.
        for rid in new_reqs.keys():
            # Tag newly introduced requirements.
            if rid not in old_reqs.keys():
                logging.info('Add newly introduced requirement `{}`'.format(rid))
                new_reqs[rid]['req'].tags.add(
                    '{}_to_{}_new_requirement'.format(self.base_revision_name, self.revision_name)
                )
                continue

            # Migrate tags and status.
            new_reqs[rid]['req'].tags = old_reqs[rid]['req'].tags
            new_reqs[rid]['req'].status = old_reqs[rid]['req'].status
            new_reqs[rid]['req'].revision_diff = old_reqs[rid]['req']

            if len(new_reqs[rid]['req'].revision_diff) > 0:
                logging.info(
                    'CSV entry changed. Add `revision_data_changed` tag to `{}`.'.format(rid)
                )
                new_reqs[rid]['req'].tags.add(
                    '{}_to_{}_data_changed'.format(self.base_revision_name, self.revision_name)
                )

            if new_reqs[rid]['req'].description != old_reqs[rid]['req'].description:
                logging.info(
                    'Description changed. Add `description_changed` tag to `{}`.'.format(rid)
                )
                new_reqs[rid]['req'].tags.add(
                    '{}_to_{}_description_changed'.format(self.base_revision_name, self.revision_name))
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
                        'Add `migrated_formalization` tag to `{}`, status to `Todo` since description changed'.format(
                            rid))
                    new_reqs[rid]['req'].tags.add(
                        '{}_to_{}_migrated_formalization'.format(self.base_revision_name, self.revision_name)
                    )
                    new_reqs[rid]['req'].status = 'Todo'
            elif len(new_reqs[rid]['req'].formalizations) == 0 and len(old_reqs[rid]['req'].formalizations) > 0:
                logging.error('Parsing of the requirement not supported.')
                raise NotImplementedError

        # Store the updated requirements for the new revision.
        logging.info('Store merge changes to revision `{}`'.format(self.revision_name))
        for r in new_reqs.values():
            r['req'].store(r['path'])

        # Store the variables collection in the new revision.
        logging.info('Migrate variables from `{}` to `{}`'.format(self.base_revision_name, self.revision_name))
        base_var_collection = VariableCollection.load(self.base_revision_var_collectioin_path)
        base_var_collection.store(self.app.config['SESSION_VARIABLE_COLLECTION'])
