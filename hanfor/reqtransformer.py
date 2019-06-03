""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import boogie_parsing
import csv
import difflib
import logging
import os
import pickle
import re
import string
import subprocess

from collections import defaultdict
from copy import deepcopy
from distutils.version import StrictVersion
from enum import Enum
from static_utils import choice, get_filenames_from_dir, replace_prefix
from threading import Thread
from typing import Dict

__version__ = '1.0.3'


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
    def has_version_mismatch(self) -> bool:
        return __version__ != self.hanfor_version

    def run_version_migrations(self):
        self._hanfor_version = __version__


class Pickleable:
    def __init__(self, path):
        self.my_path = path

    @classmethod
    def load(self, path):
        path_size = os.path.getsize(path)
        if not path_size > 0:
            raise AssertionError('Could not load object from `{}`. (path size is {})'.format(
                path, path_size
            ))
        with open(path, mode='rb') as f:
            me = pickle.load(f)
            if not isinstance(me, self):
                raise TypeError

        me.my_path = path

        return me

    def store(self, path=None):
        if path is not None:
            self.my_path = path

        with open(self.my_path, mode='wb') as out_file:
            pickle.dump(self, out_file)


class RequirementCollection(HanforVersioned, Pickleable):
    def __init__(self):
        HanforVersioned.__init__(self)
        Pickleable.__init__(self, None)
        self.csv_meta = {
            'dialect': None,
            'fieldnames': None,
            'headers': list(),
            'id_header': None,
            'desc_header': None,
            'formal_header': None,
            'type_header': None,
        }
        self.csv_all_rows = None
        self.requirements = list()

    def create_from_csv(self, csv_file, input_encoding='utf8', base_revision_headers=None):
        """ Create a RequirementCollection from a csv file, containing one requirement per line.
        Ask the user which csv fields corresponds to which requirement data.

        :param csv_file:
        :type csv_file:
        :param input_encoding:
        :type input_encoding:
        """
        self.load_csv(csv_file, input_encoding)
        self.select_headers(base_revision_headers)
        self.parse_csv_rows_into_requirements()

    def load_csv(self, csv_file, input_encoding):
        """ Reads a csv file into `csv_all_rows`. Stores csv_dialect and csv_fieldnames in `csv_meta`

        :param csv_file: Path to csv file.
        :type csv_file: str
        :param input_encoding: Encoding of the csv file.
        :type input_encoding: str
        """
        logging.info('Load Input : {}'.format(csv_file))
        with open(csv_file, 'r', encoding=input_encoding) as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(2048), delimiters='\t')
            except csv.Error:
                logging.info("Could not guess .csv dialect, assuming defaults")
                csv.register_dialect('ultimate', delimiter=',')
                dialect = 'ultimate'
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            self.csv_meta['dialect'] = dialect
            self.csv_all_rows = list(reader)
            self.csv_meta['fieldnames'] = reader.fieldnames
            self.csv_meta['headers'] = sorted(list(self.csv_all_rows[0].keys()))

    def select_headers(self, base_revision_headers=None):
        """ Ask the users, which of the csv headers correspond to our needed data.

        """
        use_old_headers = False
        if base_revision_headers:
            print('Should I use the csv header mapping from base revision?')
            use_old_headers = choice(['yes', 'no'], 'yes')
        if base_revision_headers and use_old_headers == 'yes':
            self.csv_meta['id_header'] = base_revision_headers['csv_id_header']
            self.csv_meta['desc_header'] = base_revision_headers['csv_desc_header']
            self.csv_meta['formal_header'] = base_revision_headers['csv_formal_header']
            self.csv_meta['type_header'] = base_revision_headers['csv_type_header']
        else:
            print('Select ID header')
            self.csv_meta['id_header'] = choice(self.csv_meta['headers'], 'ID')
            print('Select requirements description header')
            self.csv_meta['desc_header'] = choice(
                self.csv_meta['headers'],
                'System Requirement Specification of Audi Central Connected Getway'
            )
            print('Select formalization header')
            self.csv_meta['formal_header'] = choice(self.csv_meta['headers'] + ['Add new Formalization'],
                                                          'Formal Req')
            if self.csv_meta['formal_header'] == 'Add new Formalization':
                self.csv_meta['formal_header'] = 'Hanfor_Formalization'
            print('Select type header.')
            self.csv_meta['type_header'] = choice(self.csv_meta['headers'], 'RB_Classification')

    def parse_csv_rows_into_requirements(self):
        """ Parse each row in csv_all_rows into one Requirement.

        """
        for index, row in enumerate(self.csv_all_rows):
            # Todo: Use utils.slugify to make the rid save for a filename.
            requirement = Requirement(
                rid=row[self.csv_meta['id_header']],
                description=row[self.csv_meta['desc_header']],
                type_in_csv=row[self.csv_meta['type_header']],
                csv_row=row,
                pos_in_csv=index
            )
            self.requirements.append(requirement)


