from typing import Optional
from ai.strategies import ai_prompt_parse_abstract_class
import re, json
import logging

from reqtransformer import Requirement


class PromptDump(ai_prompt_parse_abstract_class.AiPromptParse):
    @property
    def name(self) -> str:
        return "Small Prompt"

    @property
    def description(self) -> str:
        return "Only Input with small instruction"

    def create_prompt(
        self,
        requirement_to_formalize: Requirement,
        requirement_with_formalization: list[Requirement],
        used_variables: list[dict],
    ) -> Optional[str]:
        input_ai_formalization = requirement_to_formalize.to_dict()["desc"]
        if len(requirement_with_formalization) > 0:
            input_human_formalization = requirement_with_formalization[0].to_dict()["desc"]
            human_readable_human_formalization = requirement_with_formalization[0].to_dict()["formal"]
            db_human_formalization = requirement_with_formalization[0].get_formalizations_json()

        prompt_instructions = """
        Write only the following as an answer and replace only the TODOs. Do not add anything else. Use only the given patterns, if it is not possible to use them just write Terminate:
        Output Human readable: TODO
        Output for the server: {'scope': TODO, 'pattern': TODO, 'expression_mapping': {'P': TODO, 'Q': TODO, 'R': TODO, 'S': TODO, 'T': TODO, 'U': TODO, 'V': TODO}}
        """

        prompt_input = ""
        if len(requirement_with_formalization) > 0:
            prompt_input = f""" input: {input_human_formalization}
                        Output Human readable: {human_readable_human_formalization}
                        Output for the server: {db_human_formalization}"""
        prompt_input += f"Formalize this input: {input_ai_formalization}"

        prompt = prompt_instructions + prompt_input

        return prompt

    def parse_ai_response(
        self, ai_response: str, used_variables: list[dict]
    ) -> Optional[dict[str, str | dict[str, str]]]:
        server_output_match = re.search(r"Output for the server:\s*({.*})", ai_response, re.DOTALL)
        try:
            if server_output_match:
                server_output_str = server_output_match.group(1)
                server_output_str = server_output_str.replace("'", '"')
                server_output_dict = json.loads(server_output_str)
                parsed_ai_response = server_output_dict

                formalized_output = {
                    "scope": parsed_ai_response.get("scope", "GLOBALLY"),
                    "pattern": parsed_ai_response.get("pattern", "Universality"),
                    "expression_mapping": parsed_ai_response.get("expression_mapping", {}),
                }
                return formalized_output
        except Exception as e:
            logging.warning(f"Could not parse AI-response: {e}")
        return None
