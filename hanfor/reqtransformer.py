""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""

import csv
import difflib
import json
import logging
import re
import string
from dataclasses import dataclass, field
from enum import Enum

from lark import LarkError, Lark
from typing_extensions import deprecated

import boogie_parsing
from boogie_parsing import run_typecheck_fixpoint, BoogieType
from patterns import PATTERNS
from static_utils import choice, replace_prefix, try_cast_string, SessionValue
from tags.tags import TagsApi, Tag

from typing import Dict, Tuple
from hanfor_flask import current_app

from json_db_connector.json_db import (
    DatabaseTable,
    TableType,
    DatabaseID,
    DatabaseField,
    DatabaseFieldType,
    DatabaseNonSavedField,
)
from threading import Lock

__version__ = "1.0.4"


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


class RequirementCollection:

    def __init__(self):
        self.csv_meta = CsvConfig()
        self.csv_all_rows = None
        self.requirements = list()

    def create_from_csv(
        self,
        csv_file,
        app,
        input_encoding="utf8",
        base_revision_headers=None,
        user_provided_headers=None,
        available_sessions=None,
    ):
        """Create a RequirementCollection from a csv file, containing one requirement per line.
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
        self.select_headers(base_revision_headers=base_revision_headers, user_provided_headers=user_provided_headers)
        self.process_csv_hanfor_data_import(available_sessions=available_sessions, app=app)
        self.parse_csv_rows_into_requirements(app)

    def load_csv(self, csv_file: str, input_encoding: str):
        """Reads a csv file into `csv_all_rows`. Stores csv_dialect and csv_fieldnames in `csv_meta`

        :param csv_file: Path to csv file.
        :param input_encoding: Encoding of the csv file.
        """
        logging.info(f"Load Input : {csv_file}")
        with open(csv_file, "r", encoding=input_encoding) as csvfile:
            csv.register_dialect("ultimate", delimiter=",", escapechar="\\", quoting=csv.QUOTE_ALL, quotechar="\"")
            dialect = "ultimate"
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            self.csv_all_rows = list(reader)
            self.csv_meta.fieldnames = reader.fieldnames
            self.csv_meta.headers = sorted(list(reader.fieldnames))

    def select_headers(self, base_revision_headers=None, user_provided_headers=None):
        """Determines which of the csv headers correspond to our needed data.

        Args:
            base_revision_headers:
            user_provided_headers:
        """
        use_old_headers = False
        if base_revision_headers:
            print("Should I use the csv header mapping from base revision?")
            use_old_headers = choice(["yes", "no"], "yes")

        if user_provided_headers:
            print(user_provided_headers)
            self.csv_meta.id_header = user_provided_headers["csv_id_header"]
            self.csv_meta.desc_header = user_provided_headers["csv_desc_header"]
            self.csv_meta.formal_header = user_provided_headers["csv_formal_header"]
            self.csv_meta.type_header = user_provided_headers["csv_type_header"]
        elif base_revision_headers and use_old_headers == "yes":
            self.csv_meta.id_header = base_revision_headers["csv_id_header"].value
            self.csv_meta.desc_header = base_revision_headers["csv_desc_header"].value
            self.csv_meta.formal_header = base_revision_headers["csv_formal_header"].value
            self.csv_meta.type_header = base_revision_headers["csv_type_header"].value
        else:
            available_headers = set(self.csv_meta.headers)
            available_headers.discard("Hanfor_Tags")
            available_headers.discard("Hanfor_Status")
            available_headers = sorted(available_headers)

            print("Select ID header")
            self.csv_meta.id_header = choice(available_headers, "ID")
            print("Select requirements description header")
            self.csv_meta.desc_header = choice(available_headers, "Object Text")
            print("Select formalization header")
            self.csv_meta.formal_header = choice(available_headers + ["Add new Formalization"], "Hanfor_Formalization")
            if self.csv_meta.formal_header == "Add new Formalization":
                self.csv_meta.formal_header = "Hanfor_Formalization"
            print("Select type header.")
            self.csv_meta.type_header = choice(available_headers, "RB_Classification")

    def process_csv_hanfor_data_import(self, available_sessions, app):
        if app.config["USING_REVISION"] != "revision_0":  # We only support importing formalizations for base revisions
            return

        print("Do you want to import existing data from CSV?")
        if choice(["no", "yes"], "no") == "no":
            return

        print("Do you want to import Formalizations from CSV?")
        import_formalizations = choice(["no", "yes"], "no")
        if import_formalizations == "yes":
            self.csv_meta.import_formalizations = True

        print("Do you want to import Hanfor tags and status from CSV?")
        if choice(["no", "yes"], "no") == "yes":
            print("Select the Hanfor Tags header.")
            self.csv_meta.tags_header = choice(self.csv_meta.headers, "Hanfor_Tags")
            print("Select the Hanfor Status header.")
            self.csv_meta.status_header = choice(self.csv_meta.headers, "Hanfor_Status")

        print("Do you want to import a base Variable collection?")
        if choice(["no", "yes"], "yes") == "yes":
            available_sessions = [s for s in available_sessions]
            available_sessions_names = [s["name"] for s in available_sessions]
            if len(available_sessions_names) > 0:
                print("Choose the Variable Collection to import.")
                chosen_session = choice(available_sessions_names, available_sessions_names[0])
                print("Choose the revision for session {}".format(chosen_session))
                available_revisions = [
                    r for r in available_sessions[available_sessions_names.index(chosen_session)]["revisions"]
                ]
                revision_choice = choice(available_revisions, available_revisions[0])
                # TODO: here there is funky stuff with revicion choice
                # imported_var_collection = VariableCollection.load(
                #     os.path.join(
                #         app.config["SESSION_BASE_FOLDER"],
                #         chosen_session,
                #         revision_choice,
                #         "session_variable_collection.pickle",
                #     )
                # )
                # imported_var_collection.store(app.config["SESSION_VARIABLE_COLLECTION"])
            else:
                print("No sessions available. Skipping")

    def parse_csv_rows_into_requirements(self, app):
        """Parse each row in csv_all_rows into one Requirement.

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
                pos_in_csv=index,
            )
            if self.csv_meta.import_formalizations:
                # Set the tags
                if self.csv_meta.tags_header is not None:
                    tag_api = TagsApi()
                    for t in row[self.csv_meta.tags_header].split(","):
                        if not tag_api.tag_exists(t):
                            tag_api.add(t)
                        tag = tag_api.get_tag(t)
                        requirement.tags[tag] = ""
                # Set the status
                if self.csv_meta.status_header is not None:
                    status = row[self.csv_meta.status_header].strip()
                    if status not in ["Todo", "Review", "Done"]:
                        logging.debug("Status {} not supported. Set to `Todo`".format(status))
                        status = "Todo"
                    requirement.status = status
                # Parse and set the requirements.
                formalizations = json.loads(row[self.csv_meta.formal_header])
                for key, formalization_dict in formalizations.items():
                    formalization = Formalization(int(key))
                    requirement.formalizations[int(key)] = formalization
                    requirement.update_formalization(
                        formalization_id=int(key),
                        scope_name=formalization_dict["scope"],
                        pattern_name=formalization_dict["pattern"],
                        mapping=formalization_dict["expressions"],
                        app=app,
                    )

            self.requirements.append(requirement)


