""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import argparse
import boogie_parsing
import csv
import datetime
import html
import logging
import pickle
import random
import re
import shlex
import os

from colorama import Fore, Style
from flask_assets import Bundle, Environment
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


def get_formalization_template(templates_folder, requirement, formalization_id, formalization):
    result = {'success': True}
    options = predict_scoped_pattern_to_options(requirement, reset=True)

    result['html'] = formalization_html(
        templates_folder,
        formalization_id,
        options['scopes'],
        options['patterns'],
        formalization
    )

    return result


def predict_scoped_pattern_to_options(requirement, reset=True):
    """ Predicts the requirement scope and pattern and returns the html options for the requirement modal.

    :type requirement: Requirement
    """
    result = {
        'scopes': default_scope_options,
        'patterns': default_pattern_options
    }

    if not reset:
        clf = SvmPatternClassifier()
        clf.train()
        predicted_scopes = clf.predict_scope(requirement.description)
        predicted_pattern = clf.predict_pattern(requirement.description)
        patterns = ''
        for pattern in predicted_pattern:  # type Pattern
            patterns += '<option value="{}">{}</option>'.format(pattern.name, pattern.pattern)
        result['patterns'] = patterns

        scopes = ''
        for scope_name, scope_instance in predicted_scopes:
            scopes += '<option value="{}">{}</option>'.format(scope_name, scope_instance)
        result['scopes'] = scopes

    return result


def formalization_html(templates_folder, formalization_id, scope_options, pattern_options, formalization):
    # Load template.
    html_template = ''
    with open(os.path.join(templates_folder, 'formalization.html'), mode='r') as f:
        html_template += '\n'.join(f.readlines())

    # Set values
    html_template = html_template.replace('__formalization_text__', formalization.get_string())
    html_template = html_template.replace('__formal_id__', '{}'.format(formalization_id))
    form_desc = formalization.get_string()[:90]
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
            'title="{}"'.format(key), 'title="{}" value="{}"'.format(key, html.escape(str(value))))

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
    for index, formalization in enumerate(formalizations):
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


def get_available_vars(app, parser=None, full=False):
    var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])
    result = var_collection.get_available_vars_list(used_only=True)

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
    occurences = request.form.get('occurences', '').strip().split(',')

    result = {
        'success': True,
        'has_changes': False,
        'type_changed': False,
        'name_changed': False,
        'rebuild_table': False,
        'data': {
            'name': var_name,
            'type': var_type,
            'used_by': occurences,
            'const_val': var_const_val
        }
    }

    # Check for changes
    if var_type_old != var_type or var_name_old != var_name or var_const_val_old != var_const_val:
        logging.info('Update Variable `{}`'.format(var_name_old))
        result['has_changes'] = True
        var_collection = pickle_load_from_dump(app.config['SESSION_VARIABLE_COLLECTION'])  # type: dict

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
                logging.debug(
                    '`{}` is an existing var name. Merging the two vars. '
                    '(Type of the new var `{}` wins over the old type `{}` )'.format(
                        var_name,
                        var_type,
                        var_collection.collection[var_name].type
                    )
                )
                var_collection.merge_vars(var_name_old, var_name, app)
                result['rebuild_table'] = True

            # delete the old.
            # Update the requirements using this var.
            if len(occurences) > 0:
                rename_variable_in_expressions(app, occurences, var_name_old, var_name)

            result['name_changed'] = True

        # Update type.
        if var_type_old != var_type:
            logging.info('Change type from `{}` to `{}`.'.format(var_type_old, var_type))
            var_collection.collection[var_name].type = var_type
            result['type_changed'] = True

        # Update const value.
        if var_const_val_old != var_const_val:
            logging.info('Change value from `{}` to `{}`.'.format(var_const_val_old, var_const_val))
            var_collection.collection[var_name].value = var_const_val
            result['val_changed'] = True

        logging.info('Store updated variables.')
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
            for index, formalization in enumerate(requirement.formalizations):
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
        'top_variable_colors': list()
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
    if len(var_usage) > 10:
        var_usage = var_usage[:10]

    for count, name in var_usage:
        data['top_variable_names'].append(name)
        data['top_variables_counts'].append(count)
        data['top_variable_colors'].append("#%06x" % random.randint(0, 0xFFFFFF))

    return data


