""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
import csv

import os
import re

import boogie_parsing
import logging
import random
import string
import utils

from enum import Enum


class RequirementCollection:
    def __init__(self):
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
            self.csv_meta['headers'] = list(self.csv_all_rows[0].keys())

    def select_headers(self, base_revision_headers=None):
        """ Ask the users, which of the csv headers correspond to our needed data.

        """
        use_old_headers = False
        if base_revision_headers:
            print('Should I use the csv header mapping from base revision?')
            use_old_headers = utils.choice(['yes', 'no'], 'yes')
        if base_revision_headers and use_old_headers == 'yes':
            self.csv_meta['id_header'] = base_revision_headers['csv_id_header']
            self.csv_meta['desc_header'] = base_revision_headers['csv_desc_header']
            self.csv_meta['formal_header'] = base_revision_headers['csv_formal_header']
            self.csv_meta['type_header'] = base_revision_headers['csv_type_header']
        else:
            print('Select ID header')
            self.csv_meta['id_header'] = utils.choice(self.csv_meta['headers'], 'ID')
            print('Select requirements description header')
            self.csv_meta['desc_header'] = utils.choice(
                self.csv_meta['headers'],
                'System Requirement Specification of Audi Central Connected Getway'
            )
            print('Select formalization header')
            self.csv_meta['formal_header'] = utils.choice(self.csv_meta['headers'], 'Formal Req')
            print('Select type header.')
            self.csv_meta['type_header'] = utils.choice(self.csv_meta['headers'], 'RB_Classification')

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


class Requirement:
    def __init__(self, rid, description, type_in_csv, csv_row, pos_in_csv):
        self.rid = rid
        self.formalizations = list()
        self.description = description
        self.type_in_csv = type_in_csv
        self.csv_row = csv_row
        self.pos_in_csv = pos_in_csv
        self.tags = set()
        self.status = 'Todo'

    def to_dict(self):
        d = {
            'id': self.rid,
            'desc': self.description,
            'type': self.type_in_csv if type(self.type_in_csv) is str else self.type_in_csv[0],
            'tags': sorted([tag for tag in self.tags]),
            'formal': [f.to_dict() for f in self.formalizations],
            'scope': 'None',
            'pattern': 'None',
            'vars': dict(),
            'pos': self.pos_in_csv,
            'status': self.status,
            'csv_data': self.csv_row
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
        filepath = os.path.join(app.config['REVISION_FOLDER'], '{}.pickle'.format(id))
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return utils.pickle_load_from_dump(filepath)

    def add_empty_formalization(self):
        """ Add an empty formalization to the formalizations list.

        :return: The id of the requirement (pos in list)
        :rtype: int
        """
        if self.formalizations is None:
            self.formalizations = list()
        self.formalizations.append(Formalization())

        return len(self.formalizations) - 1, Formalization()

    def delete_formalization(self, formalization_id, app):
        formalization_id = int(formalization_id)
        variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        # Remove formalizatioin
        del self.formalizations[formalization_id]
        # Collect remaining vars.
        remaining_vars = set()
        for formalization in self.formalizations:
            for expression in formalization.expressions_mapping.values():
                if expression.used_variables is not None:
                    remaining_vars = remaining_vars.union(expression.used_variables)

        # Update the mappings.
        variable_collection.req_var_mapping[self.rid] = remaining_vars
        variable_collection.var_req_mapping = variable_collection.invert_mapping(variable_collection.req_var_mapping)
        variable_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])

    def update_formalizations(self, formalizations: dict, app):
        self.tags.discard('Type_inference_error')
        logging.debug('Updating formalizatioins of requirement {}.'.format(self.rid))
        variable_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])
        # Reset the var mapping.
        variable_collection.req_var_mapping[self.rid] = set()

        for formalization in formalizations.values():
            logging.debug('Updating formalizatioin No. {}.'.format(formalization['id']))
            logging.debug('Scope: `{}`, Pattern: `{}`.'.format(formalization['scope'], formalization['pattern']))
            try:
                id = int(formalization['id'])
                # set scoped pattern
                self.formalizations[id].scoped_pattern = ScopedPattern(
                    Scope[formalization['scope']], Pattern(name=formalization['pattern'])
                )
                # set parent
                self.formalizations[id].belongs_to_requirement = self.rid
                # Parse and set the expressions.
                self.formalizations[id].set_expressions_mapping(
                    mapping=formalization['expression_mapping'],
                    variable_collection=variable_collection,
                    app=app,
                    rid=self.rid
                )
                if len(self.formalizations[id].type_inference_errors) > 0:
                    logging.debug('Type inference Error in formalization at {}.'.format(
                        [n for n in self.formalizations[id].type_inference_errors.keys()]
                    ))
                    self.tags.add('Type_inference_error')

            except Exception as e:
                logging.error('Could not update Formalization: {}'.format(e.__str__()))
                raise e

    def get_formalization_string(self):
        # TODO: implement this. (Used to print the whole formalization into the csv).
        return ''


