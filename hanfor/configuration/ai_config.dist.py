################################################################################
#                                 AI API config                                #
################################################################################

AI_PROVIDERS = {
    "PROVIDER_NAME": {
        "maximum_concurrent_api_requests": 0,
        "url": "PROVIDER_API_URL",
        "api_key": "PROVIDER_API_KEY",
        "default_model": "MODEL_NAME",
        "models": {
            "MODEL_NAME": "MODEL_DESCRIPTION",
        },
    },
}

DEFAULT_PROVIDER = "PROVIDER_NAME"