@DatabaseTable(TableType.Folder)
@DatabaseID("rid", str)
@DatabaseField("formalizations", dict)
@DatabaseField("description", str)
@DatabaseField("type_in_csv", str)
@DatabaseField("csv_row", dict)
@DatabaseField("pos_in_csv", int)
@DatabaseField("tags", dict)
@DatabaseField("status", str, default="Todo")
@DatabaseField("_revision_diff", dict)
@DatabaseField("_next_formalization_index", int, default=-1)
@DatabaseNonSavedField("_formalization_index_mutex", Lock())
class Requirement:
    def __init__(self, id: str, description: str, type_in_csv: str, csv_row: dict[str, str], pos_in_csv: int):
        self.rid: str = id
        self.formalizations: Dict[int, Formalization] = dict()
        self.description = description
        self.type_in_csv = type_in_csv
        self.csv_row = csv_row
        self.pos_in_csv = pos_in_csv
        self.tags: dict[Tag, str] = dict()
        self.status = "Todo"
        self._revision_diff = dict()
        self._next_formalization_index: int = -1
        self._formalization_index_mutex: Lock = Lock()

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
            "id": self.rid,
            "desc": self.description,
            # Typecheck is for downwards compatibility (please do not remove)
            "type": self.type_in_csv if isinstance(self.type_in_csv, str) else "None",
            "tags": [tag.name for tag in self.tags.keys()],
            "tags_comments": {tag.name: comment for tag, comment in self.tags.items()},
            "formal": [f.get_string() for f in self.formalizations.values()],
            "scope": "None",  # TODO: remove: This is obsolete since a requirement can hold multiple Formalizations.
            "pattern": "None",  # TODO: remove: This is obsolete since a requirement can hold multiple Formalizations.
            "vars": sorted([name for name in used_variables]),
            "pos": self.pos_in_csv,
            "status": self.status,
            "csv_data": self.csv_row,
            "type_inference_errors": type_inference_errors,
            "revision_diff": self.revision_diff,
        }
        return d

    @property
    def revision_diff(self) -> Dict[str, str]:
        if not hasattr(self, "_revision_diff"):
            self._revision_diff = dict()
        return self._revision_diff

    @revision_diff.setter
    def revision_diff(self, other: "Requirement"):
        """Compute and set diffs based on `other` Requirement

        :param other: Requirement the diff should be based on.
        """
        self._revision_diff = dict()
        for csv_key in self.csv_row.keys():
            if csv_key not in other.csv_row.keys():
                other.csv_row[csv_key] = ""
            if self.csv_row[csv_key] is None:
                # This can happen if we revision with an CSV that is missing the csv_key now.
                self.csv_row[csv_key] = ""
            diff = difflib.ndiff(self.csv_row[csv_key].splitlines(), other.csv_row[csv_key].splitlines())
            diff = [s for s in diff if not s.startswith("  ")]
            diff = "\n".join(diff)
            if len(diff) > 0:
                self._revision_diff[csv_key] = diff
        self.description = other.description
        self.type_in_csv = other.type_in_csv
        self.csv_row = other.csv_row
        self.pos_in_csv = other.pos_in_csv

    def _next_free_formalization_id(self) -> int:
        with self._formalization_index_mutex:
            if self._next_formalization_index == -1:
                if len(self.formalizations) == 0:
                    self._next_formalization_index = 0
                else:
                    self._next_formalization_index = max(self.formalizations.keys()) + 1
            i = self._next_formalization_index
            self._next_formalization_index += 1
            return i

    def add_empty_formalization(self) -> Tuple[int, "Formalization"]:
        """Add an empty formalization to the formalizations list."""
        id = self._next_free_formalization_id()
        self.formalizations[id] = Formalization(id)
        return id, self.formalizations[id]

    def delete_formalization(self, formalization_id, app):
        formalization_id = int(formalization_id)
        variable_collection = VariableCollection(app)

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
        variable_collection.store()
        app.db.update()

    def update_formalization(self, formalization_id, scope_name, pattern_name, mapping, app, variable_collection=None):
        if variable_collection is None:
            variable_collection = VariableCollection(app)

        # TODO: simplify
        # set scoped pattern
        sp: ScopedPattern = self.formalizations[formalization_id].scoped_pattern
        if not sp.scope.name == scope_name or not sp.pattern.name == pattern_name:
            self.formalizations[formalization_id].scoped_pattern = ScopedPattern(
                Scope[scope_name], Pattern(name=pattern_name)
            )
        # Parse and set the expressions.
        self.formalizations[formalization_id].set_expressions_mapping(
            mapping=mapping, variable_collection=variable_collection, rid=self.rid
        )

        # Add 'Type_inference_error' tag
        if len(self.formalizations[formalization_id].type_inference_errors) > 0:
            formatted_errors = self.format_error_tag(self.formalizations[formalization_id])
            self.tags[current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value] = formatted_errors

        # Add 'unknown_type' tag
        vars_with_unknown_type = []
        vars_with_unknown_type = self.formalizations[formalization_id].unknown_types_check(
            variable_collection, vars_with_unknown_type
        )
        if vars_with_unknown_type:
            self.tags[current_app.db.get_object(SessionValue, "TAG_unknown_type").value] = self.format_unknown_type_tag(
                vars_with_unknown_type
            )

        if (
            self.formalizations[formalization_id].scoped_pattern.scope != Scope.NONE
            and self.formalizations[formalization_id].scoped_pattern.pattern.name != "NotFormalizable"
        ):
            self.tags[current_app.db.get_object(SessionValue, "TAG_has_formalization").value] = ""
        else:
            self.tags[current_app.db.get_object(SessionValue, "TAG_incomplete_formalization").value] = (
                self.format_incomplete_formalization_tag(formalization_id)
            )

    def format_error_tag(self, formalisation: "Formalization") -> str:
        if current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value not in self.tags:
            result = ""
        else:
            result = self.tags[current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value]

        if not formalisation.type_inference_errors:
            return result
        for key, value in formalisation.type_inference_errors.items():
            result += f"{self.rid}_{str(formalisation.id)} ({key}): \n- "
            result += "\n- ".join(value) + "\n"
        return result

    def format_unknown_type_tag(self, vars) -> str:
        return ", ".join(sorted(vars))

    def format_incomplete_formalization_tag(self, fid: int) -> str:
        rid_fid = self.rid + "_" + fid.__str__()
        if current_app.db.get_object(SessionValue, "TAG_incomplete_formalization").value not in self.tags:
            return "- " + rid_fid
        else:
            return (
                self.tags[current_app.db.get_object(SessionValue, "TAG_incomplete_formalization").value]
                + "\n- "
                + rid_fid
            )

    def update_formalizations(self, formalizations: dict, app):
        if current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value in self.tags:
            self.tags.pop(current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value)
        if current_app.db.get_object(SessionValue, "TAG_unknown_type").value in self.tags:
            self.tags.pop(current_app.db.get_object(SessionValue, "TAG_unknown_type").value)
        if current_app.db.get_object(SessionValue, "TAG_incomplete_formalization").value in self.tags:
            self.tags.pop(current_app.db.get_object(SessionValue, "TAG_incomplete_formalization").value)
        if current_app.db.get_object(SessionValue, "TAG_has_formalization").value in self.tags:
            self.tags.pop(current_app.db.get_object(SessionValue, "TAG_has_formalization").value)
        logging.debug(f"Updating formalisations of requirement {self.rid}.")
        variable_collection = VariableCollection(app)
        # Reset the var mapping.
        variable_collection.req_var_mapping[self.rid] = set()

        for formalization in formalizations.values():
            logging.debug(f"Updating formalization No. {formalization['id']}.")
            logging.debug(f"Scope: `{formalization['scope']}`, Pattern: `{formalization['pattern']}`.")
            try:
                self.update_formalization(
                    formalization_id=int(formalization["id"]),
                    scope_name=formalization["scope"],
                    pattern_name=formalization["pattern"],
                    mapping=formalization["expression_mapping"],
                    app=app,
                    variable_collection=variable_collection,
                )
            except Exception as e:
                logging.error(f"Could not update Formalization: {e.__str__()}")
                raise e

    def run_type_checks(self, var_collection):
        logging.info(f"Run type inference and unknown check for `{self.rid}`")
        if current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value in self.tags:
            self.tags.pop(current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value)
        if current_app.db.get_object(SessionValue, "TAG_unknown_type").value in self.tags:
            self.tags.pop(current_app.db.get_object(SessionValue, "TAG_unknown_type").value)
        vars_with_unknown_type = []
        for id in self.formalizations.keys():
            # Run type inference check
            self.formalizations[id].type_inference_check(var_collection)
            if len(self.formalizations[id].type_inference_errors) > 0:
                self.tags[current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value] = (
                    self.format_error_tag(self.formalizations[id])
                )

            # Check for variables of type 'unknown' in formalization
            vars_with_unknown_type = self.formalizations[id].unknown_types_check(var_collection, vars_with_unknown_type)
            if vars_with_unknown_type:
                self.tags[current_app.db.get_object(SessionValue, "TAG_unknown_type").value] = (
                    self.format_unknown_type_tag(vars_with_unknown_type)
                )

    def get_formalizations_json(self) -> str:
        """Fetch all formalizations in json format. Used to reload formalizations.

        Returns:
            str: The json formatted version of the formalizations.

        """
        result = dict()
        for key, formalization in self.formalizations.items():
            if formalization.scoped_pattern is None:
                continue
            result[str(key)] = formalization.to_dict()

        return json.dumps(result, sort_keys=True)

    def uses_var(self, var_name):
        """Test is var_name is used in one of the requirements formalizations.

        :param var_name: The variable name.
        :return: True if var_name occurs at least once.
        """
        result = False
        for formalization in self.formalizations.values():  # type: Formalization
            if var_name in formalization.used_variables:
                result = True
                break
        return result

    @deprecated("Use req.tags with Tag objects as key instead.")
    def get_tag_name_comment_dict(self) -> dict[str, str]:
        return {tag.name: comment for tag, comment in self.tags.items()}


