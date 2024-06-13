""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import csv
import difflib
import json
import logging
import os
import pickle
import re
import string
import subprocess
from collections import defaultdict, OrderedDict
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from flask import current_app
from lark import LarkError
from packaging import version

import boogie_parsing
from boogie_parsing import run_typecheck_fixpoint, BoogieType
from patterns import PATTERNS
from static_utils import choice, get_filenames_from_dir, replace_prefix, try_cast_string
from threading import Thread
from typing import Dict, Tuple

__version__ = '1.0.4'


class HanforVersioned:
    def __init__(self):
        self._hanfor_version = __version__

    @property
    def hanfor_version(self) -> str:
        if not hasattr(self, '_hanfor_version'):
            self._hanfor_version = '0.0.0'
        return self._hanfor_version

    @hanfor_version.setter
    def hanfor_version(self, val):
        self._hanfor_version = val

    @property
    def outdated(self) -> bool:
        return version.parse(self.hanfor_version) < version.parse(__version__)

    def run_version_migrations(self):
        if self.outdated:
            logging.debug(f"Migration (noop) {self}: from {self.hanfor_version} -> {__version__}")
            self._hanfor_version = __version__
            # this is a shortcut to skip explicit update code for all things that did not change in a version.
            # TODO: non the less this should be solved differently
            if isinstance(self, Pickleable):
                self.store()


class Pickleable:
    def __init__(self, path):
        self.my_path = path

    @classmethod
    def load(cls, path):
        path_size = os.path.getsize(path)

        if not path_size > 0:
            raise AssertionError('Could not load object from `{}`. (path size is {})'.format(path, path_size))

        with open(path, mode='rb') as f:
            me = pickle.load(f)
            if not isinstance(me, cls):
                raise TypeError

        me.my_path = path

        return me

    def store(self, path=None):
        if path is not None:
            self.my_path = path

        with open(self.my_path, mode='wb') as out_file:
            pickle.dump(self, out_file)


@dataclass
class CsvConfig:
    """Representation of structure of csv being imported"""
    
    dialect: str = None
    fieldnames: str = None
    headers: list = field(default_factory=list)
    id_header: str = None
    desc_header: str = None
    formal_header: str = None
    type_header: str = None
    tags_header: str = None
    status_header: str = None
    import_formalizations: bool = False

class RequirementCollection(HanforVersioned, Pickleable):

    def __init__(self):
        HanforVersioned.__init__(self)
        Pickleable.__init__(self, None)
        self.csv_meta = CsvConfig()
        self.csv_all_rows = None
        self.requirements = list()

    def create_from_csv(
            self, csv_file, app, input_encoding='utf8', base_revision_headers=None,
            user_provided_headers=None, available_sessions=None
    ):
        """ Create a RequirementCollection from a csv file, containing one requirement per line.
        Ask the user which csv fields corresponds to which requirement data.

        Args:
            csv_file (str):
            app (Flask.app):
            input_encoding (str):
            base_revision_headers (dict):
            user_provided_headers (dict):
            available_sessions (tuple):
        """
        self.load_csv(csv_file, input_encoding)
        self.select_headers(
            base_revision_headers=base_revision_headers,
            user_provided_headers=user_provided_headers
        )
        self.process_csv_hanfor_data_import(available_sessions=available_sessions, app=app)
        self.parse_csv_rows_into_requirements(app)

    def load_csv(self, csv_file: str, input_encoding: str):
        """ Reads a csv file into `csv_all_rows`. Stores csv_dialect and csv_fieldnames in `csv_meta`

        :param csv_file: Path to csv file.
        :param input_encoding: Encoding of the csv file.
        """
        logging.info(f'Load Input : {csv_file}')
        with open(csv_file, 'r', encoding=input_encoding) as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(2048), delimiters="\t,;")
                dialect.escapechar = '\\'
            except csv.Error:
                logging.info("Could not guess .csv dialect, assuming defaults")
                csv.register_dialect('ultimate', delimiter=',')
                dialect = 'ultimate'
            csvfile.seek(0)

            reader = csv.DictReader(csvfile, dialect=dialect)
            self.csv_all_rows = list(reader)
            self.csv_meta.fieldnames = reader.fieldnames
            self.csv_meta.headers = sorted(list(reader.fieldnames))

    def select_headers(self, base_revision_headers=None, user_provided_headers=None):
        """ Determines which of the csv headers correspond to our needed data.

        Args:
            base_revision_headers:
            user_provided_headers:
        """
        use_old_headers = False
        if base_revision_headers:
            print('Should I use the csv header mapping from base revision?')
            use_old_headers = choice(['yes', 'no'], 'yes')

        if user_provided_headers:
            print(user_provided_headers)
            self.csv_meta.id_header = user_provided_headers['csv_id_header']
            self.csv_meta.desc_header = user_provided_headers['csv_desc_header']
            self.csv_meta.formal_header = user_provided_headers['csv_formal_header']
            self.csv_meta.type_header = user_provided_headers['csv_type_header']
        elif base_revision_headers and use_old_headers == 'yes':
            self.csv_meta.id_header = base_revision_headers['csv_id_header']
            self.csv_meta.desc_header = base_revision_headers['csv_desc_header']
            self.csv_meta.formal_header = base_revision_headers['csv_formal_header']
            self.csv_meta.type_header = base_revision_headers['csv_type_header']
        else:
            available_headers = set(self.csv_meta.headers)
            available_headers.discard('Hanfor_Tags')
            available_headers.discard('Hanfor_Status')
            available_headers = sorted(available_headers)

            print('Select ID header')
            self.csv_meta.id_header = choice(available_headers, 'ID')
            print('Select requirements description header')
            self.csv_meta.desc_header = choice(available_headers, 'Object Text')
            print('Select formalization header')
            self.csv_meta.formal_header = choice(available_headers + ['Add new Formalization'], 'Hanfor_Formalization')
            if self.csv_meta.formal_header == 'Add new Formalization':
                self.csv_meta.formal_header = 'Hanfor_Formalization'
            print('Select type header.')
            self.csv_meta.type_header = choice(available_headers, 'RB_Classification')

    def process_csv_hanfor_data_import(self, available_sessions, app):
        if app.config['USING_REVISION'] != 'revision_0':  # We only support importing formalizations for base revisions
            return

        print('Do you want to import existing data from CSV?')
        if choice(['no', 'yes'], 'no') == 'no':
            return

        print('Do you want to import Formalizations from CSV?')
        import_formalizations = choice(['no', 'yes'], 'no')
        if import_formalizations == 'yes':
            self.csv_meta.import_formalizations = True

        print('Do you want to import Hanfor tags and status from CSV?')
        if choice(['no', 'yes'], 'no') == 'yes':
            print('Select the Hanfor Tags header.')
            self.csv_meta.tags_header = choice(self.csv_meta.headers, 'Hanfor_Tags')
            print('Select the Hanfor Status header.')
            self.csv_meta.status_header = choice(self.csv_meta.headers, 'Hanfor_Status')

        print('Do you want to import a base Variable collection?')
        if choice(['no', 'yes'], 'yes') == 'yes':
            available_sessions = [s for s in available_sessions]
            available_sessions_names = [s['name'] for s in available_sessions]
            if len(available_sessions_names) > 0:
                print('Choose the Variable Collection to import.')
                chosen_session = choice(available_sessions_names, available_sessions_names[0])
                print('Choose the revision for session {}'.format(chosen_session))
                available_revisions = [r for r in available_sessions[
                    available_sessions_names.index(chosen_session)
                ]['revisions']]
                revision_choice = choice(available_revisions, available_revisions[0])
                imported_var_collection = VariableCollection.load(
                    os.path.join(
                        app.config['SESSION_BASE_FOLDER'],
                        chosen_session,
                        revision_choice,
                        'session_variable_collection.pickle'
                    )
                )
                imported_var_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
            else:
                print('No sessions available. Skipping')

    def parse_csv_rows_into_requirements(self, app):
        """ Parse each row in csv_all_rows into one Requirement.

        Args:
            app (Flask): Hanfor Flask app..

        """
        for index, row in enumerate(self.csv_all_rows):
            # Todo: Use utils.slugify to make the rid save for a filename.
            requirement = Requirement(
                id=row[self.csv_meta.id_header],
                description=try_cast_string(row[self.csv_meta.desc_header]),
                type_in_csv=try_cast_string(row[self.csv_meta.type_header]),
                csv_row=row,
                pos_in_csv=index
            )
            if self.csv_meta.import_formalizations:
                # Set the tags
                if self.csv_meta.tags_header is not None:
                    tags = {t.strip(): "" for t in row[self.csv_meta.tags_header].split(',')}
                    requirement.tags.update(tags)
                # Set the status
                if self.csv_meta.status_header is not None:
                    status = row[self.csv_meta.status_header].strip()
                    if status not in ['Todo', 'Review', 'Done']:
                        logging.debug('Status {} not supported. Set to `Todo`'.format(status))
                        status = 'Todo'
                    requirement.status = status
                # Parse and set the requirements.
                formalizations = json.loads(row[self.csv_meta.formal_header])
                for key, formalization_dict in formalizations.items():
                    formalization = Formalization(int(key))
                    requirement.formalizations[int(key)] = formalization
                    requirement.update_formalization(
                        formalization_id=int(key),
                        scope_name=formalization_dict['scope'],
                        pattern_name=formalization_dict['pattern'],
                        mapping=formalization_dict['expressions'],
                        app=app
                    )

            self.requirements.append(requirement)


