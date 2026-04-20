from flask import Blueprint

example_ai_addon_blueprint = Blueprint(
    "ai_addons_example_ai_addon",
    __name__,
    url_prefix="/ai_addons/example_ai_addon_blueprint",
)
