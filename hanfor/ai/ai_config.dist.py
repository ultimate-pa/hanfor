################################################################################
#                                 AI API config                                #
################################################################################

# Url, for example Ollama as in  http://some.ollama.org/api/generate
AI_API_URL = "API_URL"
AI_MODEL_NAMES = {
    "llama3.1:70b": "Existent",
}


################################################################################
#                           Standard Methods / Model                           #
################################################################################


STANDARD_SIMILARITY_METHOD = "Cosine Similarity"
STANDARD_AI_PROMPT_PARSE_METHOD = "Small Prompt"
STANDARD_AI_MODEL = "llama3.1:70b"


################################################################################
#                           AI Configuration Settings                          #
################################################################################

MAX_THREADS = 10
MAX_CONCURRENT_AI_REQUESTS = 2
MAX_AI_FORMALIZATION_TRYS = 5
DELETION_TIME_AFTER_COMPLETION_FORMALIZATION = 20  # Seconds
ENABLE_SIMILARITY_ON_STARTUP = True

# switches on interface:
AUTO_UPDATE_ON_REQUIREMENT_CHANGE = True
ENABLE_API_AI_REQUESTS = True