class Requirement(HanforVersioned, Pickleable):
    def __init__(self, id: str, description: str, type_in_csv: str, csv_row: dict[str, str], pos_in_csv: int):
        HanforVersioned.__init__(self)
        Pickleable.__init__(self, None)
        self.rid: str = id
        self.formalizations: Dict[int, Formalization] = dict()
        self.description = description
        self.type_in_csv = type_in_csv
        self.csv_row = csv_row
        self.pos_in_csv = pos_in_csv
        self.tags: OrderedDict[str, str] = OrderedDict()
        self.status = 'Todo'
        self._revision_diff = dict()

    def to_dict(self, include_used_vars=False):
        type_inference_errors = dict()
        used_variables = set()
        for index, f in self.formalizations.items():
            if f.type_inference_errors:
                type_inference_errors[index] = [key.lower() for key in f.type_inference_errors.keys()]
            if include_used_vars:
                for name in f.used_variables:
                    used_variables.add(name)

        d = {
            'id': self.rid,
            'desc': self.description,
            # Typecheck is for downwards compatibility (please do not remove)
            'type': self.type_in_csv if isinstance(self.type_in_csv, str) else "None",
            'tags': list(self.tags.keys()), 
            'tags_comments': self.tags,
            'formal': [f.get_string() for f in self.formalizations.values()],
            'scope': 'None',  # TODO: remove: This is obsolete since a requirement can hold multiple Formalizations.
            'pattern': 'None',  # TODO: remove: This is obsolete since a requirement can hold multiple Formalizations.
            'vars': sorted([name for name in used_variables]),
            'pos': self.pos_in_csv,
            'status': self.status,
            'csv_data': self.csv_row,
            'type_inference_errors': type_inference_errors,
            'revision_diff': self.revision_diff
        }
        return d

    @classmethod
    def load_requirement_by_id(cls, id: str, app) -> 'Requirement':
        """ Loads requirement from session folder if it exists.

        :param id: requirement_id
        :type id: str
        :param app: The flask app.
        :rtype: Requirement
        """
        path = os.path.join(app.config['REVISION_FOLDER'], f'{id}.pickle')
        if os.path.exists(path) and os.path.isfile(path):
            return Requirement.load(path)

    @classmethod
    def load(cls, path):
        me = Pickleable.load(path)
        if not isinstance(me, cls):
            raise TypeError

        if me.outdated:
            logging.info(f'`{me}` needs upgrade `{me.hanfor_version}` -> `{__version__}`')
            me.run_version_migrations()
            me.store()

        return me

    @classmethod
    def requirements(cls):
        """ Iterator for all requirements."""
        filenames = get_filenames_from_dir(current_app.config['REVISION_FOLDER'])
        for filename in filenames:
            try:
                yield cls.load(filename)
            except Exception:
                logging.error(f'Loading {filename} failed spectacularly!')

    def store(self, path=None):
        super().store(path)

    @property
    def revision_diff(self) -> Dict[str, str]:
        if not hasattr(self, '_revision_diff'):
            self._revision_diff = dict()
        return self._revision_diff

    @revision_diff.setter
    def revision_diff(self, other):
        """ Compute and set diffs based on `other` Requirement

        :param other: Requirement the diff should be based on.
        """
        self._revision_diff = dict()
        for csv_key in self.csv_row.keys():
            if csv_key not in other.csv_row.keys():
                other.csv_row[csv_key] = ''
            if self.csv_row[csv_key] is None:
                # This can happen if we revision with an CSV that is missing the csv_key now.
                self.csv_row[csv_key] = ''
            diff = difflib.ndiff(other.csv_row[csv_key].splitlines(), self.csv_row[csv_key].splitlines())
            diff = [s for s in diff if not s.startswith('  ')]
            diff = '\n'.join(diff)
            if len(diff) > 0:
                self._revision_diff[csv_key] = diff

    def _next_free_formalization_id(self):
        i = 0
        while i in self.formalizations.keys():
            i += 1
        return i

    def add_empty_formalization(self) -> Tuple[int, 'Formalization']:
        """ Add an empty formalization to the formalizations list."""
        id = self._next_free_formalization_id()
        self.formalizations[id] = Formalization(id)
        return id, self.formalizations[id]

    def delete_formalization(self, formalization_id, app):
        formalization_id = int(formalization_id)
        variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        # Remove formalization
        del self.formalizations[formalization_id]
        # Collect remaining vars.
        remaining_vars = set()
        for formalization in self.formalizations.values():
            for expression in formalization.expressions_mapping.values():
                if expression.used_variables is not None:
                    remaining_vars = remaining_vars.union(expression.used_variables)

        # Update the mappings.
        variable_collection.req_var_mapping[self.rid] = remaining_vars
        variable_collection.var_req_mapping = variable_collection.invert_mapping(variable_collection.req_var_mapping)
        variable_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])

    def update_formalization(self, formalization_id, scope_name, pattern_name, mapping, app, variable_collection=None):
        if variable_collection is None:
            variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        # set scoped pattern
        self.formalizations[formalization_id].scoped_pattern = ScopedPattern(
            Scope[scope_name], Pattern(name=pattern_name)
        )
        # set parent
        self.formalizations[formalization_id].belongs_to_requirement = self.rid
        # Parse and set the expressions.
        self.formalizations[formalization_id].set_expressions_mapping(mapping=mapping,
                                                                      variable_collection=variable_collection,
                                                                    rid=self.rid)
        # Run type inference check
        # Add 'Type_inference_error' tag
        if len(self.formalizations[formalization_id].type_inference_errors) > 0:
            formatted_errors = self.format_error_tag(self.formalizations[formalization_id])
            self.tags['Type_inference_error'] = formatted_errors

        # Add 'unknown_type' tag
        vars_with_unknown_type = []
        vars_with_unknown_type = self.formalizations[formalization_id].unknown_types_check(variable_collection,
                                                                                           vars_with_unknown_type)
        if vars_with_unknown_type:
            self.tags['unknown_type'] = self.format_unknown_type_tag(vars_with_unknown_type)

        if (self.formalizations[formalization_id].scoped_pattern.scope != Scope.NONE and
                self.formalizations[formalization_id].scoped_pattern.pattern.name != "NotFormalizable"):
                self.tags['has_formalization'] = ""
        else:
            self.tags['incomplete_formalization'] = self.format_incomplete_formalization_tag(formalization_id)
            
    def format_error_tag(self, formalisation: 'Formalization') -> str:
        if not self.tags.get('Type_inference_error'):
            result = ""
        else:
            result = self.tags.get('Type_inference_error')

        if not formalisation.type_inference_errors:
            return result
        for key, value in formalisation.type_inference_errors.items():
            result += f"{str(formalisation.belongs_to_requirement)}_{str(formalisation.id)} ({key}): \n- "
            result += "\n- ".join(value) + "\n"
        return result

    def format_unknown_type_tag(self, vars) -> str:
        return ", ".join(sorted(vars))

    def format_incomplete_formalization_tag(self, fid: int) -> str:
        rid_fid = self.rid + "_" + fid.__str__()
        if not self.tags.get('incomplete_formalization'):
            return "- " + rid_fid
        else:
            return self.tags.get('incomplete_formalization') + "\n- " + rid_fid

    def update_formalizations(self, formalizations: dict, app):
        if 'Type_inference_error' in self.tags:
            self.tags.pop('Type_inference_error')
        if 'unknown_type' in self.tags:
            self.tags.pop('unknown_type')
        if 'incomplete_formalization' in self.tags:
            self.tags.pop('incomplete_formalization')
        if 'has_formalization' in self.tags:
            self.tags.pop('has_formalization')
        logging.debug(f'Updating formalisations of requirement {self.rid}.')
        variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
        # Reset the var mapping.
        variable_collection.req_var_mapping[self.rid] = set()

        for formalization in formalizations.values():
            logging.debug(f"Updating formalization No. {formalization['id']}.")
            logging.debug(f"Scope: `{formalization['scope']}`, Pattern: `{formalization['pattern']}`.")
            try:
                self.update_formalization(
                    formalization_id=int(formalization['id']),
                    scope_name=formalization['scope'],
                    pattern_name=formalization['pattern'],
                    mapping=formalization['expression_mapping'],
                    app=app,
                    variable_collection=variable_collection
                )
            except Exception as e:
                logging.error(f'Could not update Formalization: {e.__str__()}')
                raise e

    def run_type_checks(self, var_collection):
        logging.info(f'Run type inference and unknown check for `{self.rid}`')
        if 'Type_inference_error' in self.tags:
            self.tags.pop('Type_inference_error')
        if 'unknown_type' in self.tags:
            self.tags.pop('unknown_type')
        vars_with_unknown_type = []
        for id in self.formalizations.keys():
            # Run type inference check
            self.formalizations[id].type_inference_check(var_collection)
            if len(self.formalizations[id].type_inference_errors) > 0:
                self.tags['Type_inference_error'] = self.format_error_tag(self.formalizations[id])

            # Check for variables of type 'unknown' in formalization
            vars_with_unknown_type = self.formalizations[id].unknown_types_check(var_collection, vars_with_unknown_type)
            if vars_with_unknown_type:
                self.tags['unknown_type'] = self.format_unknown_type_tag(vars_with_unknown_type)
        self.store()

    def get_formalizations_json(self) -> str:
        """ Fetch all formalizations in json format. Used to reload formalizations.

        Returns:
            str: The json formatted version of the formalizations.

        """
        result = dict()
        for key, formalization in self.formalizations.items():
            if formalization.scoped_pattern is None:
                continue
            result[str(key)] = formalization.to_dict()

        return json.dumps(result, sort_keys=True)

    def run_version_migrations(self):
        if self.hanfor_version == '0.0.0':
            logging.info(f'Migrating `{self.__class__.__name__}`:`{self.rid}`, from 0.0.0 -> 1.0.0')
            # Migrate list formalizations to use dict
            self.hanfor_version = '1.0.0'
            if type(self.formalizations) is list:
                self.formalizations = dict(enumerate(self.formalizations))
            self.store()
        super().run_version_migrations()

    def uses_var(self, var_name):
        """ Test is var_name is used in one of the requirements formalizations.

        :param var_name: The variable name.
        :return: True if var_name occurs at least once.
        """
        result = False
        for formalization in self.formalizations.values():  # type: Formalization
            if var_name in formalization.used_variables:
                result = True
                break
        return result


