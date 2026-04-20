from .ai_core_addon_api import blueprint
from .example_ai_addon_api import example_ai_addon_blueprint
from .threading_api import threading_blueprint
from .pattern_prediction_api import pattern_blueprint
from .ai_api import ai_blueprint

all_threading_ai_addon_blueprints = [
    blueprint,
    ai_blueprint,
    threading_blueprint,
    pattern_blueprint,
    example_ai_addon_blueprint,
]