class Requirement(HanforVersioned, Pickleable):
    def __init__(self, rid, description, type_in_csv, csv_row, pos_in_csv):
        HanforVersioned.__init__(self)
        Pickleable.__init__(self, None)
        self.rid = rid
        self.formalizations = dict()
        self.description = description
        self.type_in_csv = type_in_csv
        self.csv_row = csv_row
        self.pos_in_csv = pos_in_csv
        self.tags = set()
        self.status = 'Todo'

    def to_dict(self):
        type_inference_errors = dict()
        for index, f in self.formalizations.items():
            if f.has_type_inference_errors():
                type_inference_errors[index] = [key.lower() for key in f.type_inference_errors.keys()]
        d = {
            'id': self.rid,
            'desc': self.description,
            'type': self.type_in_csv if type(self.type_in_csv) is str else self.type_in_csv[0],
            'tags': sorted([tag for tag in self.tags]),
            'formal': [f.get_string() for f in self.formalizations.values()],
            'scope': 'None',
            'pattern': 'None',
            'vars': dict(),
            'pos': self.pos_in_csv,
            'status': self.status,
            'csv_data': self.csv_row,
            'type_inference_errors': type_inference_errors,
            'revision_diff': self.revision_diff
        }
        return d

    @classmethod
    def load_requirement_by_id(self, id, app) -> 'Requirement':
        """ Loads requirement from session folder if it exists.

        :param id: requirement_id
        :type id: str
        :param app: The flask app.
        :rtype: Requirement
        """
        path = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(id))
        if os.path.exists(path) and os.path.isfile(path):
            return Requirement.load(path)

    @classmethod
    def load(self, path):
        me = Pickleable.load(path)
        if not isinstance(me, self):
            raise TypeError

        if me.has_version_mismatch:
            logging.info('`{}` needs upgrade `{}` -> `{}`'.format(
                me,
                me.hanfor_version,
                __version__
            ))
            me.run_version_migrations()
            me.store()

        return me

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
            if not csv_key in other.csv_row.keys():
                other.csv_row[csv_key] = ''
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

    def add_empty_formalization(self):
        """ Add an empty formalization to the formalizations list.

        :return: The id of the requirement (pos in list)
        :rtype: int
        """
        return self.add_formalization(Formalization())

    def add_formalization(self, formalization):
        """ Add given formalization to this requirement

        :type formalization: Formalization
        :param formalization: The Formalization
        :return: (int, Formalization) The formalization ID and the Formalization itself.
        """
        if self.formalizations is None:
            self.formalizations = dict()

        id = self._next_free_formalization_id()
        self.formalizations[id] = formalization

        return id, self.formalizations[id]

    def delete_formalization(self, formalization_id, app):
        formalization_id = int(formalization_id)
        variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        # Remove formalizatioin
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
        self.formalizations[formalization_id].set_expressions_mapping(
            mapping=mapping,
            variable_collection=variable_collection,
            app=app,
            rid=self.rid
        )
        if len(self.formalizations[formalization_id].type_inference_errors) > 0:
            logging.debug('Type inference Error in formalization at {}.'.format(
                [n for n in self.formalizations[formalization_id].type_inference_errors.keys()]
            ))
            self.tags.add('Type_inference_error')

    def update_formalizations(self, formalizations: dict, app):
        self.tags.discard('Type_inference_error')
        logging.debug('Updating formalizatioins of requirement {}.'.format(self.rid))
        variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
        # Reset the var mapping.
        variable_collection.req_var_mapping[self.rid] = set()

        for formalization in formalizations.values():
            logging.debug('Updating formalization No. {}.'.format(formalization['id']))
            logging.debug('Scope: `{}`, Pattern: `{}`.'.format(formalization['scope'], formalization['pattern']))
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
                logging.error('Could not update Formalization: {}'.format(e.__str__()))
                raise e

    def reload_type_inference(self, var_collection, app):
        logging.info('Reload type inference for `{}`'.format(self.rid))
        self.tags.discard('Type_inference_error')
        for id in self.formalizations.keys():
            try:
                self.formalizations[id].type_inference_check(var_collection)
                if len(self.formalizations[id].type_inference_errors) > 0:
                    self.tags.add('Type_inference_error')
            except AttributeError as e:
                # Probably No pattern set.
                logging.info('Could not derive type inference for requirement `{}`, Formalization No. {}. {}'.format(
                    self.rid,
                    id,
                    e
                ))
        self.store()

    def get_formalization_string(self):
        # TODO: implement this. (Used to print the whole formalization into the csv).
        return ''

    def run_version_migrations(self):
        if self.hanfor_version == '0.0.0':
            logging.info('Migrating `{}`:`{}`, from 0.0.0 -> 1.0.0'.format(
                self.__class__.__name__, self.rid)
            )
            # Migrate list formalizations to use dict
            self.hanfor_version = '1.0.0'
            if type(self.formalizations) is list:
                formalizations = dict(enumerate(self.formalizations))
                self.formalizations = formalizations
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
    def __init__(self):
        super().__init__()
        self.scoped_pattern = None
        self.expressions_mapping = dict()
        self.belongs_to_requirement = None
        self.used_variables = None
        self.type_inference_errors = dict()

    @property
    def used_variables(self):
        result = []
        for exp in self.expressions_mapping.values():  # type: Expression
            result += exp.get_used_variables()
        return list(set(result))

    @used_variables.setter
    def used_variables(self, value):
        self._used_variables = value

    def set_expressions_mapping(self, mapping, variable_collection, app, rid):
        """ Parse expression mapping.
            + Extract variables. Replace by their ID. Create new Variables if they do not exist.
            + For used variables and update the "used_by_requirements" set.

        :type mapping: dict
        :param mapping: {'P': 'foo > 0', 'Q': 'expression for Q', ...}
        :type app: Flask
        :type variable_collection: VariableCollection
        :param variable_collection: Currently used VariableCollection.
        :type rid: str
        :param rid: associated requirement id

        :return: type_inference_errors dict {key: type_env, ...}
        :rtype: dict
        """
        for key, expression_string in mapping.items():
            if len(expression_string) is 0:
                continue
            expression = Expression()
            expression.set_expression(
                expression_string, variable_collection, app, rid)
            if self.expressions_mapping is None:
                self.expressions_mapping = dict()
            self.expressions_mapping[key] = expression
        self.get_string()
        self.type_inference_check(variable_collection)

    def type_inference_check(self, variable_collection):
        """ Apply type inference check for the expressions in this formalization.
        Reload if applied multiple times.

        :param variable_collection: The current VariableCollection
        """
        type_inference_errors = dict()
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
            except Exception as e:
                logging.error(
                    'Lark could not parse expression `{}`: \n {}. Skipping type inference'.format(
                        expression.raw_expression,
                        e
                    )
                )
                continue
            # Update the expression
            expression.set_expression(expression.raw_expression, variable_collection, None, expression.parent_rid)

            # Derive type for variables in expression and update missing or changed types.
            type, type_env = boogie_parsing.infer_variable_types(tree, var_env).derive_type()
            if type not in allowed_types[key]:  # We have derived error, mark this expression as type error.
                type_inference_errors[key] = type_env
            for name, type in type_env.items():  # Update the hanfor variable types.
                if (variable_collection.collection[name].type is not None
                        and variable_collection.collection[name].type.lower() in ['const', 'enum']):
                    continue
                if variable_collection.collection[name].type not in boogie_parsing.BoogieType.aliases(type):
                    logging.info('Update variable `{}` with derived type. Old: `{}` => New: `{}`.'.format(
                        name,
                        variable_collection.collection[name].type,
                        type.name
                    ))
                    variable_collection.set_type(name, type.name)
        variable_collection.store()
        self.type_inference_errors = type_inference_errors

    def to_dict(self):
        d = {
            'scope': None,
            'pattern': None,
            'expressions': None
        }

        return d

    def get_string(self):
        result = ''
        try:
            result = self.scoped_pattern.get_string(self.expressions_mapping)
        except:
            logging.debug('Formalization can not be instantiated. There is no scoped pattern set.')
        return result

    def has_type_inference_errors(self):
        return len(self.type_inference_errors) > 0


