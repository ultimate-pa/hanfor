################################################################################
#                                 AI API config                                #
################################################################################


AI_API_URL = "http://192.168.178.87:11434/api/generate"
AI_MODEL_NAMES = {
    "gemma3:12b": "An efficient 8B-parameter model for advanced text understanding and generation.",
    "llama3.1:13b": "NON-EXISTENT",
    "llama3.1:34b": "NON-EXISTENT",
}


################################################################################
#                           Standard Methods / Model                           #
################################################################################


STANDARD_SIMILARITY_METHOD = "Levenshtein"
STANDARD_AI_PROMPT_PARSE_METHOD = "Prompt without grammar"
STANDARD_AI_MODEL = "gemma3:12b"


################################################################################
#                           AI Configuration Settings                          #
################################################################################


MAX_CONCURRENT_AI_REQUESTS = 2
MAX_AI_FORMALIZATION_TRYS = 5
DELETION_TIME_AFTER_COMPLETION_FORMALIZATION = 20  # Seconds
ENABLE_SIMILARITY_ON_STARTUP = True

# switches on interface:
AUTO_UPDATE_ON_REQUIREMENT_CHANGE = True
ENABLE_API_AI_REQUESTS = True