class Formalization(HanforVersioned):
    def __init__(self, id: int):
        super().__init__()
        self.id: int = id
        self.scoped_pattern = ScopedPattern()
        self.expressions_mapping: dict[str, Expression] = dict()
        self.belongs_to_requirement = None
        self.type_inference_errors = dict()

    @property
    def used_variables(self):
        result = []
        for exp in self.expressions_mapping.values():  # type: Expression
            result += exp.used_variables
        return list(set(result))

    def set_expressions_mapping(self, mapping, variable_collection, rid):
        """ Parse expression mapping.
            + Extract variables. Replace by their ID. Create new Variables if they do not exist.
            + For used variables and update the "used_by_requirements" set.

        :type mapping: dict
        :param mapping: {'P': 'foo > 0', 'Q': 'expression for Q', ...}
        :type variable_collection: VariableCollection
        :param variable_collection: Currently used VariableCollection.
        :type rid: str
        :param rid: associated requirement id

        :return: type_inference_errors dict {key: type_env, ...}
        :rtype: dict
        """
        if self.expressions_mapping is None:
            self.expressions_mapping = dict()
        for key, expression_string in mapping.items():
            expression = Expression()
            if key in self.scoped_pattern.environment:
                expression.set_expression(expression_string, variable_collection, rid)
            self.expressions_mapping[key] = expression
        self.get_string()
        self.type_inference_check(variable_collection)

    def type_inference_check(self, variable_collection):
        """ Apply type inference check for the expressions in this formalization.
        Reload if applied multiple times.

        :param variable_collection: The current VariableCollection
        """
        allowed_types = self.scoped_pattern.get_allowed_types()
        var_env = variable_collection.get_boogie_type_env()

        for key, expression in self.expressions_mapping.items():
            # We can only check type inference,
            # if the pattern has declared allowed types for the current pattern key e.g. `P`
            if key not in allowed_types.keys():
                continue

            # Check if the given expression can be parsed by lark.
            # Else there is a syntax error in the expression.
            try:
                tree = boogie_parsing.get_parser_instance().parse(expression.raw_expression)
            except LarkError as e:
                logging.error(
                    f'Lark could not parse expression `{expression.raw_expression}`: \n {e}. Skipping type inference')
                continue
            expression.set_expression(expression.raw_expression, variable_collection, expression.parent_rid)

            # Derive type for variables in expression and update missing or changed types.
            ti = run_typecheck_fixpoint(tree, var_env, expected_types=allowed_types[key])
            expression_type, type_env, type_errors = ti.type_root.t, ti.type_env, ti.type_errors

            # Add type error if a variable is used in a timing expression
            if allowed_types[key] != [BoogieType.bool]:
                for var in expression.used_variables:
                    if variable_collection.collection[var].type != 'CONST':
                        type_errors.append(f"Variable '{var}' used in time bound.")

            for name, var_type in type_env.items():  # Update the hanfor variable types.
                if (variable_collection.collection[name].type
                        and variable_collection.collection[name].type.lower() in ['const', 'enum']):
                    continue
                if variable_collection.collection[name].type not in boogie_parsing.BoogieType.aliases(var_type):
                    logging.info(f'Update variable `{name}` with derived type. '
                                 f'Old: `{variable_collection.collection[name].type}` => New: `{var_type.name}`.')
                    variable_collection.set_type(name, var_type.name)
            if type_errors:
                self.type_inference_errors[key] = type_errors
            elif key in self.type_inference_errors:
                # TODO: refactor the whole error handling process, as this gets too complex
                del self.type_inference_errors[key]
        variable_collection.store()

    def unknown_types_check(self, variable_collection, unknowns):
        for k, v in self.expressions_mapping.items():
            for var in v.used_variables:
                if variable_collection.get_type(var) == BoogieType.unknown.name:
                    unknowns.append(var)
        return unknowns

    def to_dict(self):
        d = {
            'scope': self.scoped_pattern.scope.name,
            'pattern': self.scoped_pattern.pattern.name,
            'expressions': {key: exp.raw_expression for key, exp in self.expressions_mapping.items()}
        }

        return d

    def get_string(self):
        return self.scoped_pattern.get_string(self.expressions_mapping)