@DatabaseFieldType()
@DatabaseField("id", int)
@DatabaseField("scoped_pattern", "ScopedPattern")
@DatabaseField("expressions_mapping", dict)
@DatabaseField("type_inference_errors", dict)
class Formalization:
    def __init__(self, id: int):
        self.id: int = id
        self.scoped_pattern = ScopedPattern()
        self.expressions_mapping: dict[str, Expression] = dict()
        self.type_inference_errors = dict()

    @property
    def used_variables(self):
        result = []
        for exp in self.expressions_mapping.values():  # type: Expression
            result += exp.used_variables
        return list(set(result))

    def set_expressions_mapping(
        self, mapping: dict[str, str], variable_collection: "VariableCollection", rid: str
    ) -> None:
        """Parse expression mapping.
            + Extract variables. Replace by their ID. Create new Variables if they do not exist.
            + For used variables and update the "used_by_requirements" set.

        :param mapping: {'P': 'foo > 0', 'Q': 'expression for Q', ...}
        :param variable_collection: Currently used VariableCollection.
        :param rid: associated requirement id

        :return: type_inference_errors dict {key: type_env, ...}
        """
        changes = False
        for key, expression_string in mapping.items():
            if key not in self.expressions_mapping:
                self.expressions_mapping[key] = Expression(rid)
            if self.expressions_mapping[key].set_expression(expression_string, variable_collection):
                changes = True
        if changes:
            self.type_inference_check(variable_collection)

    def type_inference_check(self, variable_collection):
        """Apply type inference check for the expressions in this formalization.
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
                    f"Lark could not parse expression `{expression.raw_expression}`: \n {e}. Skipping type inference"
                )
                continue
            expression.set_expression(expression.raw_expression, variable_collection)

            # Derive type for variables in expression and update missing or changed types.
            ti = run_typecheck_fixpoint(tree, var_env, expected_types=allowed_types[key])
            expression_type, type_env, type_errors = ti.type_root.t, ti.type_env, ti.type_errors

            # Add type error if a variable is used in a timing expression
            if allowed_types[key] != [BoogieType.bool]:
                for var in expression.used_variables:
                    if variable_collection.collection[var].type != "CONST":
                        type_errors.append(f"Variable '{var}' used in time bound.")

            for name, var_type in type_env.items():  # Update the hanfor variable types.
                if variable_collection.collection[name].type and variable_collection.collection[name].type.lower() in [
                    "const",
                    "enum",
                ]:
                    continue
                if variable_collection.collection[name].type not in boogie_parsing.BoogieType.aliases(var_type):
                    logging.info(
                        f"Update variable `{name}` with derived type. "
                        f"Old: `{variable_collection.collection[name].type}` => New: `{var_type.name}`."
                    )
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
            "scope": self.scoped_pattern.scope.name,
            "pattern": self.scoped_pattern.pattern.name,
            "expressions": {key: exp.raw_expression for key, exp in self.expressions_mapping.items()},
        }

        return d

    def get_string(self):
        return self.scoped_pattern.get_string(self.expressions_mapping)


@DatabaseFieldType()
@DatabaseField("used_variables", list[str])
@DatabaseField("raw_expression", str)
@DatabaseField("parent_rid", str)
class Expression:
    """Representing an Expression in a ScopedPattern.
    For example: Let
       `Globally, {P} is always true.`
    be a Scoped pattern. One might replace {P} by
        `NO_PAIN => NO_GAIN`
    Then `NO_PAIN => NO_GAIN` is the Expression.
    """

    def __init__(self, parent_rid: str):
        self.used_variables: list[str] = list()  # TODO use Variable objects instead of str
        self.raw_expression = ""
        self.parent_rid = parent_rid

    def set_expression(self, expression: str, variable_collection: "VariableCollection") -> bool:
        """Parses the Expression using the boogie grammar.
        * Extract variables.
            + Create new ones if not in Variable collection.
            + Replace Variables by their identifier.
        * Store set of used variables to `self.used_variables`
        """
        if expression == self.raw_expression:
            return False
        logging.debug(f"Setting expression: `{expression}`")
        self.raw_expression = expression
        # Get the vars occurring in the expression.
        tree = boogie_parsing.get_parser_instance().parse(expression)

        self.used_variables = set(boogie_parsing.get_variables_list(tree))
        for var_name in self.used_variables:
            if var_name not in variable_collection:
                variable_collection.add_var(var_name)

        variable_collection.map_req_to_vars(self.parent_rid, self.used_variables)
        return True

    def __str__(self):
        return f'"{self.raw_expression}"'


class Scope(Enum):
    GLOBALLY = "Globally"
    BEFORE = 'Before "{P}"'
    AFTER = 'After "{P}"'
    BETWEEN = 'Between "{P}" and "{Q}"'
    AFTER_UNTIL = 'After "{P}" until "{Q}"'
    NONE = "// None"

    def instantiate(self, *args):
        return str(self.value).format(*args)

    def get_slug(self):
        """Returns a short slug representing the scope value.
        Use in applications where you don't want to use the full string.

        :return: Slug like AFTER_UNTIL for 'After "{P}" until "{Q}"'
        :rtype: str
        """
        slug_map = {
            str(self.GLOBALLY): "GLOBALLY",
            str(self.BEFORE): "BEFORE",
            str(self.AFTER): "AFTER",
            str(self.BETWEEN): "BETWEEN",
            str(self.AFTER_UNTIL): "AFTER_UNTIL",
            str(self.NONE): "NONE",
        }
        return slug_map[self.__str__()]

    def __str__(self):
        result = str(self.value).replace('"', "")
        return result

    def get_allowed_types(self):
        scope_env = {
            "GLOBALLY": {},
            "BEFORE": {"P": [boogie_parsing.BoogieType.bool]},
            "AFTER": {"P": [boogie_parsing.BoogieType.bool]},
            "BETWEEN": {"P": [boogie_parsing.BoogieType.bool], "Q": [boogie_parsing.BoogieType.bool]},
            "AFTER_UNTIL": {"P": [boogie_parsing.BoogieType.bool], "Q": [boogie_parsing.BoogieType.bool]},
            "NONE": {},
        }
        return scope_env[self.name]


@DatabaseFieldType()
@DatabaseField("name", str)
@DatabaseField("pattern", str)
class Pattern:
    def __init__(self, name: str = "NotFormalizable"):
        self.name = name
        self.pattern = PATTERNS[name]["pattern"]
        self.environment = PATTERNS[name]["env"]

    def is_instantiatable(self):
        return self.name != "NotFormalizable"

    def instantiate(self, scope: Scope, *args):
        return str(scope) + ", " + self.pattern.format(*args)

    def __str__(self):
        return self.pattern

    def get_allowed_types(self):
        return BoogieType.alias_env_to_instantiated_env(PATTERNS[self.name]["env"])


@DatabaseFieldType()
@DatabaseField("scope", Scope)
@DatabaseField("pattern", Pattern)
@DatabaseField("regex_pattern", str)
class ScopedPattern:
    def __init__(self, scope: Scope = Scope.NONE, pattern: Pattern = None):
        self.scope = scope
        if not pattern:
            pattern = Pattern()
        self.pattern = pattern
        self.regex_pattern = None
        self.environment = pattern.environment | scope.get_allowed_types()

    def get_string(self, expression_mapping: dict):
        # TODO: avoid having this problem in the first place
        try:
            return self.__str__().format(**expression_mapping).replace("\n", " ").replace("\r", " ")
        except KeyError as e:
            logging.error(
                f"Pattern {self.pattern.name}: insufficient " f"keys in expression mapping {str(expression_mapping)}"
            )
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
        for _, field_name, _, _ in fmt.parse(literal_str):
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
        return str(self.scope) + ", " + str(self.pattern)

    def get_allowed_types(self):
        result = self.scope.get_allowed_types()
        result.update(self.pattern.get_allowed_types())
        return result


class VariableCollection:
    def __init__(self, app):
        self.app = app
        self.collection: Dict[str, Variable] = {v.name: v for v in app.db.get_objects(Variable).values()}
        self.refresh_var_usage(app)
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)

    def __contains__(self, item):
        return item in self.collection.keys()

    def get_available_vars_list(self, sort_by=None, used_only=False, exclude_types=frozenset()):
        """Returns a list of all available var names."""

        def in_result(var) -> bool:
            if used_only:
                if var.name not in self.var_req_mapping.keys():
                    return False
                if len(self.var_req_mapping[var.name]) == 0:
                    return False
            if var.type in exclude_types:
                return False

            return True

        result = [var.to_dict(self.var_req_mapping) for var in self.collection.values() if in_result(var)]

        if len(result) > 0 and sort_by is not None and sort_by in result[0].keys():
            result = sorted(result, key=lambda k: k[sort_by])

        return result

    def get_available_var_names_list(self, used_only=True, exclude_types=frozenset()):
        return [var["name"] for var in self.get_available_vars_list(used_only=used_only, exclude_types=exclude_types)]

    def var_name_exists(self, name):
        return name in self.collection.keys()

    def add_var(self, var_name, variable=None):
        if not self.var_name_exists(var_name):
            if variable is None:
                variable = Variable(var_name, None, None)
            logging.debug(f"Adding variable `{var_name}` to collection.")
            self.collection[variable.name] = variable
            self.app.db.add_object(variable)

    def store(self):
        self.var_req_mapping = self.invert_mapping(self.req_var_mapping)
        # self.app.db.update()

    def invert_mapping(self, mapping):
        newdict = {}
        for k in mapping:
            for v in mapping[k]:
                newdict.setdefault(v, set()).add(k)
        return newdict

    def map_req_to_vars(self, rid, used_variables):
        """Map a requirement by rid to used vars."""

        if rid not in self.req_var_mapping.keys():
            self.req_var_mapping[rid] = set()
        for var in used_variables:
            self.req_var_mapping[rid].add(var)

    def rename(self, old_name: str, new_name: str, app):
        """Rename a var in the collection. Merges the variables if new_name variable exists.

        :param old_name: The old var name.
        :param new_name: The new var name.
        :returns affected_enumerators List [(old_enumerator_name, new_enumerator_name)] of potentially affected
        enumerators.
        """
        logging.info(f"Rename `{old_name}` -> `{new_name}`")
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
        self.var_req_mapping[new_name] = self.var_req_mapping.pop(old_name, set()).union(
            self.var_req_mapping.pop(new_name, set())
        )

        # Rename
        # Todo: this is inefficient. Parse the var name from constraint name to limit only for affected vars.
        for affected_var_name in self.collection.keys():
            try:
                self.collection[affected_var_name].rename_var_in_constraints(old_name, new_name)
            except Exception as e:
                logging.debug(f"`{affected_var_name}` constraints not updatable: {e}")

        # Update the constraint names if any
        def rename_constraint(name: str, old_name: str, new_name: str):
            match = re.match(Variable.CONSTRAINT_REGEX, name)
            if match is not None and match.group(2) == old_name:
                return name.replace(old_name, new_name)
            return name

        # Todo: this is even more inefficient :-(
        for key in self.var_req_mapping.keys():
            self.var_req_mapping[key] = {
                rename_constraint(name, old_name, new_name) for name in self.var_req_mapping[key]
            }

        # Update the req -> var mapping.
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)

        # Rename the enumerators in case this renaming affects an enum.
        affected_enumerators = []
        if self.collection[new_name].type in ["ENUM_INT", "ENUM_REAL"]:
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
            "bool": boogie_parsing.BoogieType.bool,
            "int": boogie_parsing.BoogieType.int,
            "enum_int": boogie_parsing.BoogieType.int,
            "enum_real": boogie_parsing.BoogieType.real,
            "enumerator_int": boogie_parsing.BoogieType.int,
            "enumerator_real": boogie_parsing.BoogieType.real,
            "real": boogie_parsing.BoogieType.real,
            "unknown": boogie_parsing.BoogieType.unknown,
            "error": boogie_parsing.BoogieType.error,
        }
        type_env = dict()
        for name, var in self.collection.items():
            if var.type is None:
                type_env[name] = mapping["unknown"]
            elif var.type.lower() in mapping.keys():
                type_env[name] = mapping[var.type.lower()]
            elif var.type == "CONST":
                # Check for int, real or unknown based on value.
                try:
                    float(var.value)
                except Exception:
                    type_env[name] = mapping["unknown"]
                    continue

                if "." in var.value:
                    type_env[name] = mapping["real"]
                    continue

                type_env[name] = mapping["int"]
            else:
                type_env[name] = mapping["unknown"]

        # Todo: Store this so we can reuse and update on collection change.
        return type_env

    def enum_type_mismatch(self, enum, type):
        enum_type = self.collection[enum].type
        accepted_type = replace_prefix(enum_type, "ENUM", "ENUMERATOR")

        return not type == accepted_type

    def set_type(self, name, type):
        if type in ["ENUMERATOR_INT", "ENUMERATOR_REAL"]:
            if self.enum_type_mismatch(self.collection[name].belongs_to_enum, type):
                raise TypeError("ENUM type mismatch")

        self.collection[name].set_type(type)

    def get_type(self, name):
        return self.collection[name].type

    def add_new_constraint(self, var_name):
        """Add a new empty constraint to var_name variable.
        :type var_name: str
        :param var_name:
        """
        return self.collection[var_name].add_constraint()

    def del_constraint(self, var_name, constraint_id):
        self.req_var_mapping.pop("Constraint_{}_{}".format(var_name, constraint_id), None)
        return self.collection[var_name].del_constraint(constraint_id)

    def refresh_var_constraint_mapping(self):
        def not_in_constraint(var_name, constraint_name):
            """Checks if var_name is used in constraint_name (if constraint_name is existing).

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

    def refresh_var_usage(self, app):
        mapping = dict()

        # Add the requirements using this variable.
        for req in app.db.get_objects(Requirement).values():
            for formalization in req.formalizations.values():
                try:
                    for var_name in formalization.used_variables:
                        if var_name not in mapping.keys():
                            mapping[var_name] = set()
                        mapping[var_name].add(req.rid)
                except TypeError:
                    pass
                except Exception as e:
                    logging.info("Could not read formalizations for `{}`: {}".format(req.rid, e))
                    raise e

        # Add the constraints using this variable.
        for var in self.collection.values():
            for constraint in var.get_constraints().values():
                for constraint_id, expression in enumerate(constraint.expressions_mapping.values()):
                    for var_name in expression.used_variables:
                        if var_name not in mapping.keys():
                            mapping[var_name] = set()
                        mapping[var_name].add("Constraint_{}_{}".format(var.name, constraint_id))

        self.var_req_mapping = mapping

    def del_var(self, var_name) -> bool:
        """Delete a variable if it is not used, or only used by its own constraints.

        :param var_name:
        :return: True on deletion else False.
        """
        deletable = False
        if var_name not in self.var_req_mapping:
            deletable = True
        else:
            constraint_pref = "Constraint_{}".format(var_name)
            affected_constraints = len([f for f in self.var_req_mapping[var_name] if constraint_pref in f])
            total_usages = len(self.var_req_mapping[var_name])
            if affected_constraints == total_usages:
                deletable = True

        if deletable:
            deleted_var = self.collection.pop(var_name, None)
            self.var_req_mapping.pop(var_name, None)
            if deleted_var:
                self.app.db.remove_object(deleted_var)
            return True
        return False

    def get_enumerators(self, enum_name: str) -> list["Variable"]:
        enumerators = []
        for other_var in self.collection.values():
            if other_var.belongs_to_enum == enum_name:
                enumerators.append(other_var)
        return enumerators

    def import_session(self, import_collection):
        """Import another VariableCollection into this.

        :param import_collection: The other VariableCollection
        """
        for var_name, variable in import_collection.collection.items():
            if var_name in self.collection:
                pass
            else:
                self.collection[var_name] = variable


