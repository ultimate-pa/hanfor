from .ai_core_addon_api import core_ai_addon_blueprint, core_ai_addon_api_namespace
from .example_ai_addon_api import example_ai_addon_api_namespace
from .threading_api import threading_api_namespace
from .pattern_prediction_api import pattern_prediction_namespace
from .ai_api import ai_api_namespace

all_threading_ai_addon_blueprints = [
    (core_ai_addon_blueprint, core_ai_addon_api_namespace),
    (None, ai_api_namespace),
    (None, threading_api_namespace),
    (None, pattern_prediction_namespace),
    (None, example_ai_addon_api_namespace),
]