class Expression(HanforVersioned):
    """ Representing an Expression in a ScopedPattern.
    For example: Let
       `Globally, {P} is always true.`
    be a Scoped pattern. One might replace {P} by
        `NO_PAIN => NO_GAIN`
    Then `NO_PAIN => NO_GAIN` is the Expression.
     """

    def __init__(self):
        super().__init__()
        self.used_variables: list[str] = list()
        self.raw_expression = None
        self.parent_rid = None

    def set_expression(self, expression: str, variable_collection: 'VariableCollection', parent_rid):
        """ Parses the Expression using the boogie grammar.
            * Extract variables.
                + Create new ones if not in Variable collection.
                + Replace Variables by their identifier.
            * Store set of used variables to `self.used_variables`
        """
        self.raw_expression = expression
        self.parent_rid = parent_rid
        logging.debug(f'Setting expression: `{expression}`')
        # Get the vars occurring in the expression.
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(expression)

        self.used_variables = set(boogie_parsing.get_variables_list(tree))

        new_vars = []
        for var_name in self.used_variables:
            if var_name not in variable_collection:
                variable_collection.add_var(var_name)
                new_vars.append(var_name)

        # TODO: restore if needed, not clear what this does
        # further app was not always available here, thus this has to be refactored
        # if len(new_vars) > 0:
        #    variable_collection.reload_script_results(app, new_vars)

        variable_collection.map_req_to_vars(parent_rid, self.used_variables)
        # try:
        #    variable_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
        # except:
        #    pass

    def __str__(self):
        return f'"{self.raw_expression}"'


class Scope(Enum):
    GLOBALLY = 'Globally'
    BEFORE = 'Before "{P}"'
    AFTER = 'After "{P}"'
    BETWEEN = 'Between "{P}" and "{Q}"'
    AFTER_UNTIL = 'After "{P}" until "{Q}"'
    NONE = '// None'

    def instantiate(self, *args):
        return str(self.value).format(*args)

    def get_slug(self):
        """ Returns a short slug representing the scope value.
        Use in applications where you don't want to use the full string.

        :return: Slug like AFTER_UNTIL for 'After "{P}" until "{Q}"'
        :rtype: str
        """
        slug_map = {
            str(self.GLOBALLY): 'GLOBALLY',
            str(self.BEFORE): 'BEFORE',
            str(self.AFTER): 'AFTER',
            str(self.BETWEEN): 'BETWEEN',
            str(self.AFTER_UNTIL): 'AFTER_UNTIL',
            str(self.NONE): 'NONE'
        }
        return slug_map[self.__str__()]

    def __str__(self):
        result = str(self.value).replace('"', '')
        return result

    def get_allowed_types(self):
        scope_env = {
            'GLOBALLY': {
            },
            'BEFORE': {
                'P': [boogie_parsing.BoogieType.bool]
            },
            'AFTER': {
                'P': [boogie_parsing.BoogieType.bool]
            },
            'BETWEEN': {
                'P': [boogie_parsing.BoogieType.bool],
                'Q': [boogie_parsing.BoogieType.bool]
            },
            'AFTER_UNTIL': {
                'P': [boogie_parsing.BoogieType.bool],
                'Q': [boogie_parsing.BoogieType.bool]
            },
            'NONE': {
            }
        }
        return scope_env[self.name]


class Pattern:
    def __init__(self, name: str = "NotFormalizable"):
        self.name = name
        self.environment = PATTERNS[name]["env"]
        self.pattern = PATTERNS[name]['pattern']

    def is_instantiatable(self):
        return self.name != "NotFormalizable"

    def instantiate(self, scope, *args):
        return scope + ', ' + self.pattern.format(*args)

    def __str__(self):
        return self.pattern

    def get_allowed_types(self):
        return BoogieType.alias_env_to_instantiated_env(
            PATTERNS[self.name]['env']
        )


class ScopedPattern:
    def __init__(self, scope: Scope = Scope.NONE, pattern: Pattern = None):
        self.scope = scope
        if not pattern:
            pattern = Pattern()
        self.pattern = pattern
        self.regex_pattern = None
        self.environment = pattern.environment | scope.get_allowed_types()

    def get_string(self, expression_mapping: dict):
        #TODO: avoid having this problem in the first place
        try:
            return self.__str__().format(**expression_mapping).replace('\n', ' ').replace('\r', ' ')
        except KeyError as e:
            logging.error(f"Pattern {self.pattern.name}: insufficient "
                          f"keys in expression mapping {str(expression_mapping)}")
        return "Pattern error - please delete formalisation."


    def is_instantiatable(self) -> bool:
        return self.scope != Scope.NONE and self.pattern.is_instantiatable()

    def instantiate(self, *args):
        return self.pattern.instantiate(self.scope, *args)

    def regex(self):
        if self.regex_pattern is not None:
            return self.regex_pattern

        fmt = string.Formatter()
        fields = set()
        literal_str = self.__str__()
        for (_, field_name, _, _) in fmt.parse(literal_str):
            fields.add(field_name)
        fields.remove(None)

        for f in fields:
            literal_str = literal_str.replace('"{{{}}}"'.format(f), r'"([\d\w\s"-]*)"')

        self.regex_pattern = literal_str
        return self.regex_pattern

    def get_scope_slug(self):
        if self.scope:
            return self.scope.get_slug()
        return "None"

    def get_pattern_slug(self):
        if self.pattern:
            return self.pattern.name
        return "None"

    def __str__(self):
        return str(self.scope) + ', ' + str(self.pattern)

    def get_allowed_types(self):
        result = self.scope.get_allowed_types()
        result.update(self.pattern.get_allowed_types())
        return result


