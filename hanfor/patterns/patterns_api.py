from flask_restx import Namespace, Resource
from flask import current_app
from hanfor_flask import nocache
from lib_core.api_models import PatternsResponseModel
from lib_core.pattern.patterns_basic import APattern

patterns_ns = Namespace("Patterns", path="/patterns")


@patterns_ns.route("")
class ApiPatterns(Resource):
    @patterns_ns.doc(description="Returns all patterns grouped by category, with group ordering and scope options.")
    @patterns_ns.response(200, "Success", PatternsResponseModel)
    @nocache
    def get(self):
        frontend = APattern.to_frontent_dict()
        groups = {}
        for name, data in frontend.items():
            try:
                pattern = APattern().get_pattern(name)
            except KeyError:
                continue
            group = pattern.group
            if group not in groups:
                groups[group] = []
            groups[group].append(
                {
                    "name": name,
                    "text": pattern._pattern_text,
                    "env": data["env"],
                }
            )

        group_order = current_app.config.get("PATTERNS_GROUP_ORDER", [])
        ordered_groups = {}
        for g in group_order:
            if g in groups:
                ordered_groups[g] = groups[g]
        for g in groups:
            if g not in ordered_groups:
                ordered_groups[g] = groups[g]

        return {
            "groups": ordered_groups,
            "group_order": [g for g in group_order if g in groups]
            + [g for g in groups if g not in group_order],
            "scopes": [
                {"value": "NONE", "label": "None"},
                {"value": "GLOBALLY", "label": "Globally"},
                {"value": "BEFORE", "label": 'Before "{P}"'},
                {"value": "AFTER", "label": 'After "{P}"'},
                {"value": "BETWEEN", "label": 'Between "{P}" and "{Q}"'},
                {"value": "AFTER_UNTIL", "label": 'After "{P}" until "{Q}"'},
            ],
        }
