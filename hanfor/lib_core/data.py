import datetime
import difflib
import json
import logging
import re
import string
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, Iterable, Union
from uuid import uuid4

from lark import LarkError
from typing_extensions import deprecated

from configuration.patterns import APattern
from hanfor_flask import HanforFlask
from json_db_connector.json_db import (
    DatabaseTable,
    TableType,
    DatabaseID,
    DatabaseField,
    DatabaseNonSavedField,
    DatabaseFieldType,
    JsonDatabase,
)
from lib_core import boogie_parsing
from lib_core.boogie_parsing import run_typecheck_fixpoint, BoogieType


@DatabaseTable(TableType.File)
@DatabaseID("uuid", use_uuid=True)
@DatabaseField("name", str)
@DatabaseField("color", str)
@DatabaseField("internal", bool)
@DatabaseField("description", str)
@DatabaseField("mutable", bool, True)
@DatabaseNonSavedField("used_by", [])
@dataclass
class Tag:
    name: str
    color: str
    internal: bool
    description: str
    mutable: bool = True  # if a Tag is not mutable then it can not be deleted and the name can not be changed
    used_by: list = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid4()))

    def __hash__(self):
        return hash(self.uuid)


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
    def __init__(self, rid: str, description: str, type_in_csv: str, csv_row: dict[str, str], pos_in_csv: int):
        self.rid: str = rid
        self.formalizations: dict[int, Formalization] = dict()
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
    def revision_diff(self) -> dict[str, str]:
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
                # This can happen if we create revision with an CSV that is missing the csv_key now.
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

    def add_empty_formalization(self) -> tuple[int, "Formalization"]:
        """Add an empty formalization to the formalizations list."""
        fid = self._next_free_formalization_id()
        self.formalizations[fid] = Formalization(fid)
        return fid, self.formalizations[fid]

    def delete_formalization(self, formalization_id, variable_collection: "VariableCollection"):
        formalization_id = int(formalization_id)

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

    def update_formalization(
        self,
        formalization_id: int,
        scope_name: str,
        pattern_name: str,
        mapping: dict[str, str],
        variable_collection: "VariableCollection",
        standard_tags: dict[str, Tag],
    ):
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
            formatted_errors = self.format_error_tag(self.formalizations[formalization_id], standard_tags)
            self.tags[standard_tags["TAG_Type_inference_error"]] = formatted_errors

        # Add 'unknown_type' tag
        vars_with_unknown_type = []
        vars_with_unknown_type = self.formalizations[formalization_id].unknown_types_check(
            variable_collection, vars_with_unknown_type
        )
        if vars_with_unknown_type:
            self.tags[standard_tags["TAG_unknown_type"]] = self.format_unknown_type_tag(vars_with_unknown_type)

        if (
            self.formalizations[formalization_id].scoped_pattern.scope != Scope.NONE
            and self.formalizations[formalization_id].scoped_pattern.pattern.get_name() != "NotFormalizable"
        ):
            self.tags[standard_tags["TAG_has_formalization"]] = ""
        else:
            self.tags[standard_tags["TAG_incomplete_formalization"]] = self.format_incomplete_formalization_tag(
                formalization_id, standard_tags
            )

    def format_error_tag(self, formalisation: "Formalization", standard_tags: dict[str, Tag]) -> str:
        if standard_tags["TAG_Type_inference_error"] not in self.tags:
            result = ""
        else:
            result = self.tags[standard_tags["TAG_Type_inference_error"]]

        if not formalisation.type_inference_errors:
            return result
        for key, value in formalisation.type_inference_errors.items():
            result += f"{self.rid}_{str(formalisation.id)} ({key}): \n- "
            result += "\n- ".join(value) + "\n"
        return result

    @staticmethod
    def format_unknown_type_tag(variables: list[str]) -> str:
        return ", ".join(sorted(variables))

    def format_incomplete_formalization_tag(self, fid: int, standard_tags: dict[str, Tag]) -> str:
        rid_fid = self.rid + "_" + fid.__str__()
        if standard_tags["TAG_incomplete_formalization"] not in self.tags:
            return "- " + rid_fid
        else:
            return self.tags[standard_tags["TAG_incomplete_formalization"]] + "\n- " + rid_fid

    def update_formalizations(self, formalizations: dict, standard_tags: dict[str, Tag], variable_collection):
        if standard_tags["TAG_Type_inference_error"] in self.tags:
            self.tags.pop(standard_tags["TAG_Type_inference_error"])
        if standard_tags["TAG_unknown_type"] in self.tags:
            self.tags.pop(standard_tags["TAG_unknown_type"])
        if standard_tags["TAG_incomplete_formalization"] in self.tags:
            self.tags.pop(standard_tags["TAG_incomplete_formalization"])
        if standard_tags["TAG_has_formalization"] in self.tags:
            self.tags.pop(standard_tags["TAG_has_formalization"])
        logging.debug(f"Updating formalisations of requirement {self.rid}.")
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
                    variable_collection=variable_collection,
                    standard_tags=standard_tags,
                )
            except Exception as e:
                logging.error(f"Could not update Formalization: {e.__str__()}")
                raise e

    def run_type_checks(self, var_collection, standard_tags: dict[str, Tag]):
        logging.info(f"Run type inference and unknown check for `{self.rid}`")
        if standard_tags["TAG_Type_inference_error"] in self.tags:
            self.tags.pop(standard_tags["TAG_Type_inference_error"])
        if standard_tags["TAG_unknown_type"] in self.tags:
            self.tags.pop(standard_tags["TAG_unknown_type"])
        vars_with_unknown_type = []
        for fid in self.formalizations.keys():
            # Run type inference check
            self.formalizations[fid].type_inference_check(var_collection)
            if len(self.formalizations[fid].type_inference_errors) > 0:
                self.tags[standard_tags["TAG_Type_inference_error"]] = self.format_error_tag(
                    self.formalizations[fid], standard_tags
                )

            # Check for variables of type 'unknown' in formalization
            vars_with_unknown_type = self.formalizations[fid].unknown_types_check(
                var_collection, vars_with_unknown_type
            )
            if vars_with_unknown_type:
                self.tags[standard_tags["TAG_unknown_type"]] = self.format_unknown_type_tag(vars_with_unknown_type)

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
    def __init__(self, fid: int):
        self.id: int = fid
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
    ) -> list["Variable"]:
        """Parse expression mapping.
            + Extract variables. Replace by their ID. Create new Variables if they do not exist.
            + For used variables and update the "used_by_requirements" set.

        :param mapping: {'P': 'foo > 0', 'Q': 'expression for Q', ...}
        :param variable_collection: Currently used VariableCollection.
        :param rid: associated requirement id

        :return: type_inference_errors dict {key: type_env, ...}
        """
        changes = False
        new_vars = []
        for key, expression_string in mapping.items():
            if key not in self.expressions_mapping:
                self.expressions_mapping[key] = Expression(rid)
            if self.expressions_mapping[key].expression_changed(expression_string):
                new_vars = self.expressions_mapping[key].set_expression(expression_string, variable_collection)
                changes = True
        if changes:
            self.type_inference_check(variable_collection)
        return new_vars

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
                    f"Lark could not parse expression `{expression.raw_expression}`: {e}. Skipping type inference"
                )
                continue

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
            "pattern": self.scoped_pattern.pattern.get_name(),
            "expressions": {key: exp.raw_expression for key, exp in self.expressions_mapping.items()},
        }

        return d

    def get_string(self):
        return self.scoped_pattern.get_string(self.expressions_mapping)

    def __repr__(self):
        return f"<{self.__class__.__name__} rid={self.id}: {self.scoped_pattern}>"


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
        self.used_variables: set[str] = set()  # TODO use Variable objects instead of str
        self.raw_expression = ""
        self.parent_rid = parent_rid

    def expression_changed(self, expression: str):
        return expression != self.raw_expression

    def set_expression(self, expression: str, variable_collection: "VariableCollection") -> list["Variable"]:
        """Parses the Expression using the boogie grammar.
        * Extract variables.
            + Create new ones if not in Variable collection.
            + Replace Variables by their identifier.
        * Store set of used variables to `self.used_variables`
        """
        logging.debug(f"Setting expression: `{expression}`")
        self.raw_expression = expression
        # Get the vars occurring in the expression.
        tree = boogie_parsing.get_parser_instance().parse(expression)

        new_vars = []
        self.used_variables = set(boogie_parsing.get_variables_list(tree))
        for var_name in self.used_variables:
            if var_name not in variable_collection:
                assert var_name is not None  # TODO: remove, not sure if this may happen here
                variable = variable_collection.add_var(var_name)
                new_vars.append(variable)

        variable_collection.map_req_to_vars(self.parent_rid, self.used_variables)
        return new_vars

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
        self.pattern = APattern.get_pattern(name)._pattern_text
        self.environment = APattern.get_pattern(name)._env

    def get_name(self):
        # TODO: hack to update the pattern names to new names
        #  (move to database update when we are able do that)
        self.name = APattern.get_pattern(self.name).__class__.__name__
        return self.name

    def is_instantiatable(self):
        return self.name != "NotFormalizable"

    def instantiate(self, scope: Scope, *args):
        return str(scope) + ", " + self.pattern.format(*args)

    def __str__(self):
        return self.pattern

    def get_allowed_types(self):
        return BoogieType.alias_env_to_instantiated_env(APattern.get_pattern(self.name)._env)


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
        except KeyError:
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
        return self.scope.get_slug()

    def get_pattern_slug(self):
        return self.pattern.get_name()

    def __str__(self):
        return str(self.scope) + ", " + str(self.pattern)

    def get_allowed_types(self):
        result = self.scope.get_allowed_types()
        result.update(self.pattern.get_allowed_types())
        return result


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

    def __init__(self, name: str, var_type: str | None, value: str | None = None):
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
        type_inference_errors = dict()
        for index, f in self.get_constraints().items():
            if f.type_inference_errors:
                type_inference_errors[index] = [key.lower() for key in f.type_inference_errors.keys()]
        used_by = sorted(list(var_req_mapping[self.name])) if self.name in var_req_mapping else []

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
        while i in self.constraints.keys():
            i += 1
        return i

    def add_constraint(self):
        """Add a new empty constraint

        :return: (index: int, The constraint: Formalization)
        """
        fid = self._next_free_constraint_id()
        self.constraints[fid] = Formalization(fid)
        return fid

    def del_constraint(self, cid):
        if cid in self.constraints:
            del self.constraints[cid]
            return True
        logging.debug(f"Constraint id `{cid}` not found in var `{self.name}`")
        return False

    def get_constraints(self):
        return self.constraints

    def reload_constraints_type_inference_errors(
        self, var_collection: "VariableCollection", standard_tags: dict[str, Tag]
    ):
        logging.info(f"Reload type inference for variable `{self.name}` constraints")
        self.remove_tag(standard_tags["TAG_Type_inference_error"])
        for cid in self.constraints:
            try:
                self.constraints[cid].type_inference_check(var_collection)
                if len(self.constraints[cid].type_inference_errors) > 0:
                    self.tags.add(standard_tags["TAG_Type_inference_error"])
            except AttributeError as e:
                # Probably No pattern set.
                logging.info(f"Could not derive type inference for variable `{self.name}` constraint No. {cid}. {e}")

    def update_constraint(
        self,
        constraint_id: int,
        scope_name: str,
        pattern_name: str,
        mapping: dict[str, str],
        variable_collection: "VariableCollection",
        standard_tags: dict[str, Tag],
    ):
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
            if expression.expression_changed(expression_string):
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
            self.add_tag(standard_tags["TAG_Type_inference_error"])

        variable_collection.collection[self.name] = self

        return variable_collection

    def update_constraints(self, constraints, variable_collection, standard_tags):
        """replace all constraints with :param constraints.

        :return: updated VariableCollection
        """
        logging.debug(f"Updating constraints for variable `{self.name}`.")
        self.remove_tag(standard_tags["TAG_Type_inference_error"])

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
                    standard_tags=standard_tags,
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