class VariableCollection(HanforVersioned, Pickleable):
    def __init__(self, path):
        HanforVersioned.__init__(self)
        Pickleable.__init__(self, path)
        self.collection: Dict[str, Variable] = dict()
        self.req_var_mapping = dict()
        self.var_req_mapping = dict()

    def __contains__(self, item):
        return item in self.collection.keys()

    @classmethod
    def load(cls, path) -> 'VariableCollection':
        me = Pickleable.load(path)
        if not isinstance(me, cls):
            raise TypeError

        if me.outdated:
            logging.info(f'`{me}` needs upgrade `{me.hanfor_version}` -> `{__version__}`')
            me.run_version_migrations()
            me.store()

        return me

    def get_available_vars_list(self, sort_by=None, used_only=False, exclude_types=frozenset()):
        """ Returns a list of all available var names."""

        def in_result(var) -> bool:
            if used_only:
                if var.name not in self.var_req_mapping.keys():
                    return False
                if len(self.var_req_mapping[var.name]) == 0:
                    return False
            if var.type in exclude_types:
                return False

            return True

        result = [
            var.to_dict(self.var_req_mapping)
            for var in self.collection.values()
            if in_result(var)
        ]

        if len(result) > 0 and sort_by is not None and sort_by in result[0].keys():
            result = sorted(result, key=lambda k: k[sort_by])

        return result

    def get_available_var_names_list(self, used_only=True, exclude_types=frozenset()):
        return [var['name'] for var in self.get_available_vars_list(used_only=used_only, exclude_types=exclude_types)]

    def var_name_exists(self, name):
        return name in self.collection.keys()

    def add_var(self, var_name, variable=None):
        if not self.var_name_exists(var_name):
            if variable is None:
                variable = Variable(var_name, None, None)
            logging.debug(f'Adding variable `{var_name}` to collection.')
            self.collection[variable.name] = variable

    def store(self, path=None):
        self.var_req_mapping = self.invert_mapping(self.req_var_mapping)
        super().store(path)

    def invert_mapping(self, mapping):
        newdict = {}
        for k in mapping:
            for v in mapping[k]:
                newdict.setdefault(v, set()).add(k)
        return newdict

    def map_req_to_vars(self, rid, used_variables):
        """ Map a requirement by rid to used vars."""

        if rid not in self.req_var_mapping.keys():
            self.req_var_mapping[rid] = set()
        for var in used_variables:
            self.req_var_mapping[rid].add(var)

    def rename(self, old_name: str, new_name: str, app):
        """ Rename a var in the collection. Merges the variables if new_name variable exists.

        :param old_name: The old var name.
        :param new_name: The new var name.
        :returns affected_enumerators List [(old_enumerator_name, new_enumerator_name)] of potentially affected
        enumerators.
        """
        logging.info(f'Rename `{old_name}` -> `{new_name}`')
        # Store constraints to restore later on.
        tmp_constraints = []
        if old_name in self.collection:
            tmp_constraints += self.collection[old_name].get_constraints().values()
        if new_name in self.collection:
            tmp_constraints += self.collection[new_name].get_constraints().values()
        tmp_constraints = dict(enumerate(tmp_constraints))

        # Copy to new location.
        self.collection[new_name] = self.collection.pop(old_name)
        # Update name to new name (rename also triggers to update constraint names.)
        self.collection[new_name].rename(new_name)
        # Copy back back Constraints
        self.collection[new_name].constraints = tmp_constraints

        # Update the mappings.
        # Copy old to new mapping
        self.var_req_mapping[new_name] = self.var_req_mapping \
            .pop(old_name, set()) \
            .union(self.var_req_mapping.pop(new_name, set()))

        # Rename
        # Todo: this is inefficient. Parse the var name from constraint name to limit only for affected vars.
        for affected_var_name in self.collection.keys():
            try:
                self.collection[affected_var_name].rename_var_in_constraints(old_name, new_name)
            except Exception as e:
                logging.debug(f'`{affected_var_name}` constraints not updatable: {e}')

        # Update the constraint names if any
        def rename_constraint(name: str, old_name: str, new_name: str):
            match = re.match(Variable.CONSTRAINT_REGEX, name)
            if match is not None and match.group(2) == old_name:
                return name.replace(old_name, new_name)
            return name

        # Todo: this is even more inefficient :-(
        for key in self.var_req_mapping.keys():
            self.var_req_mapping[key] = {rename_constraint(name, old_name, new_name) for name in
                                         self.var_req_mapping[key]}

        # Update the req -> var mapping.
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)

        # Update the variable script results.
        self.reload_script_results(app, [new_name])

        # Rename the enumerators in case this renaming affects an enum.
        affected_enumerators = []
        if self.collection[new_name].type in ['ENUM_INT', 'ENUM_REAL']:
            for var in self.collection.values():
                if var.belongs_to_enum == old_name:
                    var.belongs_to_enum = new_name
                    old_enumerator_name = var.name
                    new_enumerator_name = replace_prefix(var.name, old_name, new_name)
                    affected_enumerators.append((old_enumerator_name, new_enumerator_name))
        for old_enumerator_name, new_enumerator_name in affected_enumerators:
            self.rename(old_enumerator_name, new_enumerator_name, app)
        return affected_enumerators

    def get_boogie_type_env(self):
        mapping = {
            'bool': boogie_parsing.BoogieType.bool,
            'int': boogie_parsing.BoogieType.int,
            'enum_int': boogie_parsing.BoogieType.int,
            'enum_real': boogie_parsing.BoogieType.real,
            'enumerator_int': boogie_parsing.BoogieType.int,
            'enumerator_real': boogie_parsing.BoogieType.real,
            'real': boogie_parsing.BoogieType.real,
            'unknown': boogie_parsing.BoogieType.unknown,
            'error': boogie_parsing.BoogieType.error
        }
        type_env = dict()
        for name, var in self.collection.items():
            if var.type is None:
                type_env[name] = mapping['unknown']
            elif var.type.lower() in mapping.keys():
                type_env[name] = mapping[var.type.lower()]
            elif var.type == 'CONST':
                # Check for int, real or unknown based on value.
                try:
                    float(var.value)
                except Exception:
                    type_env[name] = mapping['unknown']
                    continue

                if '.' in var.value:
                    type_env[name] = mapping['real']
                    continue

                type_env[name] = mapping['int']
            else:
                type_env[name] = mapping['unknown']

        # Todo: Store this so we can reuse and update on collection change.
        return type_env

    def enum_type_mismatch(self, enum, type):
        enum_type = self.collection[enum].type
        accepted_type = replace_prefix(enum_type, 'ENUM', 'ENUMERATOR')

        return not type == accepted_type

    def set_type(self, name, type):
        if type in ['ENUMERATOR_INT', 'ENUMERATOR_REAL']:
            if self.enum_type_mismatch(self.collection[name].belongs_to_enum, type):
                raise TypeError('ENUM type mismatch')

        self.collection[name].set_type(type)

    def get_type(self, name):
        return self.collection[name].type

    def add_new_constraint(self, var_name):
        """ Add a new empty constraint to var_name variable.
        :type var_name: str
        :param var_name:
        """
        return self.collection[var_name].add_constraint()

    def del_constraint(self, var_name, constraint_id):
        self.req_var_mapping.pop('Constraint_{}_{}'.format(var_name, constraint_id), None)
        return self.collection[var_name].del_constraint(constraint_id)

    def refresh_var_constraint_mapping(self):
        def not_in_constraint(var_name, constraint_name):
            """ Checks if var_name is used in constraint_name (if constraint_name is existing).

            :param var_name:
            :param constraint_name:
            :return:
            """
            match = re.match(Variable.CONSTRAINT_REGEX, constraint_name)
            if match:
                constraint_variable_name = match.group(2)
                if constraint_variable_name not in self.collection.keys():
                    # The referenced variable is no longer existing.
                    try:
                        self.req_var_mapping[constraint_name].discard(var_name)
                    except Exception:
                        pass
                    return True
                else:
                    # The variable exists. Now check if var_name occurs in one of its constraints.
                    for constraint in self.collection[constraint_variable_name].get_constraints().values():
                        if var_name in constraint.get_string():
                            return False
                    try:
                        self.req_var_mapping[constraint_name].discard(var_name)
                    except Exception:
                        pass
                    return True

            return False

        for name, variable in self.collection.items():
            if name in self.var_req_mapping:
                self.var_req_mapping[name] = {
                    c_name for c_name in self.var_req_mapping[name] if not not_in_constraint(name, c_name)
                }

    def reload_type_inference_errors_in_constraints(self):
        for name, var in self.collection.items():
            if len(var.get_constraints()) > 0:
                var.reload_constraints_type_inference_errors(self)
                self.collection[name] = var

    def refresh_var_usage(self, app):
        filenames = get_filenames_from_dir(app.config['REVISION_FOLDER'])
        mapping = dict()

        # Add the requirements using this variable.
        for filename in filenames:
            try:
                req = Requirement.load(filename)
            except TypeError:
                continue
            for formalization in req.formalizations.values():
                try:
                    for var_name in formalization.used_variables:
                        if var_name not in mapping.keys():
                            mapping[var_name] = set()
                        mapping[var_name].add(req.rid)
                except TypeError:
                    pass
                except Exception as e:
                    logging.info('Could not read formalizations for `{}`: {}'.format(req.rid, e))
                    raise e

        # Add the constraints using this variable.
        for var in self.collection.values():
            for constraint in var.get_constraints().values():
                for constraint_id, expression in enumerate(constraint.expressions_mapping.values()):
                    for var_name in expression.used_variables:
                        if var_name not in mapping.keys():
                            mapping[var_name] = set()
                        mapping[var_name].add('Constraint_{}_{}'.format(var.name, constraint_id))

        self.var_req_mapping = mapping

    def del_var(self, var_name) -> bool:
        """ Delete a variable if it is not used, or only used by its own constraints.

        :param var_name:
        :return: True on deletion else False.
        """
        deletable = False
        if var_name not in self.var_req_mapping:
            deletable = True
        else:
            constraint_pref = 'Constraint_{}'.format(var_name)
            affected_constraints = len([f for f in self.var_req_mapping[var_name] if constraint_pref in f])
            total_usages = len(self.var_req_mapping[var_name])
            if affected_constraints == total_usages:
                deletable = True

        if deletable:
            self.collection.pop(var_name, None)
            self.var_req_mapping.pop(var_name, None)
            return True
        return False

    def get_enumerators(self, enum_name: str) -> list['Variable']:
        enumerators = []
        for other_var in self.collection.values():
            if other_var.belongs_to_enum == enum_name:
                enumerators.append(other_var)
        return enumerators

    def run_version_migrations(self):
        logging.info(
            f'Migrating `{self.__class__.__name__}`:`{self.my_path}`, from {self.hanfor_version} -> {__version__}')
        for name, variable in self.collection.items():  # type: (str, Variable)
            variable.run_version_migrations()
        if version.parse(self.hanfor_version) < version.parse('1.0.3'):
            # Migrate for introduction of ENUM_INT and ENUM_REAL.
            for name, variable in self.collection.items():  # type: (str, Variable)
                if variable.type == 'ENUM':
                    logging.info(f'Migrate old ENUM `{variable.name}` to new ENUM_INT, ENUM_REAL')
                    enumerators = []
                    for other_var_name, other_var in self.collection.items():  # type: str, Variable
                        if (len(other_var_name) > len(variable.name)
                                and other_var_name.startswith(variable.name)
                                and other_var.type == 'ENUMERATOR'):
                            enumerators.append(other_var_name)
                            # Set newly introduced belongs_to_enum.
                            other_var.belongs_to_enum = variable.name
                    # Determine the new type from the ENUMERATOR values.
                    new_type = 'INT'
                    for enumerator_name in enumerators:
                        try:
                            int(self.collection[enumerator_name].value)
                        except Exception:
                            new_type = 'REAL'
                    # Set new types.
                    variable.type = 'ENUM_{}'.format(new_type)
                    logging.info('Set type of `{}` to `{}`'.format(variable.name, variable.type))
                    for enumerator_name in enumerators:
                        self.collection[enumerator_name].type = 'ENUMERATOR_{}'.format(new_type)
                        logging.info('Set type of `{}` to `{}`'.format(
                            enumerator_name,
                            self.collection[enumerator_name].type
                        ))
        super().run_version_migrations()

    def script_eval(self, env, script_filename, script, params_config, var_names, app):
        with app.app_context():
            results = dict()
            for name in var_names:
                params = [param.replace('$VAR_NAME', name) for param in params_config]
                logging.debug('Eval script: `{}` using params `{}` for var `{}`'.format(
                    script_filename,
                    params,
                    name
                ))
                try:
                    result = subprocess.check_output(
                        [script] + params,
                        shell=True,
                        env=env,
                        stderr=subprocess.DEVNULL
                    ).decode()
                except subprocess.CalledProcessError as e:
                    result = 'Output: {}'.format(e.output.decode())
                results[name] = 'Results for `{}` <br> {} <br>'.format(
                    script_filename, result
                )
            logging.info('Store script eval for script: {}'.format(script_filename))

            # Update script_results.
            script_results = ScriptEvals.load(path=app.config['SCRIPT_EVAL_RESULTS_PATH'])
            script_results.update_evals(results, script_filename)
            script_results.store()

    def start_script_eval_thread(self, env, script_filename, script, params_config, var_names, app):
        Thread(
            target=self.script_eval,
            args=(env, script_filename, script, params_config, var_names, app)
        ).start()

    def reload_script_results(self, app, var_names=None):
        """ Run the script evaluations for the variables in this collection as set in the config.py

        :param var_names: Iterable object of variable names the script should be reevaluated. Uses all if None
        :param app: Hanfor flask app for context.
        """
        logging.info('Start variable script evaluations.')
        if var_names is None:
            var_names = self.collection.keys()

        if 'SCRIPT_EVALUATIONS' not in app.config:
            logging.info('No SCRIPT_EVALUATIONS settings found in config.py. Skipping variable script evaluations.')
            return

        # Prepare the subprocess to use our environment.
        env = os.environ.copy()
        env["PATH"] = "/usr/sbin:/sbin:" + env["PATH"]

        # Eval each script given by the config
        for script_filename, params_config in app.config['SCRIPT_EVALUATIONS'].items():
            # First load the script to prevent permission issues.
            try:
                script_path = os.path.join(app.config['SCRIPT_UTILS_PATH'], script_filename)
                with open(script_path, 'rb') as f:
                    script = f.read()
            except Exception as e:
                logging.error('Could not load `{}` to eval variable scrypt results: `{}`'.format(script_filename, e))
                continue
            self.start_script_eval_thread(
                env=env,
                script_filename=script_filename,
                script=script,
                params_config=params_config,
                var_names=var_names,
                app=app
            )

    def import_session(self, import_collection):
        """ Import another VariableCollection into this.

        :param import_collection: The other VariableCollection
        """
        for var_name, variable in import_collection.collection.items():
            if var_name in self.collection:
                pass
            else:
                self.collection[var_name] = variable


