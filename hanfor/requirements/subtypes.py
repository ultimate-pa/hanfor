import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, wraps
from typing import ClassVar, Generic, TypeVar

from hanfor_flask import current_app
from json_db_connector.json_db import DatabaseKeyError
from lib_core.data import (
    Formalization,
    FormalizationType,
    Requirement,
    RequirementElement,
    SessionValue,
    Tag,
    Variable,
    VariableCollection,
)
from lib_core.utils import delete_variable_everywhere, rename_variable_everywhere
from requirements.desc_highlighting import delete_variables, new_variables_regenerate_highlighting


@dataclass
class SubtypeContext:
    """What every request against a formalization subtype needs, loaded once.

    `variable_collection` and `standard_tags` are lazy, since building the collection walks every
    requirement times every element, and the paths that answer 404 never actually need it
    """

    rid: str
    requirement: Requirement

    @classmethod
    def load(cls, rid: str) -> "SubtypeContext":
        try:
            return cls(rid=rid, requirement=current_app.db.get_object(Requirement, rid))
        except DatabaseKeyError as e:
            raise SubtypeNotFound(f"Requirement '{rid}' not found.") from e

    # TODO: Check if the caching of this is actually okay, if it introduces errors
    @cached_property
    def variable_collection(self) -> VariableCollection:
        return VariableCollection(
            current_app.db.get_objects(Variable).values(),
            current_app.db.get_objects(Requirement).values(),
        )

    @cached_property
    def standard_tags(self) -> dict[str, Tag]:
        return SessionValue.get_standard_tags(current_app.db)


class SubtypeError(Exception):
    """A subtype operation failed. `status` is what the resource should answer with."""

    status = 400


class SubtypeNotFound(SubtypeError):
    """No element of the requested subtype exists under that id."""

    status = 404


class InvalidPayload(SubtypeError):
    """The request body cannot be applied to this subtype."""

    status = 400


def subtype_errors_to_response(view):
    """
    Translate `SubtypeError` into the `(body, status)` pair flask_restx expects,
    keeps http out of the subtype logic
    """

    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except SubtypeError as exc:
            return {"success": False, "errormsg": str(exc)}, exc.status

    return wrapper


E = TypeVar("E", bound=RequirementElement)


class SubtypeHandler(ABC, Generic[E]):
    """Everything one subtype does in response to a write, in one object.

    Handlers mutate what `ctx` reaches and raise `SubtypeError` on
    failure. Persisting and turning the outcome into a response is the `flask` job, which is what makes
    a handler callable from a script or a test with no request in sight.
    """

    name: ClassVar[FormalizationType]
    model: type[E]

    @abstractmethod
    def create(self, ctx: "SubtypeContext", fid: str, data: dict) -> int:
        """Attach a new element and return the id it was given.

        `fid` is the temporary id the client used in the URL. Only the server assigns
        the real one, so a second client cannot pick the same id.
        """

    @abstractmethod
    def patch(self, ctx: "SubtypeContext", fid: str, data: dict) -> None:
        """Apply the fields present in `data`, leaving the rest as they are."""

    @abstractmethod
    def replace(self, ctx: "SubtypeContext", fid: str, data: dict) -> None:
        """Overwrite the element, requiring every field `data` must carry (PUT semantics)"""

    def fetch(self, ctx: "SubtypeContext", fid: str) -> E:
        """The identity check, once, for every subtype."""
        element = ctx.requirement.formalizations.get(int(fid)) if str(fid).isdigit() else None
        if not isinstance(element, self.model):
            raise SubtypeNotFound(f"{self.name.capitalize()} not found.")
        return element

    @staticmethod
    def handler_for(ctx: "SubtypeContext", fid: str) -> "SubtypeHandler":
        element = ctx.requirement.formalizations.get(int(fid)) if str(fid).isdigit() else None
        if element is None:
            raise SubtypeNotFound("Formalization not found.")
        return SUBTYPES[element.of_type()].handler

    def serialize(self, ctx: "SubtypeContext", fid: str) -> dict:
        element = self.fetch(ctx, fid)
        return {
            **element.to_dict(var_collection=ctx.variable_collection),
            "formalization_type": element.of_type(),
            "id": int(fid),
            "text": element.get_string(),
            "is_constraint": element.is_constraint,
        }

    def delete(self, ctx: "SubtypeContext", fid: str) -> None:
        """Remove the element, then derive the formalization tags again from what is left."""
        self.fetch(ctx, fid)
        ctx.requirement.delete_formalization(int(fid), ctx.variable_collection)
        ctx.requirement.recompute_formalization_tags(ctx.standard_tags)