class Expression(HanforVersioned):
    """ Representing a Expression in a ScopedPattern.
    For example: Let
       `Globally, {P} is always true.`
    be a Scoped pattern. One might replace {P} by
        `NO_PAIN => NO_GAIN`
    Then `NO_PAIN => NO_GAIN` is the Expression.
     """
    def __init__(self):
        """ Create an empty new expression.

        """
        super().__init__()
        self.used_variables = None
        self.raw_expression = None
        self.parent_rid = None

    def get_used_variables(self):
        if self.used_variables is not None:
            return self.used_variables
        else:
            return []

    def set_expression(self, expression: str, variable_collection: 'VariableCollection', app, parent_rid):
        """ Parses the Expression using the boogie grammar.
            * Extract variables.
                + Create new ones if not in Variable collection.
                + Replace Variables by their identifier.
            * Store set of used variables to `self.used_variables`

        :param expression:
        :type expression: str
        """
        self.raw_expression = expression
        self.parent_rid = parent_rid
        logging.debug(
            'Setting expression: `{}`'.format(expression)
        )
        # Get the vars occurring in the expression.
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(expression)

        self.used_variables = set(boogie_parsing.get_variables_list(tree))

        new_vars = []
        for var_name in self.used_variables:
            if var_name not in variable_collection:
                variable_collection.add_var(var_name)
                new_vars.append(var_name)

        if len(new_vars) > 0:
            variable_collection.reload_script_results(app, new_vars)

        variable_collection.map_req_to_vars(parent_rid, self.used_variables)
        try:
            variable_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
        except:
            pass

    def __str__(self):
        result = '"{}"'.format(self.raw_expression)
        # If the var is a number,
        if re.search(r'^\d+$', self.raw_expression) or re.search(r'^\d+\.\d+$', self.raw_expression):
            # do not quote.
            result = self.raw_expression
        return result


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
    name_mapping = {
        'Invariant':
            'it is always the case that if {R} holds, then {S} holds as well',
        'Absence':
            'it is never the case that {R} holds',
        'Universality':
            'it is always the case that {R} holds',
        'Existence':
            '{R} eventually holds',
        'BoundedExistence':
            'transitions to states in which {R} holds occur at most twice',
        'Precedence':
            'it is always the case that if {R} holds then {S} previously held',
        'PrecedenceChain1-2':
            'it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held',
        'PrecedenceChain2-1':
            'it is always the case that if {R} holds then {S} previously held and was preceded by {T}',
        'Response':
            'it is always the case that if {R} holds then {S} eventually holds',
        'ResponseChain1-2':
            'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}',
        'ResponseChain2-1':
            'it is always the case that if {R} holds and is succeeded by {S}, '
            'then {T} eventually holds after {S}',
        'ConstrainedChain':
            'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, '
            'where {U} does not hold between {S} and {T}',
        'MinDuration':
            'it is always the case that once {R} becomes satisfied, it holds for at least {S} time units',
        'MaxDuration':
            'it is always the case that once {R} becomes satisfied, it holds for less than {S} time units',
        'BoundedRecurrence':
            'it is always the case that {R} holds at least every {S} time units',
        'BoundedResponse':
            'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        'BoundedInvariance':
            'it is always the case that if {R} holds, then {S} holds for at least {T} time units',
        'TimeConstrainedMinDuration':
            'it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for '
            'at least {U} time units',
        'TimeConstrainedInvariant':
            'it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards',
        'ConstrainedTimedExistence':
            'it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least '
            '{U} time units',
        'Toggle1':
            'it is always the case that if {R} holds then {S} toggles {T}',
        'Toggle2':
            'it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later',
        'NotFormalizable': '// not formalizable'
    }

    pattern_env = {
        'Invariant': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool]
        },
        'Absence': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'Universality': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'Existence': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'BoundedExistence': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'Precedence': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool]
        },
        'PrecedenceChain1-2': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'PrecedenceChain2-1': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'Response': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool]
        },
        'ResponseChain1-2': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'ResponseChain2-1': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'ConstrainedChain': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'MinDuration': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'MaxDuration': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'BoundedRecurrence': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'BoundedResponse': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'BoundedInvariance': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'TimeConstrainedMinDuration': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
            'T': [boogie_parsing.BoogieType.bool],
            'U': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'TimeConstrainedInvariant': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
            'T': [boogie_parsing.BoogieType.bool],
        },
        'ConstrainedTimedExistence': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
            'U': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'Toggle1': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool],
        },
        'Toggle2': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool],
            'U': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'NotFormalizable': {}
    }

    def __init__(self, name, pattern=None):
        self.name = name
        if pattern is None:
            self.pattern = Pattern.name_mapping[name]
        else:
            self.pattern = pattern

    def instantiate(self, scope, *args):
        return scope + ', ' + Pattern.name_mapping[self.name].format(*args)

    def __str__(self):
        return Pattern.name_mapping[self.name]

    def get_allowed_types(self):
        return self.pattern_env[self.name]