class Variable(HanforVersioned):
    CONSTRAINT_REGEX = r"^(Constraint_)(.*)(_[0-9]+$)"

    def __init__(self, name: str, type: str, value: str):
        super().__init__()
        self.name: str = name
        self.type: str = type
        self.value: str = value
        # TODO: Show variables (e.g. typing errors) or remove tags from variables; show them or remove them
        self.tags: set[str] = set()
        self.script_results: str = ''
        self.belongs_to_enum: str = ''
        self.constraints = dict()
        self.description: str = ''

    def to_dict(self, var_req_mapping):
        used_by = []
        type_inference_errors = dict()
        for index, f in self.get_constraints().items():
            if f.type_inference_errors:
                type_inference_errors[index] = [key.lower() for key in f.type_inference_errors.keys()]
        try:
            used_by = sorted(list(var_req_mapping[self.name]))
        except Exception:
            pass

        d = {
            'name': self.name,
            'type': self.type,
            'const_val': self.value,
            'used_by': used_by,
            'tags': list(self.get_tags()),
            'type_inference_errors': type_inference_errors,
            'constraints': [constraint.get_string() for constraint in self.get_constraints().values()],
            'script_results': self.script_results,
            'belongs_to_enum': self.belongs_to_enum
        }

        return d

    def add_tag(self, tag_name):
        self.tags.add(tag_name)

    def remove_tag(self, tag_name):
        self.tags.discard(tag_name)

    def get_tags(self):
        return self.tags

    def set_type(self, new_type):
        allowed_types = ['CONST']
        allowed_types += boogie_parsing.BoogieType.get_valid_type_names()
        if new_type not in allowed_types:
            raise ValueError(f'Illegal variable type: `{new_type}`. Allowed types are: `{allowed_types}`')

        self.type = new_type

    def _next_free_constraint_id(self):
        i = 0
        try:
            while i in self.constraints.keys():
                i += 1
        except Exception:
            pass
        return i

    def add_constraint(self):
        """ Add a new empty constraint

        :return: (index: int, The constraint: Formalization)
        """
        id = self._next_free_constraint_id()
        self.constraints[id] = Formalization(id)
        return id

    def del_constraint(self, id):
        try:
            del self.constraints[id]
            return True
        except Exception as e:
            logging.debug(f'Constraint id `{id}` not found in var `{self.name}`')
            return False

    def get_constraints(self):
        return self.constraints

    def reload_constraints_type_inference_errors(self, var_collection):
        logging.info(f'Reload type inference for variable `{self.name}` constraints')
        self.remove_tag('Type_inference_error')
        for id in self.constraints:
            try:
                self.constraints[id].type_inference_check(var_collection)
                if len(self.constraints[id].type_inference_errors) > 0:
                    self.tags.add('Type_inference_error')
            except AttributeError as e:
                # Probably No pattern set.
                logging.info(f'Could not derive type inference for variable `{self.name}` constraint No. {id}. { e}')

    def update_constraint(self, constraint_id, scope_name, pattern_name, mapping, variable_collection):
        """ Update a single constraint

        :param constraint_id:
        :param scope_name:
        :param pattern_name:
        :param mapping:
        :param variable_collection:
        :return:
        """
        # set scoped pattern
        self.constraints[constraint_id].scoped_pattern = ScopedPattern(
            Scope[scope_name], Pattern(name=pattern_name)
        )
        # Parse and set the expressions.
        for key, expression_string in mapping.items():
            if len(expression_string) == 0:
                continue
            expression = Expression()
            expression.set_expression(expression_string, variable_collection,
                                      'Constraint_{}_{}'.format(self.name, constraint_id))
            if self.constraints[constraint_id].expressions_mapping is None:
                self.constraints[constraint_id].expressions_mapping = dict()
            self.constraints[constraint_id].expressions_mapping[key] = expression
        self.constraints[constraint_id].get_string()
        self.constraints[constraint_id].type_inference_check(variable_collection)

        if len(self.constraints[constraint_id].type_inference_errors) > 0:
            logging.debug('Type inference Error in variable `{}` constraint `{}` at {}.'.format(
                self.name,
                constraint_id,
                [n for n in self.constraints[constraint_id].type_inference_errors.keys()]
            ))
            self.add_tag('Type_inference_error')

        variable_collection.collection[self.name] = self

        return variable_collection

    def update_constraints(self, constraints, app, variable_collection=None):
        """ replace all constraints with :param constraints.

        :return: updated VariableCollection
        """
        logging.debug(f"Updating constraints for variable `{self.name}`.")
        self.remove_tag('Type_inference_error')
        if variable_collection is None:
            variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        for constraint in constraints.values():
            logging.debug(f"Updating formalization No. {constraint['id']}.")
            logging.debug(f"Scope: `{constraint['scope']}`, Pattern: `{constraint['pattern']}`.")
            try:
                variable_collection = self.update_constraint(constraint_id=int(constraint['id']),
                                                             scope_name=constraint['scope'],
                                                             pattern_name=constraint['pattern'],
                                                             mapping=constraint['expression_mapping'],
                                                             variable_collection=variable_collection)
            except Exception as e:
                logging.error(f'Could not update Constraint: {e.__str__()}.')
                raise e

        return variable_collection

    def rename_var_in_constraints(self, old_name, new_name):
        # replace in every formalization
        for index, constraint in self.get_constraints().items():
            for key, expression in constraint.expressions_mapping.items():
                if old_name not in expression.raw_expression:
                    continue
                new_expression = boogie_parsing.replace_var_in_expression(
                    expression=expression.raw_expression,
                    old_var=old_name,
                    new_var=new_name
                )
                self.constraints[index].expressions_mapping[key].raw_expression = new_expression
                self.constraints[index].expressions_mapping[key].used_variables.discard(old_name)
                self.constraints[index].expressions_mapping[key].used_variables.add(new_name)

    def rename(self, new_name):
        old_name = self.name
        self.name = new_name
        self.rename_var_in_constraints(old_name, new_name)

    def get_parent_enum(self, variable_collection):
        """ Returns the parent enum in case this variable is an enumerator.

        :return: The parent enum name
        :param variable_collection:
        """
        result = ''
        if self.type == 'ENUMERATOR':
            for other_var_name in variable_collection.collection.keys():
                if (len(self.name) > len(other_var_name)
                        and variable_collection.collection[other_var_name].type == 'ENUM'
                        and self.name.startswith(other_var_name)):
                    result = other_var_name
                    break
        return result

    def get_enumerators(self, variable_collection):
        """ Returns a list of enumerator names, in case this variable is an enum.

        :param variable_collection:
        :return: List of enumerator names.
        """
        result = []
        if self.type == 'ENUM':
            for other_var_name in variable_collection.collection.keys():
                if (len(self.name) < len(other_var_name)
                        and variable_collection.collection[other_var_name].type == 'ENUMERATOR'
                        and other_var_name.startswith(self.name)):
                    result.append(other_var_name)
                    break
        return result

    def run_version_migrations(self):
        if version.parse(self.hanfor_version) <= version.parse('0.0.0'):
            logging.info(f'Migrating `{self.__class__.__name__}`:`{self.name}`, from 0.0.0 -> 1.0.0')
            if hasattr(self, 'constraints'):
                self.constraints = dict(enumerate(self.constraints))
            else:
                self.constraints = dict()
        if version.parse(self.hanfor_version) <= version.parse('1.0.0'):
            logging.info(f'Migrating `{self.__class__.__name__}`:`{self.name}`, from 1.0.0 -> 1.0.1')
            self.script_results = ''
        if version.parse(self.hanfor_version) <= version.parse('1.0.2'):
            logging.info(f'Migrating `{self.__class__.__name__}`:`{ self.name}`, from {self.hanfor_version} -> 1.0.3')
            self.belongs_to_enum = ''
            if self.type == 'ENUM':
                logging.info(f'Migrate old ENUM `{self.name}` to new ENUM_INT, ENUM_REAL')
        if not hasattr(self, 'constraints') or not isinstance(self.constraints, dict):
            setattr(self, 'constraints', dict())
        if not hasattr(self, 'description') or not isinstance(self.constraints, str):
            setattr(self, 'description', str())
        super().run_version_migrations()


