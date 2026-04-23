from .ai_core_addon_api import blueprint
from .example_ai_addon_api import example_ai_addon_blueprint, example_ai_addon_api_namespace
from .threading_api import threading_blueprint, threading_api_namespace
from .pattern_prediction_api import pattern_blueprint
from .ai_api import ai_blueprint

all_threading_ai_addon_blueprints = [
    (blueprint, None),
    (ai_blueprint, None),
    (threading_blueprint, threading_api_namespace),
    (pattern_blueprint, None),
    (example_ai_addon_blueprint, example_ai_addon_api_namespace),
]
