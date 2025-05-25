from os import path
from abc import ABC, abstractmethod
import re

from typing_extensions import Optional
import reqtransformer
from lib_core.data import Scope
from lib_core.utils import get_default_pattern_options


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
    def create_prompt(
        self,
        requirement_to_formalize: reqtransformer.Requirement,
        requirement_with_formalization: list[reqtransformer.Requirement],
        used_variables: list[dict],
    ) -> Optional[str]:
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

    @staticmethod
    def check_ai_should_formalized(req) -> bool:
        """Method which checks if the Requirement can be Ai formalized."""
        return not req.to_dict(include_used_vars=True)["formal"]

    @staticmethod
    def check_template_for_ai_formalization(req) -> bool:
        """Method which checks if the Requirement can be used as example for Ai formalization."""
        req = req.to_dict(include_used_vars=True)
        return "has_formalization" in req["tags"]


def get_scope() -> dict[str, str]:
    """returns like: {AFTER: After '{P}'}"""
    scope_dict = {scope.name: scope.value for scope in Scope if scope.name != "NONE"}
    return scope_dict


def get_pattern() -> dict[str, dict[str, str | dict[str, str]]]:
    """
    Keys = pattern name with two values:
    [pattern]["env"] (The allowed types for the variables/expressions if available)
    [pattern]["pattern"] (the pattern as string)

    like: 'Universality': {'env': {'R': ['bool']}, 'pattern': 'it is always the case that {R} holds'}
    """
    # TODO primitive fix for new function
    pattern_dict = {}
    option_pattern = re.compile(r'<option value="([^"]+)">([^<]+)</option>')
    for match in option_pattern.finditer(get_default_pattern_options()):
        key = match.group(1)
        text = match.group(2)

        if key == "NotFormalizable":
            continue
        cleaned_text = re.sub(r'"\{([A-Z])\}"', r'{\1}', text)
        pattern_dict[key] = {"pattern": cleaned_text}
    return pattern_dict


def get_grammar() -> str:
    """returns the grammar from lark file as string"""
    grammar_path = path.join(path.dirname(path.abspath(__file__)), "../../hanfor_boogie_grammar.lark")
    with open(grammar_path, "r") as f:
        grammar = f.read()
    return grammar