class FormalizationHandler(SubtypeHandler[Formalization]):
    name = "formalization"
    model = Formalization

    def create(self, ctx: "SubtypeContext", fid: str, data: dict) -> int:
        # NOTE: `None` counts as missing, would this be good practice?
        missing = [key for key in ("scope", "pattern", "expression_mapping") if data.get(key) is None]
        if missing:
            raise InvalidPayload(f"Missing required field(s): {', '.join(missing)}")

        fid, _ = ctx.requirement.add_empty_formalization()
        try:
            ctx.requirement.update_formalization(
                fid,
                data["scope"],
                data["pattern"],
                data["expression_mapping"],
                ctx.variable_collection,
                ctx.standard_tags,
            )
            for v in ctx.variable_collection.new_vars:
                current_app.db.add_object(v)
            if current_app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"]:
                new_variables_regenerate_highlighting(ctx.variable_collection.new_vars)
            if "is_constraint" in data:
                ctx.requirement.formalizations[fid].is_constraint = bool(data["is_constraint"])
            # now rerun the inference checks, expensive but works (and we dont care)
            ctx.requirement.run_type_checks(ctx.variable_collection, ctx.standard_tags)
        except Exception as e:
            # A create that fails must leave nothing behind, including a half applied draft
            ctx.requirement.formalizations.pop(fid, None)
            raise InvalidPayload(f"Could not parse draft: `{e}`") from e
        return fid

    def patch(self, ctx: "SubtypeContext", fid: str, data: dict) -> None:
        formalization = self.fetch(ctx, fid)
        self._update(
            ctx,
            fid,
            data.get("scope", formalization.scoped_pattern.scope.name),
            data.get("pattern", formalization.scoped_pattern.pattern.get_name()),
            {
                **{k: v.raw_expression for k, v in formalization.expressions_mapping.items()},
                **data.get("expression_mapping", {}),
            },
        )

    def replace(self, ctx: "SubtypeContext", fid: str, data: dict) -> None:
        if "scope" not in data or "pattern" not in data or "expression_mapping" not in data:
            raise InvalidPayload("scope, pattern, and expression_mapping are required")

        self.fetch(ctx, fid)
        self._update(ctx, fid, data["scope"], data["pattern"], data["expression_mapping"])

    @staticmethod
    def _update(ctx: "SubtypeContext", fid: str, scope: str, pattern: str, mapping: dict) -> None:
        """The half `patch` and `replace` share; they differ only in how they arrive at the arguments."""
        try:
            ctx.requirement.update_formalization(
                int(fid), scope, pattern, mapping, ctx.variable_collection, ctx.standard_tags
            )
            for v in ctx.variable_collection.new_vars:
                current_app.db.add_object(v)
        except KeyError as e:
            raise InvalidPayload(f"Could not update formalization: {e}") from e
        except Exception as e:
            raise InvalidPayload(f"Could not parse formalization: `{e}`") from e


class VariableHandler(SubtypeHandler[Variable]):
    name = "variable"
    model = Variable

    def create(self, ctx: "SubtypeContext", fid: str, data: dict) -> int:
        logging.debug(f"Data set by the variable: {data}")
        assigned_fid = ctx.requirement.next_id()
        try:
            var = Variable(data["name"], data["type"], value=data.get("value"), order=assigned_fid)
            var.set_type(data["type"])
        except ValueError as e:
            raise InvalidPayload(str(e)) from e

        if ctx.variable_collection.add_var(var.name, var) is None:
            raise InvalidPayload(f"A variable named `{var.name}` already exists.")
        current_app.db.add_object(var)

        ctx.requirement.add_formalization_with_id(var, assigned_fid)
        self._apply_enumerators(ctx, data["name"], data["type"], data.get("enumerators", []))
        return assigned_fid

    def patch(self, ctx: "SubtypeContext", fid: str, data: dict) -> None:
        variable = self.fetch(ctx, fid)

        if "name" in data:
            self._rename(ctx, variable, data["name"])
        if "type" in data:
            try:
                variable.set_type(data["type"])
            except ValueError as e:
                raise InvalidPayload(str(e)) from e
        if "value" in data:
            variable.value = data["value"]
        if "order" in data:
            variable.order = int(data["order"])

        if "enumerators" in data:
            self._apply_enumerators(ctx, variable.name, variable.type, data["enumerators"])

    def replace(self, ctx: "SubtypeContext", fid: str, data: dict) -> None:
        if "name" not in data or "type" not in data:
            raise InvalidPayload("name and type are required")

        variable = self.fetch(ctx, fid)
        self._rename(ctx, variable, data["name"])
        variable.type = data["type"]
        variable.value = data.get("value", "")
        variable.order = int(data.get("order", 0))

        if "enumerators" in data:
            self._apply_enumerators(ctx, variable.name, variable.type, data["enumerators"])

    def delete(self, ctx: "SubtypeContext", fid: str) -> None:
        variable = self.fetch(ctx, fid)
        super().delete(ctx, fid)
        collection = ctx.variable_collection
        names = [variable.name, *(e.name for e in collection.get_enumerators(variable.name))]
        if any(collection.is_used(name) for name in names):
            return
        for name in names:
            delete_variable_everywhere(collection, name)
        if current_app.config["FEATURE_VARIABLE_DESCRIPTION_HIGHLIGHTING"]:
            delete_variables(names)

    @staticmethod
    def _rename(ctx: "SubtypeContext", variable: Variable, new_name: str) -> None:
        if new_name == variable.name:
            return
        if ctx.variable_collection.var_name_exists(new_name):
            raise InvalidPayload(f"A variable named `{new_name}` already exists.")

        try:
            rename_variable_everywhere(ctx.variable_collection, variable.name, new_name)
        except (KeyError, ValueError) as e:
            raise InvalidPayload(str(e)) from e

    @staticmethod
    def _apply_enumerators(ctx: "SubtypeContext", name: str, var_type: str, enumerators: list) -> None:
        success, errormsg, _ = ctx.variable_collection.create_enum_variable(name, var_type, enumerators)
        if not success:
            raise InvalidPayload(errormsg)


@dataclass(frozen=True)
class SubtypeSpec:
    name: FormalizationType
    model: type[RequirementElement]
    handler: SubtypeHandler


SUBTYPES: dict[str, SubtypeSpec] = {}


def register(handler: SubtypeHandler) -> None:
    SUBTYPES[handler.name] = SubtypeSpec(handler.name, handler.model, handler)


register(FormalizationHandler())
register(VariableHandler())
