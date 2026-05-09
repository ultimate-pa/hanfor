import os
import importlib
from flask import Blueprint
from flask_restx import Namespace

threading_namespace_and_blueprint = []
ai_namespace_and_blueprint = ()
all_ai_addon_namespaces_and_blueprints = []
addons_base = os.path.abspath(os.path.join(str(os.path.dirname(__file__)), ".."))

for addon_dir in os.listdir(addons_base):
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
                if filename.startswith("threading") or filename.startswith("ai_core"):
                    threading_namespace_and_blueprint.append((blueprint, namespace))
                elif filename.startswith("ai"):
                    ai_namespace_and_blueprint = (blueprint, namespace)
                else:
                    all_ai_addon_namespaces_and_blueprints.append((blueprint, namespace))