class VariableCollection:
    def __init__(self, variables: Iterable[Variable], requierments: Iterable[Requirement]):
        self.collection: dict[str, Variable] = {v.name: v for v in variables}
        self.var_req_mapping = dict()
        self.refresh_var_usage(requierments)
        self.req_var_mapping = self.invert_mapping(self.var_req_mapping)
        self.new_vars: set[Variable] = set()

    def __contains__(self, item):
        return item in self.collection

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

    def add_var(self, var_name, variable=None) -> Variable:
        if not self.var_name_exists(var_name):
            if variable is None:
                variable = Variable(var_name, None, None)
            logging.debug(f"Adding variable `{var_name}` to collection.")
            self.collection[variable.name] = variable
            self.new_vars.add(variable)
            return variable
        return None

    def store(self):
        self.var_req_mapping = self.invert_mapping(self.req_var_mapping)

    @staticmethod
    def invert_mapping(mapping):
        new_dict = {}
        for k in mapping:
            for v in mapping[k]:
                new_dict.setdefault(v, set()).add(k)
        return new_dict

    def map_req_to_vars(self, rid, used_variables):
        """Map a requirement by rid to used vars."""

        if rid not in self.req_var_mapping.keys():
            self.req_var_mapping[rid] = set()
        for var in used_variables:
            self.req_var_mapping[rid].add(var)

    def rename(self, old_name: str, new_name: str, app: HanforFlask) -> list[tuple[str, str]]:
        """Rename a var in the collection. Merges the variables if new_name variable exists.

        :param old_name: The old var name.
        :param new_name: The new var name.
        :param app: the app
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
        # Copy back Constraints
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
        def rename_constraint(name: str, old_constraint_name: str, new_constraint_name: str):
            match = re.match(Variable.CONSTRAINT_REGEX, name)
            if match is not None and match.group(2) == old_constraint_name:
                return name.replace(old_constraint_name, new_constraint_name)
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
                except ValueError:
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

    def enum_type_mismatch(self, enum, new_type):
        enum_type = self.collection[enum].type
        accepted_type = replace_prefix(enum_type, "ENUM", "ENUMERATOR")

        return not new_type == accepted_type

    def set_type(self, name, new_type):
        if new_type in ["ENUMERATOR_INT", "ENUMERATOR_REAL"]:
            if self.enum_type_mismatch(self.collection[name].belongs_to_enum, new_type):
                raise TypeError("ENUM type mismatch")

        self.collection[name].set_type(new_type)

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
                    if constraint_name in self.req_var_mapping and var_name in self.req_var_mapping[constraint_name]:
                        self.req_var_mapping[constraint_name].discard(var_name)
                    return True
                else:
                    # The variable exists. Now check if var_name occurs in one of its constraints.
                    for constraint in self.collection[constraint_variable_name].get_constraints().values():
                        if var_name in constraint.get_string():
                            return False
                    if constraint_name in self.req_var_mapping and var_name in self.req_var_mapping[constraint_name]:
                        self.req_var_mapping[constraint_name].discard(var_name)
                    return True

            return False

        for name, variable in self.collection.items():
            if name in self.var_req_mapping:
                self.var_req_mapping[name] = {
                    c_name for c_name in self.var_req_mapping[name] if not not_in_constraint(name, c_name)
                }

    def reload_type_inference_errors_in_constraints(self, standard_tags: dict[str, Tag]):
        for name, var in self.collection.items():
            if len(var.get_constraints()) > 0:
                var.reload_constraints_type_inference_errors(self, standard_tags)

    def refresh_var_usage(self, requirements: Iterable[Requirement]):
        mapping = dict()

        # Add the requirements using this variable.
        for req in requirements:
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

    def del_var(self, var_name) -> Union[Variable, None]:
        """Check if a variable can be deleted ie, is not used somewhere.

        :param var_name:
        :return: variable to delete from db or None
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
                return deleted_var
        return None

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


