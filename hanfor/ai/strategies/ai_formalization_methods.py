import re, json
import logging

prompt_suffix = """
Possible to use [Scope: Pattern]:
Response: it is always the case that if [R] holds then [S] eventually holds
ResponseChain1-2: it is always the case that if [R] holds then [S] eventually holds and is succeeded by [T]
ConstrainedChain: it is always the case that if [R] holds then [S] eventually holds and is succeeded by [T], where [U] does not hold between [S] and [T]
Precedence: it is always the case that if [R] holds then [S] previously held
PrecedenceChain2-1: it is always the case that if [R] holds then [S] previously held and was preceded by [T]
PrecedenceChain1-2: it is always the case that if [R] holds and is succeeded by [S], then [T] previously held
Universality: it is always the case that [R] holds
UniversalityDelay: it is always the case that [R] holds after at most [S] time units
BoundedExistence: transitions to states in which [R] holds occur at most twice
Invariant: it is always the case that if [R] holds, then [S] holds as well
Absence: it is never the case that [R] holds
BoundedResponse: it is always the case that if [R] holds, then [S] holds after at most [T] time units
BoundedRecurrence: it is always the case that [R] holds at least every [S] time units
MaxDuration: it is always the case that once [R] becomes satisfied, it holds for less than [S] time units
TimeConstrainedMinDuration: it is always the case that if [R] holds for at least [S] time units, then [T] holds afterwards for at least [U] time units
BoundedInvariance: it is always the case that if [R] holds, then [S] holds for at least [T] time units
TimeConstrainedInvariant: it is always the case that if [R] holds for at least [S] time units, then [T] holds afterwards
MinDuration: it is always the case that once [R] becomes satisfied, it holds for at least [S] time units
ConstrainedTimedExistence: it is always the case that if [R] holds, then [S] holds after at most [T] time units for at least [U] time units
BndTriggeredEntryConditionPattern: it is always the case that after [R] holds for at least [S] time units and [T] holds, then [U] holds
BndTriggeredEntryConditionPatternDelayed: it is always the case that after [R] holds for at least [S]  time units and [T] holds, then [U] holds after at most [V]  time units
EdgeResponsePatternDelayed: it is always the case that once [R] becomes satisfied, [S] holds after at most [T] time units
BndEdgeResponsePattern: it is always the case that once [R] becomes satisfied, [S] holds for at least [T] time units
BndEdgeResponsePatternDelayed: it is always the case that once [R] becomes satisfied, [S] holds after at most [T] time units for at least [U] time units
BndEdgeResponsePatternTU : it is always the case that once [R] becomes satisfied and holds for at most [S] time units, then [T] holds  afterwards
Initialization : it is always the case that initially [R] holds
Persistence: it is always the case that if [R] holds, then it holds persistently
Toggle1: it is always the case that if [R] holds then [S] toggles [T]
Toggle2: it is always the case that if [R] holds then [S] toggles [T] at most [U] time units later
BndEntryConditionPattern: it is always the case that after [R] holds for at least [S]  time units, then [T] holds
ResponseChain2-1: it is always the case that if [R] holds and is succeeded by [S], then [T] eventually holds after [S]
Existence: [R] eventually holds

Write only the following as an answer and replace only the TODOs. Do not add anything else. Use only the given patterns, if it is not possible to use them just write Terminate:
Output Human readable: TODO
Output for the server: {'scope': TODO, 'pattern': TODO, 'expression_mapping': {'P': TODO, 'Q': TODO, 'R': TODO, 'S': TODO, 'T': TODO, 'U': TODO, 'V': TODO}}
"""


def create_prompt(req_formal, req_ai) -> (str, str):
    input_ai_formalization = req_ai.to_dict()["desc"]
    input_human_formalization = req_formal.to_dict()["desc"]
    human_readable_human_formalization = req_formal.to_dict()["formal"]
    db_human_formalization = req_formal.get_formalizations_json()

    prompt = (
        f""" input: {input_human_formalization}
    Output Human readable: {human_readable_human_formalization}
    Output for the server: {db_human_formalization}
    Formalize this input: {input_ai_formalization}"""
        + prompt_suffix
    )

    return "prompt_created", prompt


def parse_ai_response(ai_response) -> (str, dict):
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
            return "response_parsed", formalized_output
    except Exception as e:
        logging.warning(f"Could not parse AI-response: {e}")
    return "error_parsing", None