class VarImportSession(HanforVersioned):
    def __init__(self, source_var_collection, target_var_collection):
        """

        :type source_var_collection: VariableCollection
        :type target_var_collection: VariableCollection
        """
        HanforVersioned.__init__(self)
        self.source_var_collection = source_var_collection
        self.target_var_collection = target_var_collection
        self.result_var_collection = deepcopy(target_var_collection)

        self.actions = dict()
        self.init_actions()

        self.available_constraints = dict()
        for name, vars in self.to_dict().items():
            av_dict = dict()
            i = 0
            if 'source' in vars:
                for j, c in self.source_var_collection.collection[name].get_constraints().items():
                    i += 1
                    av_dict[i] = {
                        'id': i,
                        'origin_id': j,
                        'constraint': c.get_string(),
                        'origin': 'source',
                        'to_result': False
                    }
            if 'target' in vars:
                for j, c in self.target_var_collection.collection[name].get_constraints().items():
                    i += 1
                    av_dict[i] = {
                        'id': i,
                        'origin_id': j,
                        'constraint': c.get_string(),
                        'origin': 'target',
                        'to_result': True
                    }
            self.available_constraints[name] = av_dict

    def init_actions(self):
        dict_data = self.to_dict()
        for name, data in dict_data.items():
            self.actions[name] = 'target' if 'target' in data else 'skipped'

    def to_dict(self):
        result = defaultdict(defaultdict)
        for name, variable in self.source_var_collection.collection.items():
            result[name]['source'] = variable.to_dict(self.source_var_collection.var_req_mapping)
        for name, variable in self.target_var_collection.collection.items():
            result[name]['target'] = variable.to_dict(self.target_var_collection.var_req_mapping)
        for name, variable in self.result_var_collection.collection.items():
            result[name]['result'] = variable.to_dict(self.result_var_collection.var_req_mapping)
        return result

    def to_datatables_data(self):
        dict_data = self.to_dict()
        result = list()
        for name, data in dict_data.items():
            result.append({
                'name': name,
                'available_constraints': self.available_constraints[name],
                'action': self.actions[name],
                'source': data['source'] if 'source' in data else {},
                'target': data['target'] if 'target' in data else {},
                'result': data['result'] if 'result' in data else {}
            })
        return result

    def store_changes(self, rows):
        for name, data in rows.items():
            self.actions[name] = data['action']
            if data['action'] == 'source':
                self.result_var_collection.collection[name] = deepcopy(self.source_var_collection.collection[name])
            if data['action'] == 'target':
                self.result_var_collection.collection[name] = deepcopy(self.target_var_collection.collection[name])
            for key in self.available_constraints[name].keys():
                self.available_constraints[name][key]['to_result'] = (
                        self.available_constraints[name][key]['origin'] == data['action']
                )

    def store_variable(self, row):
        self.actions[row['name']] = row['action']
        self.result_var_collection.collection[row['name']].set_type(row['result']['type'])
        self.available_constraints[row['name']] = row['available_constraints']
        try:
            const_val = int(row['result']['const_val'])
            self.result_var_collection.collection[row['name']].value = const_val
        except Exception:
            pass

    def apply_constraint_selection(self):
        used_variables = set()
        for var_name, available_constraints in self.available_constraints.items():
            if len(available_constraints) > 0 and var_name in self.result_var_collection.collection.keys():
                constraints = []
                for id, constraint in available_constraints.items():
                    if constraint['to_result']:
                        if constraint['origin'] == 'source':
                            constraints.append(deepcopy(
                                self.source_var_collection.collection[var_name].constraints[constraint['origin_id']]
                            ))
                        else:
                            constraints.append(deepcopy(
                                self.target_var_collection.collection[var_name].constraints[constraint['origin_id']]
                            ))
                self.result_var_collection.collection[var_name].constraints = dict(enumerate(constraints))
                # Collect used variables to auto include missing ones into the target.
                vars_in_constraint = set()
                for constraint in self.result_var_collection.collection[var_name].constraints.values():
                    for var in constraint.used_variables:
                        vars_in_constraint.add(var)
                used_variables |= vars_in_constraint

        # Include missing vars used by constraints.
        for var_name in used_variables:
            if var_name not in self.result_var_collection.collection:
                logging.debug('Var: `{}` not marked to be in result but used in a constraint -> auto include.'.format(
                    var_name
                ))
                if var_name in self.source_var_collection:
                    self.actions[var_name] = 'source'
                    self.result_var_collection.collection[var_name] = deepcopy(
                        self.source_var_collection.collection[var_name]
                    )
                if var_name in self.target_var_collection:
                    self.actions[var_name] = 'target'
                    self.result_var_collection.collection[var_name] = deepcopy(
                        self.target_var_collection.collection[var_name]
                    )

    def info(self):
        def get_path_info(path):
            path, file = os.path.split(path)
            path, revision = os.path.split(path)
            path, session = os.path.split(path)

            return file, revision, session

        info = dict()

        info['source'] = get_path_info(self.source_var_collection.my_path)
        info['target'] = get_path_info(self.target_var_collection.my_path)

        return info

    def run_version_migrations(self):
        logging.info(
            'Migrating `{}`:`{}` -> `{}`, from {} -> {}'.format(
                self.__class__.__name__,
                self.source_var_collection.my_path,
                self.target_var_collection.my_path,
                self.hanfor_version,
                __version__
            )
        )
        self.source_var_collection.run_version_migrations()
        self.target_var_collection.run_version_migrations()
        self.result_var_collection.run_version_migrations()
        super().run_version_migrations()


