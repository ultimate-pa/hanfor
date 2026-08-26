from dataclasses import dataclass
from functools import cached_property, wraps

from hanfor_flask import current_app
from lib_core.data import Requirement, SessionValue, Tag, Variable, VariableCollection


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
        return cls(rid=rid, requirement=current_app.db.get_object(Requirement, rid))

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
