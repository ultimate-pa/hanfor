import os
from abc import ABC, abstractmethod
from typing_extensions import Optional
from hanfor.patterns import PATTERNS
import reqtransformer


class AiPromptParse(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the similarity algorithm (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the similarity algorithm (visible in Hanfor)"""
        pass

    @abstractmethod
    def create_prompt(self, req_formal, req_ai, used_variables: list[dict]) -> Optional[str]:
        """Generating Prompt for AI (if error return None)"""
        pass

    @abstractmethod
    def parse_ai_response(
        self, ai_response: str, used_variables: list[dict]
    ) -> Optional[dict[str, str | dict[str, str]]]:
        """
        Parsing AI Response from the created Prompt (if error return None)
        Must be:
        {
        "scope": str
        "pattern": str
        "expression_mapping": dict
        }
        """
        pass


def get_scope() -> dict[str, str]:
    scope_dict = {scope.name: scope.value for scope in reqtransformer.Scope}
    return scope_dict


def get_pattern() -> dict[str, dict[str, str | dict[str, str]]]:
    """
    returns a dictionary Keys = scope with two values:
    [pattern]["env"] (The allowed types for the variables/expressions if available)
    [pattern]["pattern"] (the pattern as string)
    """
    pattern = {}
    for key, val in PATTERNS.items():
        if val["group"] != "Legacy":
            pattern[key] = {}
            if "env" in val:
                pattern[key]["env"] = val["env"]
            if "pattern" in val:
                pattern[key]["pattern"] = val["pattern"]
    return pattern


def get_grammar() -> str:
    """returns the grammar from lark file as string"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../hanfor_boogie_grammar.lark")
    with open(path, "r") as f:
        grammar = f.read()
    return grammar