class Formalization:
    def __init__(self):
        self.scoped_pattern = None
        self.expressions_mapping = dict()
        self.belongs_to_requirement = None
        self.used_variables = None
        self.type_inference_errors = dict()

    def set_expressions_mapping(self, mapping, variable_collection, app, rid):
        """ Parse expression mapping.
            + Extract variables. Replace by their ID. Create new Variables if they do not exist.
            + For used variables and update the "used_by_requirements" set.

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
        type_inference_errors = dict()
        for key, expression in self.expressions_mapping.items():
            tree = boogie_parsing.get_parser_instance().parse(expression.raw_expression)
            type_a = boogie_parsing.infer_variable_types(tree, variable_collection.get_boogie_type_env())
            type, type_env = type_a.derive_type()
            if type == boogie_parsing.BoogieType.error or boogie_parsing.BoogieType.error in type_env.values():
                type_inference_errors[key] = type_env
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
            logging.debug('Formalizatioin can not be instanciated. There is no scoped pattern set.')
        return result


class Expression:
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
        self.used_variables = None
        self.raw_expression = None
        self.parent_rid = None

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

        for var_name in self.used_variables:
            if var_name not in variable_collection:
                variable_collection.add_var(var_name)

        variable_collection.map_req_to_vars(parent_rid, self.used_variables)
        variable_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])

    def __str__(self):
        return self.raw_expression


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
        return slug_map[self.value]

    def __str__(self):
        return str(self.value)


class Pattern:
    name_mapping = {
        'Invariant':
            'it is always the case that if "{R}" holds, then "{S}" holds as well',
        'Absence':
            'it is never the case that "{R}" holds',
        'Universality':
            'it is always the case that "{R}" holds',
        'Existence':
            '"{R}" eventually holds',
        'BoundedExistence':
            'transitions to states in which "{R}" holds occur at most twice',
        'Precedence':
            'it is always the case that if "{R}" holds then "{S}" previously held',
        'PrecedenceChain1-2':
            'it is always the case that if "{R}" holds and is succeeded by "{S}", then "{T}" previously held',
        'PrecedenceChain2-1':
            'it is always the case that if "{R}" holds then "{S}" previously held and was preceded by "{T}"',
        'Response':
            'it is always the case that if "{R}" holds then "{S}" eventually holds',
        'ResponseChain1-2':
            'it is always the case that if "{R}" holds then "{S}" eventually holds and is succeeded by "{T}"',
        'ResponseChain2-1':
            'it is always the case that if "{R}" holds and is succeeded by "{S}", '
            'then "{T}" eventually holds after "{S}"',
        'ConstrainedChain':
            'it is always the case that if "{R}" holds then "{S}" eventually holds and is succeeded by "{T}", '
            'where "{U}" does not hold between "{S}" and "{T}"',
        'MinDuration':
            'it is always the case that once "{R}" becomes satisfied, it holds for at least "{S}" time units',
        'MaxDuration':
            'it is always the case that once "{R}" becomes satisfied, it holds for less than "{S}" time units',
        'BoundedRecurrence':
            'it is always the case that "{R}" holds at least every "{S}" time units',
        'BoundedResponse':
            'it is always the case that if "{R}" holds, then "{S}" holds after at most "{T}" time units',
        'BoundedInvariance':
            'it is always the case that if "{R}" holds, then "{S}" holds for at least "{T}" time units',
        'TimeConstrainedMinDuration':
            'if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units',
        'TimeConstrainedInvariant':
            'if {R} holds for at least {S} time units, then {T} holds afterwards',
        'ConstrainedTimedExistence':
            'it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} '
            'time units',
        'NotFormalizable': '// not formalizable'
    }

    def __init__(self, name, pattern=None):
        self.name = name
        if pattern is None:
            self.pattern = Pattern.name_mapping[name]
        else:
            self.pattern = pattern

    def instantiate(self, scope, *args):
        return scope + ', ' + self.pattern.format(*args)

    def __str__(self):
        return self.pattern


class ScopedPattern:
    def __init__(self, scope, pattern):
        self.scope = scope
        self.pattern = pattern
        self.regex_pattern = None

    def get_string(self, expression_mapping: dict):
        return self.__str__().format(**expression_mapping)

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
            literal_str = literal_str.replace('"{{{}}}"'.format(f), '"([\d\w\s"-]*)"')

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


class VariableCollection:
    def __init__(self):
        self.collection = dict()
        self.req_var_mapping = dict()
        self.var_req_mapping = dict()

    def __contains__(self, item):
        return item in self.collection.keys()

    @classmethod
    def load(self, path) -> 'VariableCollection':
        return utils.pickle_load_from_dump(path)

    def get_available_vars_list(self, sort_by=None, used_only=False):
        """ Returns a list of all available var names.

        :return:
        :rtype:
        """
        def in_result(var_name) -> bool:
            if used_only:
                if var_name not in self.var_req_mapping.keys():
                    return False
                if len(self.var_req_mapping[var_name]) == 0:
                    return False
            return True
        result = [
            var.to_dict(self.var_req_mapping)
            for var in self.collection.values()
            if in_result(var.name)
        ]
        if len(result) > 0 and sort_by is not None and sort_by in result[0].keys():
            result = sorted(result, key=lambda k: k[sort_by])
        return result

    def get_available_var_names_list(self, used_only=True):
        return [var['name'] for var in self.get_available_vars_list(used_only=used_only)]

    def add_var(self, var_name):
        if var_name not in self.collection.keys():
            logging.debug('Adding variable `{}` to collection.'.format(var_name))
            self.collection[var_name] = Variable(var_name, None, None)

    def store(self, path):
        self.var_req_mapping = self.invert_mapping(self.req_var_mapping)
        utils.pickle_dump_obj_to_file(self, path)

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
        """ Rename a var in the collection.

        :param old_name:
        :type old_name:
        :param new_name:
        :type new_name:
        """
        # Copy to new location.
        self.collection[new_name] = self.collection.pop(old_name)
        # Update name to new name
        self.collection[new_name].name = new_name

        # Update the mappings.
        # Copy old to new mapping
        self.var_req_mapping[new_name] = self.var_req_mapping.pop(old_name)
        # Update the req -> var mapping.
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)

    def merge_vars(self, origin, target, app):
        """ Merge var origin into var source (resulting in only a source var).

        :param origin:
        :type origin:
        :param source:
        :type source:
        """
        self.var_req_mapping[target] = self.var_req_mapping[target].union(self.var_req_mapping[origin])
        del self.var_req_mapping[origin]
        del self.collection[origin]
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)

    def get_boogie_type_env(self):
        mapping = {
            'bool': boogie_parsing.BoogieType.bool,
            'int': boogie_parsing.BoogieType.int,
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
                    x = float(var.value)
                except ValueError:
                    type_env[name] = mapping['unknown']
                    continue

                try:
                    x = int(x)
                except ValueError:
                    type_env[name] = mapping['real']
                    continue

                type_env[name] = mapping['int']
            else:
                type_env[name] = mapping['unknown']

        # Todo: Store this so we can reuse and update on collection change.
        return type_env


class Variable:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value

    def to_dict(self, var_req_mapping):
        used_by = []
        try:
            used_by = sorted(list(var_req_mapping[self.name]))
        except:
            logging.info('No req mapping found for var `{}`'.format(self.name))

        d = {
            'name': self.name,
            'type': self.type,
            'const_val': self.value,
            'used_by': used_by
        }

        return d


# This PatternVariable is here only for compatibility reasons.
class PatternVariable:
    TYPES = ['bool', 'int']

    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        self.value = None

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.type))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
