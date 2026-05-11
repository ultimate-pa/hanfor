################################################################################
#                                 AI API config                                #
################################################################################

AI_PROVIDERS = {
    "PROVIDER_NAME": {
        "maximum_concurrent_api_requests": 0,
        "url": "PROVIDER_API_URL",
        "api_key": "PROVIDER_API_KEY",
        "api_methods_names": ["API_METHOD_NAME"],  # standard_ai_api will always be provided. No need to add here
        "default_model": "MODEL_NAME",
        "models": {
            "MODEL_NAME": "MODEL_DESCRIPTION",
        },
    },
}

DEFAULT_PROVIDER = "PROVIDER_NAME"

################################################################################
#                                AI ADDON config                               #
################################################################################

ADDON_EXAMPLE_AI_ADDON = False

ADDON_PATTERN_PREDICTION = False
