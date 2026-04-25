import os
import importlib
from flask import Blueprint
from flask_restx import Namespace

EXCLUDE_DIRS = {"__pycache__"}
all_threading_ai_addon_blueprints = []
addons_base = os.path.abspath(os.path.join(str(os.path.dirname(__file__)), ".."))

for addon_dir in os.listdir(addons_base):
    if addon_dir in EXCLUDE_DIRS:
        continue
    addon_path = os.path.join(addons_base, addon_dir)
    if not os.path.isdir(addon_path):
        continue

    for filename in os.listdir(addon_path):
        if filename.endswith("_api.py"):
            module_name = filename[:-3]
            module = importlib.import_module(f"ai_addons.{addon_dir}.{module_name}")

            namespaces = [
                getattr(module, attr)
                for attr in dir(module)
                if attr.endswith("_namespace") and isinstance(getattr(module, attr), Namespace)
            ]
            blueprints = [
                getattr(module, attr)
                for attr in dir(module)
                if attr.endswith("_blueprint") and isinstance(getattr(module, attr), Blueprint)
            ]

            blueprint = blueprints[0] if blueprints else None
            for namespace in namespaces:
                all_threading_ai_addon_blueprints.append((blueprint, namespace))