@DatabaseTable(TableType.File)
@DatabaseID("id", use_uuid=True)
@DatabaseField("timestamp", datetime.datetime)
@DatabaseField("message", str)
@DatabaseField("requirements", list[Requirement])
@dataclass()
class RequirementEditHistory:
    timestamp: datetime.datetime
    message: str
    requirements: list[Requirement]
    id: str = field(default_factory=lambda: str(uuid4()))


@DatabaseTable(TableType.File)
@DatabaseID("name", str)
@DatabaseField("value", dict)
@dataclass()
class SessionValue:
    name: str
    value: Any

    @staticmethod
    def get_standard_tags(db: JsonDatabase) -> dict[str, Tag]:
        standard_tags = dict()
        tag_ids = [
            "TAG_Type_inference_error",
            "TAG_unknown_type",
            "TAG_has_formalization",
            "TAG_incomplete_formalization",
        ]
        for tid in tag_ids:
            standard_tags[tid] = db.get_object(SessionValue, tid).value
        return standard_tags


def replace_prefix(input_string: str, prefix_old: str, prefix_new: str):
    """Replace the prefix (prefix_old) of a string with (prefix_new).
    String remains unchanged if prefix_old is not matched.

    :param input_string: To be changed.
    :param prefix_old: Existing prefix of the string.
    :param prefix_new: Replacement prefix.
    :return: String with prefix_old replaced by prefix_new.
    """
    if input_string.startswith(prefix_old):
        input_string = "".join((prefix_new, input_string[len(prefix_old) :]))
    return input_string