class ScopedPattern:
    def __init__(self, scope, pattern):
        self.scope = scope
        self.pattern = pattern
        self.regex_pattern = None

    def get_string(self, expression_mapping: dict):
        return self.__str__().format(**expression_mapping).replace('\n', ' ').replace('\r', ' ')

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
        try:
            slug = self.scope.get_slug()
        except:
            slug = 'None'
        return slug

    def get_pattern_slug(self):
        try:
            slug = self.pattern.name
        except:
            slug = 'None'
        return slug

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
        self.collection = dict()
        self.req_var_mapping = dict()
        self.var_req_mapping = dict()

    def __contains__(self, item):
        return item in self.collection.keys()

    @classmethod
    def load(self, path) -> 'VariableCollection':
        me = Pickleable.load(path)
        if not isinstance(me, self):
            raise TypeError

        if me.has_version_mismatch:
            logging.info('`{}` needs upgrade `{}` -> `{}`'.format(
                me,
                me.hanfor_version,
                __version__
            ))
            me.run_version_migrations()
            me.store()

        return me

    def get_available_vars_list(self, sort_by=None, used_only=False, exclude_types=frozenset()):
        """ Returns a list of all available var names.

        :return:
        :rtype:
        """
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
            logging.debug('Adding variable `{}` to collection.'.format(var_name))
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
        """ Map a requirement by rid to used vars.

        :param rid:
        :type rid:
        :param used_variables:
        :type used_variables:
        """
        if rid not in self.req_var_mapping.keys():
            self.req_var_mapping[rid] = set()
        for var in used_variables:
            self.req_var_mapping[rid].add(var)

    def rename(self, old_name, new_name, app):
        """ Rename a var in the collection. Merges the variables if new_name variable exists.

        :param old_name: The old var name.
        :type old_name: str
        :param new_name: The new var name.
        :type new_name: str
        """
        logging.info('Rename `{}` -> `{}`'.format(old_name, new_name))
        # Store constraints to restore later on.
        tmp_constraints = []
        try:
            tmp_constraints += self.collection[old_name].get_constraints().values()
        except:
            pass
        try:
            tmp_constraints += self.collection[new_name].get_constraints().values()
        except:
            pass

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
                logging.debug('`{}` constraints not updatable: {}'.format(affected_var_name, e))

        # Update the constraint names if any
        def rename_constraint(name: str, old_name: str, new_name: str):
            match = re.match(Variable.CONSTRAINT_REGEX, name)
            if match is not None and match.group(2) == old_name:
                return name.replace(old_name, new_name)
            return name

        # Todo: this is even more inefficient :-(
        for key in self.var_req_mapping.keys():
            self.var_req_mapping[key] = {rename_constraint(name, old_name, new_name) for name in self.var_req_mapping[key]}

        # Update the req -> var mapping.
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)

        # Update the variable script results.
        self.reload_script_results(app, [new_name])

        # Rename the enumerators in case this renaming affects a enum.
        if self.collection[new_name].type in ['ENUM_INT', 'ENUM_REAL']:
            affected_enumerators = []
            for var in self.collection.values():
                if var.belongs_to_enum == old_name:
                    var.belongs_to_enum = new_name
                    old_enumerator_name = var.name
                    new_enumerator_name = replace_prefix(var.name, old_name, new_name)
                    affected_enumerators.append((old_enumerator_name, new_enumerator_name))
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
                except Exception as e:
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
                if not constraint_variable_name in self.collection.keys():
                    # The referenced variable is no longer existing.
                    try:
                        self.req_var_mapping[constraint_name].discard(var_name)
                    except:
                        pass
                    return True
                else:
                    # The variable exists. Now check if var_name occures in one of its constraints.
                    for constraint in self.collection[constraint_variable_name].get_constraints().values():
                        if var_name in constraint.get_string():
                            return False
                    try:
                        self.req_var_mapping[constraint_name].discard(var_name)
                    except:
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
                    for var_name in expression.get_used_variables():
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
            constrainr_pref = 'Constraint_{}'.format(var_name)
            affected_constraints = len([f for f in self.var_req_mapping[var_name] if constrainr_pref in f])
            total_usages = len(self.var_req_mapping[var_name])
            if affected_constraints == total_usages:
                deletable = True

        if deletable:
            self.collection.pop(var_name, None)
            self.var_req_mapping.pop(var_name, None)
            return True
        return False

    def get_enumerators(self, enum_name):
        enumerators = []
        for other_var in self.collection.values():
            if other_var.belongs_to_enum == enum_name:
                enumerators.append(other_var)
        return enumerators

    def run_version_migrations(self):
        logging.info(
            'Migrating `{}`:`{}`, from {} -> {}'.format(
                self.__class__.__name__,
                self.my_path,
                self.hanfor_version,
                __version__
            )
        )
        for name, variable in self.collection.items():  # type: (str, Variable)
            variable.run_version_migrations()
        if StrictVersion(self.hanfor_version) < StrictVersion('1.0.3'):
            # Migrate for introduction of ENUM_INT and ENUM_REAL.
            for name, variable in self.collection.items():  # type: (str, Variable)
                if variable.type == 'ENUM':
                    logging.info('Migrate old ENUM `{}` to new ENUM_INT, ENUM_REAL'.format(variable.name))
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
                        except:
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


