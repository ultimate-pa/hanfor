import importlib
import inspect
import os
import unittest

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass


class TestAiAddonStructure(unittest.TestCase):

    def setUp(self):
        self.here = os.path.dirname(os.path.realpath(__file__))
        self.addon_root = os.path.abspath(os.path.join(self.here, "..", "ai_addons"))
        self.excluded_dirs = {"core_ui", "__pycache__"}

    def test_all_addons_follow_structure(self):

        for addon_name in os.listdir(self.addon_root):

            addon_dir = os.path.join(self.addon_root, addon_name)

            if not os.path.isdir(addon_dir):
                continue

            if addon_name in self.excluded_dirs:
                continue

            with self.subTest(addon=addon_name):

                # -------------------------------------------------
                # Check addon class exists
                # -------------------------------------------------
                module_name = f"ai_addons.{addon_name}.{addon_name}"

                try:
                    module = importlib.import_module(module_name)
                except ModuleNotFoundError:
                    self.fail(f"{addon_name}: missing module {module_name}")

                addon_classes = [
                    cls
                    for _, cls in inspect.getmembers(module, inspect.isclass)
                    if issubclass(cls, AiAddonAbstractClass) and cls is not AiAddonAbstractClass
                ]

                self.assertTrue(
                    addon_classes,
                    f"{addon_name}: no AiAddonAbstractClass implementation found",
                )

                # -------------------------------------------------
                # Optional frontend checks
                # -------------------------------------------------
                def build_dummy_dependencies(cls):
                    return {dep: object() for dep in getattr(cls, "required_dependencies", [])}

                instance = addon_classes[0](enabled=False, **build_dummy_dependencies(addon_classes[0]))

                normalized_name = instance.normalize_addon_name()

                # static check
                static_dir = os.path.join(addon_dir, "static")
                if os.path.isdir(static_dir):
                    js_file = os.path.join(static_dir, f"{normalized_name}.js")
                    self.assertTrue(
                        os.path.exists(js_file),
                        f"{addon_name}: missing {normalized_name}.js",
                    )

                # template check
                templates_dir = os.path.join(addon_dir, "templates", "ai_addons")
                if os.path.isdir(templates_dir):
                    html_file = os.path.join(templates_dir, f"{normalized_name}.html")
                    self.assertTrue(
                        os.path.exists(html_file),
                        f"{addon_name}: missing {normalized_name}.html template",
                    )
