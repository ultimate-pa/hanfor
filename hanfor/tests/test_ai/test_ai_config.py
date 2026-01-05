from unittest import TestCase
import ai.ai_config as config
from ai.ai_utils import load_similarity_methods
from ai.interfaces.ai_interface import load_ai_prompt_parse_methods


class TestAiConfig(TestCase):
    def test_ai_config_values(self):
        """
        Test to verify that all configuration values are present and have the correct type.
        """
        # Test for AI_API_URL
        self.assertTrue(hasattr(config, "AI_API_URL"), "AI_API_URL is missing.")
        self.assertIsInstance(config.AI_API_URL, str, "AI_API_URL should be a string.")
        self.assertTrue(bool(config.AI_API_URL.strip()), "AI_API_URL should not be empty.")

        # Test for AI_MODEL_NAMES
        self.assertTrue(hasattr(config, "AI_MODEL_NAMES"), "AI_MODEL_NAMES is missing.")
        self.assertIsInstance(config.AI_MODEL_NAMES, dict, "AI_MODEL_NAMES should be a dictionary.")
        self.assertTrue(config.AI_MODEL_NAMES, "AI_MODEL_NAMES should contain at least one model.")
        for model, description in config.AI_MODEL_NAMES.items():
            self.assertIsInstance(model, str, f"Model name '{model}' should be a string.")
            self.assertIsInstance(description, str, f"Description for '{model}' should be a string.")

        # Test for STANDARD_SIMILARITY_METHOD
        self.assertTrue(hasattr(config, "STANDARD_SIMILARITY_METHOD"), "STANDARD_SIMILARITY_METHOD is missing.")
        self.assertIsInstance(config.STANDARD_SIMILARITY_METHOD, str, "STANDARD_SIMILARITY_METHOD should be a string.")
        similarity_methods = load_similarity_methods()
        self.assertIsInstance(similarity_methods, dict, "load_similarity_methods should return a dictionary.")
        self.assertTrue(
            config.STANDARD_SIMILARITY_METHOD in similarity_methods.keys(),
            f"STANDARD_SIMILARITY_METHOD: [{config.STANDARD_SIMILARITY_METHOD}] not in strategies: {similarity_methods.keys()}.",
        )

        # Test for STANDARD_AI_PROMPT_PARSE_METHOD
        self.assertTrue(
            hasattr(config, "STANDARD_AI_PROMPT_PARSE_METHOD"), "STANDARD_AI_PROMPT_PARSE_METHOD is missing."
        )
        self.assertIsInstance(
            config.STANDARD_AI_PROMPT_PARSE_METHOD, str, "STANDARD_AI_PROMPT_PARSE_METHOD should be a string."
        )
        ai_methods = load_ai_prompt_parse_methods()
        self.assertIsInstance(ai_methods, dict, "load_similarity_methods should return a dictionary.")
        self.assertTrue(
            config.STANDARD_AI_PROMPT_PARSE_METHOD in ai_methods.keys(),
            f"STANDARD_AI_PROMPT_PARSE_METHOD: [{config.STANDARD_AI_PROMPT_PARSE_METHOD}] not in strategies: {ai_methods.keys()}.",
        )

        # Test for STANDARD_AI_MODEL
        self.assertTrue(hasattr(config, "STANDARD_AI_MODEL"), "STANDARD_AI_MODEL is missing.")
        self.assertIsInstance(config.STANDARD_AI_MODEL, str, "STANDARD_AI_MODEL should be a string.")
        self.assertIn(
            config.STANDARD_AI_MODEL, config.AI_MODEL_NAMES, "STANDARD_AI_MODEL should be a key in AI_MODEL_NAMES."
        )

        # Test for MAX_CONCURRENT_AI_REQUESTS
        self.assertTrue(hasattr(config, "MAX_CONCURRENT_AI_REQUESTS"), "MAX_CONCURRENT_AI_REQUESTS is missing.")
        self.assertTrue(config.MAX_CONCURRENT_AI_REQUESTS > 0, "MAX_AI_FORMALIZATION_TRYS should be [int] > 0.")

        # Test for MAX_AI_FORMALIZATION_TRYS
        self.assertTrue(hasattr(config, "MAX_AI_FORMALIZATION_TRYS"), "MAX_AI_FORMALIZATION_TRYS is missing.")
        self.assertTrue(config.MAX_AI_FORMALIZATION_TRYS > 0, "MAX_AI_FORMALIZATION_TRYS should be [int] > 0.")

        # Test for ENABLE_SIMILARITY_ON_STARTUP
        self.assertTrue(hasattr(config, "ENABLE_SIMILARITY_ON_STARTUP"), "ENABLE_SIMILARITY_ON_STARTUP is missing.")
        self.assertIsInstance(
            config.ENABLE_SIMILARITY_ON_STARTUP, bool, "ENABLE_SIMILARITY_ON_STARTUP should be a boolean."
        )

        # Test for AUTO_UPDATE_ON_REQUIREMENT_CHANGE
        self.assertTrue(
            hasattr(config, "AUTO_UPDATE_ON_REQUIREMENT_CHANGE"), "AUTO_UPDATE_ON_REQUIREMENT_CHANGE is missing."
        )
        self.assertIsInstance(
            config.AUTO_UPDATE_ON_REQUIREMENT_CHANGE, bool, "AUTO_UPDATE_ON_REQUIREMENT_CHANGE should be a boolean."
        )

        # Test for ENABLE_API_AI_REQUESTS
        self.assertTrue(hasattr(config, "ENABLE_API_AI_REQUESTS"), "ENABLE_API_AI_REQUESTS is missing.")
        self.assertIsInstance(config.ENABLE_API_AI_REQUESTS, bool, "ENABLE_API_AI_REQUESTS should be a boolean.")