class Variable(HanforVersioned):
    CONSTRAINT_REGEX = r"^(Constraint_)(.*)(_[0-9]+$)"

    def __init__(self, name, type, value):
        super().__init__()
        self.name = name
        self.type = type
        self.value = value
        self.tags = set()
        self.script_results = ''
        self.belongs_to_enum = ''

    def to_dict(self, var_req_mapping):
        used_by = []
        type_inference_errors = dict()
        for index, f in self.get_constraints().items():
            if f.has_type_inference_errors():
                type_inference_errors[index] = [key.lower() for key in f.type_inference_errors.keys()]
        try:
            used_by = sorted(list(var_req_mapping[self.name]))
        except:
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
        try:
            self.tags.add(tag_name)
        except AttributeError:
            self.tags = {tag_name}

    def remove_tag(self, tag_name):
        try:
            self.tags.discard(tag_name)
        except AttributeError:
            self.tags = {}

    def get_tags(self):
        try:
            return self.tags
        except AttributeError:
            return set()

    def set_type(self, new_type):
        allowed_types = ['CONST']
        allowed_types += boogie_parsing.BoogieType.get_valid_type_names()
        # return True
        if new_type not in allowed_types:
            raise ValueError('Illegal variable type: `{}`. Allowed types are: `{}`'.format(new_type, allowed_types))

        self.type = new_type

    def _next_free_constraint_id(self):
        i = 0
        try:
            while i in self.constraints.keys():
                i += 1
        except:
            pass
        return i

    def add_constraint(self):
        """ Add a new empty constraint

        :return: (index: int, The constraint: Formalization)
        """
        id = self._next_free_constraint_id()
        try:
            self.constraints[id] = Formalization()
        except:
            self.constraints = dict()
            self.constraints[id] = Formalization()

        return id, self.constraints[id]

    def del_constraint(self, id):
        try:
            del self.constraints[id]
            return True
        except:
            logging.debug('Constraint id `{}` not found in var `{}`'.format(id, self.name))
            return False

    def get_constraints(self):
        try:
            return self.constraints
        except:
            return dict()

    def reload_constraints_type_inference_errors(self, var_collection):
        logging.info('Reload type inference for variable `{}` constraints'.format(self.name))
        self.remove_tag('Type_inference_error')
        for id in self.get_constraints().keys():
            try:
                self.constraints[id].type_inference_check(var_collection)
                if len(self.constraints[id].type_inference_errors) > 0:
                    self.tags.add('Type_inference_error')
            except AttributeError as e:
                # Probably No pattern set.
                logging.info('Could not derive type inference for variable `{}` constraint No. {}. {}'.format(
                    self.name,
                    id,
                    e
                ))

    def update_constraint(self, constraint_id, scope_name, pattern_name, mapping, app, variable_collection):
        """ Update a single constraint

        :param constraint_id:
        :param scope_name:
        :param pattern_name:
        :param mapping:
        :param app:
        :param variable_collection:
        :return:
        """
        # set scoped pattern
        self.constraints[constraint_id].scoped_pattern = ScopedPattern(
            Scope[scope_name], Pattern(name=pattern_name)
        )
        # Parse and set the expressions.
        for key, expression_string in mapping.items():
            if len(expression_string) is 0:
                continue
            expression = Expression()
            expression.set_expression(
                expression_string, variable_collection, app, 'Constraint_{}_{}'.format(self.name, constraint_id)
            )
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
        logging.debug('Updating constraints for variable `{}`.'.format(self.name))
        self.remove_tag('Type_inference_error')
        if variable_collection is None:
            variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        for constraint in constraints.values():
            logging.debug('Updating formalizatioin No. {}.'.format(constraint['id']))
            logging.debug('Scope: `{}`, Pattern: `{}`.'.format(constraint['scope'], constraint['pattern']))
            try:
                variable_collection = self.update_constraint(
                    constraint_id=int(constraint['id']),
                    scope_name=constraint['scope'],
                    pattern_name=constraint['pattern'],
                    mapping=constraint['expression_mapping'],
                    app=app,
                    variable_collection=variable_collection
                )
            except Exception as e:
                logging.error('Could not update Constraint: {}'.format(e.__str__()))
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
                        and self.other_var_name.startswith(self.name)):
                    result.append(other_var_name)
                    break
        return result

    def run_version_migrations(self):
        if self.hanfor_version == '0.0.0':
            logging.info('Migrating `{}`:`{}`, from 0.0.0 -> 1.0.0'.format(
                self.__class__.__name__, self.name)
            )
            self.constraints = dict(enumerate(self.get_constraints()))
            self.hanfor_version = '1.0.0'
        if self.hanfor_version == '1.0.0':
            logging.info('Migrating `{}`:`{}`, from 1.0.0 -> 1.0.1'.format(
                self.__class__.__name__, self.name)
            )
            self.script_results = ''
            self.hanfor_version = '1.0.1'
        if self.hanfor_version in ['1.0.1', '1.0.2']:
            logging.info('Migrating `{}`:`{}`, from {} -> 1.0.3'.format(
                self.__class__.__name__, self.name, self.hanfor_version)
            )
            self.belongs_to_enum = ''
            self.hanfor_version = '1.0.3'
            if self.type == 'ENUM':
                logging.info('Migrate old ENUM `{}` to new ENUM_INT, ENUM_REAL'.format(self.name))

        super().run_version_migrations()


class Tag:
    def __init__(self, name, color='#5bc0de'):
        self.name = name
        self.color = color

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name


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
        except:
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
            if not var_name in self.result_var_collection.collection:
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
        self.import_sessions = list()

    @classmethod
    def load(self, path) -> 'VarImportSessions':
        me = Pickleable.load(path)
        if not isinstance(me, self):
            raise TypeError

        if me.has_version_mismatch:
            logging.info('`{}` needs upgrade `{}` -> `{}`'.format(
                me,
                me.hanfor_version,
                __version__
            ))
            me.run_version_migrations()
            me.store()

        return me

    @classmethod
    def load_for_app(self, app):
        var_import_sessions_path = os.path.join(
            app.config['SESSION_BASE_FOLDER'],
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
            'Migrating `{}`:`{}`, from {} -> {}'.format(
                self.__class__.__name__,
                self.my_path,
                self.hanfor_version,
                __version__
            )
        )
        for import_session in self.import_sessions:  # type: VarImportSession
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