class VarImportSessions(HanforVersioned, Pickleable):
    def __init__(self, path=None):
        HanforVersioned.__init__(self)
        Pickleable.__init__(self, path)
        self.import_sessions: list[VarImportSession] = list()

    @classmethod
    def load(cls, path) -> 'VarImportSessions':
        me = Pickleable.load(path)
        if not isinstance(me, cls):
            raise TypeError

        if me.outdated:
            logging.info(f'`{me}` needs upgrade `{me.hanfor_version}` -> `{__version__}`')
            me.run_version_migrations()
            me.store()

        return me

    @classmethod
    def load_for_app(cls, session_base_path: str):
        var_import_sessions_path = os.path.join(
            session_base_path,
            'variable_import_sessions.pickle'
        )
        return VarImportSessions.load(var_import_sessions_path)

    def create_new_session(self, source_collection, target_collection):
        new_session = VarImportSession(
            source_var_collection=source_collection,
            target_var_collection=target_collection
        )
        self.import_sessions.append(new_session)
        self.store()
        return len(self.import_sessions) - 1

    def info(self):
        info = dict()

        for i, import_session in enumerate(self.import_sessions):
            session_info = import_session.info()
            info[i] = {
                'id': i,
                'source': session_info['source'],
                'target': session_info['target']
            }

        return info

    def run_version_migrations(self):
        logging.info(
            f'Migrating `{self.__class__.__name__}`:`{self.my_path}`, from {self.hanfor_version} -> {__version__}')
        for import_session in self.import_sessions:
            import_session.run_version_migrations()
        super().run_version_migrations()


class ScriptEvals(Pickleable):
    def __init__(self, path=None):
        self.evals = defaultdict(defaultdict)
        Pickleable.__init__(self, path)

    def update_evals(self, results: dict, script_name):
        for name, eval in results.items():
            self.evals[name].update({script_name: eval})

    def get_concatenated_evals(self):
        result = dict()
        for name, evals in self.evals.items():
            result[name] = ' '.join(sorted(evals.values()))

        return result