def get_requirements(input_dir, filter_list=None, invert_filter=False):
    """ Load all requiremenst from session folder and return in a list.

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
    requirements = get_requirements(app.config['REVISION_FOLDER'], filter_list=filter_list, invert_filter=invert_filter)

    # get session status
    session_dict = pickle_load_from_dump(app.config['SESSION_STATUS_PATH'])  # type: dict

    # Write to output_file
    if not output_file:
        output_file = os.path.join(app.config['SESSION_FOLDER'], '{}_{}_out.csv'.format(
            app.config['SESSION_TAG'],
            app.config['USING_REVISION']
        ))
    for requirement in requirements:
        requirement.csv_row[session_dict['csv_formal_header']] = requirement.get_formalization_string()
    rows = [r.csv_row for r in requirements]
    with open(output_file, mode='w') as out_csv:
        csv.register_dialect('ultimate', delimiter=',')
        writer = csv.DictWriter(out_csv, session_dict['csv_fieldnames'], dialect=session_dict['csv_dialect'])
        writer.writeheader()
        writer.writerows(rows)

    return output_file


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

    # Write to .req file
    if not output_file:
        output_file = os.path.join(
            app.config['SESSION_FOLDER'], '{}_{}_formalized_requirements.req'.format(
                app.config['SESSION_TAG'],
                app.config['USING_REVISION']
            ))
    logging.info('Write to output file: {}'.format(output_file))
    with open(output_file, mode='w') as out_file:
        content = ''
        constants = ''
        for var in available_vars:
            if var['type'] == 'CONST':
                constants += 'CONST {} IS {}\n'.format(var['name'], var['const_val'])
            else:
                content += 'Input {} IS {}\n'.format(var['name'], var['type'])
        if len(constants) > 0:
            content = '\n'.join([constants, content])
        content += '\n'
        for requirement in requirements:  # type: Requirement
            try:
                for index, formalization in enumerate(requirement.formalizations):
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
                        re.sub(r"\s+", '_', requirement.rid),
                        index,
                        formalization.get_string()
                    )
            except AttributeError:
                continue
        content += '\n'
        out_file.write(content)

    return output_file


def get_stored_session_names(session_folder=None, only_names=False) -> tuple:
    """ Get stored session tags (folder names) including os.stat.
    Returned tuple is (
        (os.stat(), name),
        ...
    )
    If only_names == True the list is (
        name_1,
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
        result = ((os.path.join(session_folder, file_name), file_name) for file_name in os.listdir(session_folder))
        if only_names:
            result = (entry[1] for entry in result)
        else:
            result = ((os.stat(entry[0]), entry[1]) for entry in result)
    except Exception as e:
        logging.error('Could not fetch stored sessions: {}'.format(e))

    return result


def get_available_revisions(config):
    result = []

    try:
        names = os.listdir(config['SESSION_FOLDER'])
        result = [name for name in names if os.path.isdir(os.path.join(config['SESSION_FOLDER'], name))]
    except Exception as e:
        logging.error('Could not fetch stored sessions: {}'.format(e))

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
        'js': Bundle(
            'js/jquery-3.2.1.js',
            'js/jquery-ui.js',
            'js/bootstrap-tokenfield.js',
            'js/popper.js',
            'js/jquery.dataTables.js',
            'js/tether.js',
            'js/bootstrap.js',
            'js/dataTables.bootstrap4.js',
            'js/loadingoverlay.js',
            'js/bootstrap-confirmation.min.js',
            filters='jsmin',
            output='gen/vendor.js'
        ),
        'main': Bundle(
            'js/app.js',
            output='main/app.js'
        ),
        'css': Bundle(
            'css/bootstrap.css',
            'css/bootstrap-grid.css',
            'css/bootstrap-reboot.css',
            'css/dataTables.bootstrap4.css',
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
    offset = 6  # we have 6 fixed cols.
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


def slugify(s):
    """ Normalizes string, converts to lowercase, removes non-alpha characters, and converts spaces to hyphens.

    :param s: string
    :type s: str
    :return: String save for filename
    :rtype: str
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


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


class ParseSessionsToUltimateReqFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None, **kwargs):
        tag = values[0]
        logging.info('Generating .req file for session {}'.format(tag))
        generate_req_file(tag)
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
            '-L', '--list_stored_sessions',
            nargs=0,
            help="List the tags of stored sessions..",
            action=ListStoredSessions,
            app=self.app
        )
        self.add_argument(
            '-G', '--generate_formalization_from_session',
            metavar='session_tag',
            nargs=1,
            help="Generates ultimate formalization from an existing session and stores the result to .req file.",
            action=ParseSessionsToUltimateReqFile
        )