@DatabaseTable(TableType.Folder)
@DatabaseID("uuid", use_uuid=True)
@DatabaseField("name", str)
@DatabaseField("type", str)
@DatabaseField("value", str)
@DatabaseField("tags", set[Tag])
@DatabaseField("script_results", str)
@DatabaseField("belongs_to_enum", str)
@DatabaseField("constraints", dict)
@DatabaseField("description", str)
class Variable:
    CONSTRAINT_REGEX = r"^(Constraint_)(.*)(_[0-9]+$)"

    def __init__(self, name: str, var_type: str | None, value: str | None):
        self.name: str = name
        self.type: str = var_type
        self.value: str = value
        # TODO: Show variables (e.g. typing errors) or remove tags from variables; show them or remove them
        self.tags: set[Tag] = set()
        self.script_results: str = ""
        self.belongs_to_enum: str = ""
        self.constraints = dict()
        self.description: str = ""

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
            "name": self.name,
            "type": self.type,
            "const_val": self.value,
            "used_by": used_by,
            "tags": [tag.name for tag in self.get_tags()],
            "type_inference_errors": type_inference_errors,
            "constraints": [constraint.get_string() for constraint in self.get_constraints().values()],
            "script_results": self.script_results,
            "belongs_to_enum": self.belongs_to_enum,
        }

        return d

    def add_tag(self, tag: Tag):
        self.tags.add(tag)

    def remove_tag(self, tag: Tag):
        self.tags.discard(tag)

    def get_tags(self):
        return self.tags

    def set_type(self, new_type):
        allowed_types = ["CONST"]
        allowed_types += boogie_parsing.BoogieType.get_valid_type_names()
        if new_type not in allowed_types:
            raise ValueError(f"Illegal variable type: `{new_type}`. Allowed types are: `{allowed_types}`")

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
        """Add a new empty constraint

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
            logging.debug(f"Constraint id `{id}` not found in var `{self.name}`")
            return False

    def get_constraints(self):
        return self.constraints

    def reload_constraints_type_inference_errors(self, var_collection):
        logging.info(f"Reload type inference for variable `{self.name}` constraints")
        self.remove_tag(current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value)
        for id in self.constraints:
            try:
                self.constraints[id].type_inference_check(var_collection)
                if len(self.constraints[id].type_inference_errors) > 0:
                    self.tags.add(current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value)
            except AttributeError as e:
                # Probably No pattern set.
                logging.info(f"Could not derive type inference for variable `{self.name}` constraint No. {id}. { e}")

    def update_constraint(self, constraint_id, scope_name, pattern_name, mapping, variable_collection):
        """Update a single constraint

        :param constraint_id:
        :param scope_name:
        :param pattern_name:
        :param mapping:
        :param variable_collection:
        :return:
        """
        # set scoped pattern
        self.constraints[constraint_id].scoped_pattern = ScopedPattern(Scope[scope_name], Pattern(name=pattern_name))
        # Parse and set the expressions.
        for key, expression_string in mapping.items():
            if len(expression_string) == 0:
                continue
            expression = Expression("Constraint_{}_{}".format(self.name, constraint_id))
            expression.set_expression(expression_string, variable_collection)
            if self.constraints[constraint_id].expressions_mapping is None:
                self.constraints[constraint_id].expressions_mapping = dict()
            self.constraints[constraint_id].expressions_mapping[key] = expression
        self.constraints[constraint_id].get_string()
        self.constraints[constraint_id].type_inference_check(variable_collection)

        if len(self.constraints[constraint_id].type_inference_errors) > 0:
            logging.debug(
                "Type inference Error in variable `{}` constraint `{}` at {}.".format(
                    self.name, constraint_id, [n for n in self.constraints[constraint_id].type_inference_errors.keys()]
                )
            )
            self.add_tag(current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value)

        variable_collection.collection[self.name] = self

        return variable_collection

    def update_constraints(self, constraints, app, variable_collection=None):
        """replace all constraints with :param constraints.

        :return: updated VariableCollection
        """
        logging.debug(f"Updating constraints for variable `{self.name}`.")
        self.remove_tag(current_app.db.get_object(SessionValue, "TAG_Type_inference_error").value)
        if variable_collection is None:
            variable_collection = VariableCollection(app)

        for constraint in constraints.values():
            logging.debug(f"Updating formalization No. {constraint['id']}.")
            logging.debug(f"Scope: `{constraint['scope']}`, Pattern: `{constraint['pattern']}`.")
            try:
                variable_collection = self.update_constraint(
                    constraint_id=int(constraint["id"]),
                    scope_name=constraint["scope"],
                    pattern_name=constraint["pattern"],
                    mapping=constraint["expression_mapping"],
                    variable_collection=variable_collection,
                )
            except Exception as e:
                logging.error(f"Could not update Constraint: {e.__str__()}.")
                raise e

        return variable_collection

    def rename_var_in_constraints(self, old_name, new_name):
        # replace in every formalization
        for index, constraint in self.get_constraints().items():
            for key, expression in constraint.expressions_mapping.items():
                if old_name not in expression.raw_expression:
                    continue
                new_expression = boogie_parsing.replace_var_in_expression(
                    expression=expression.raw_expression, old_var=old_name, new_var=new_name
                )
                self.constraints[index].expressions_mapping[key].raw_expression = new_expression
                self.constraints[index].expressions_mapping[key].used_variables.discard(old_name)
                self.constraints[index].expressions_mapping[key].used_variables.add(new_name)

    def rename(self, new_name):
        old_name = self.name
        self.name = new_name
        self.rename_var_in_constraints(old_name, new_name)

    def get_parent_enum(self, variable_collection):
        """Returns the parent enum in case this variable is an enumerator.

        :return: The parent enum name
        :param variable_collection:
        """
        result = ""
        if self.type == "ENUMERATOR":
            for other_var_name in variable_collection.collection.keys():
                if (
                    len(self.name) > len(other_var_name)
                    and variable_collection.collection[other_var_name].type == "ENUM"
                    and self.name.startswith(other_var_name)
                ):
                    result = other_var_name
                    break
        return result

    def get_enumerators(self, variable_collection):
        """Returns a list of enumerator names, in case this variable is an enum.

        :param variable_collection:
        :return: List of enumerator names.
        """
        result = []
        if self.type == "ENUM":
            for other_var_name in variable_collection.collection.keys():
                if (
                    len(self.name) < len(other_var_name)
                    and variable_collection.collection[other_var_name].type == "ENUMERATOR"
                    and other_var_name.startswith(self.name)
                ):
                    result.append(other_var_name)
                    break
        return result
