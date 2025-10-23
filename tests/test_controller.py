import unittest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage

from tests.base_test_case import BaseTestCase
from controller import Controller


class TestController(BaseTestCase):
    target_class = Controller
    _setup_args = []  # Controller uses default agent_folder
    public_methods = ["stream", "invoke"]
    public_properties = [
        "agent_name",
        "agent_folder",
        "base_path",
        "agent_path",
        "system_prompt_path",
        "knowledge_directory",
        "system_prompt",
        "model",
        "extra_files",
        "temperature",
    ]

    def test_model_is_initialized(self):
        model = self.obj.model
        self.assertIsNotNone(model)

    def test_agent_name_property(self):
        """Test that agent_name property works correctly."""
        controller = Controller()
        controller.agent_name = "TestBot"
        self.assertEqual(controller.agent_name, "TestBot")

    def test_invoke_returns_message(self):
        result = self.obj.model.invoke("Hello, world!")
        self.assertIsNotNone(result)

    def test_invoke_method_calls_invoke_on_model(self):
        # Test that the model returns an AIMessage when invoked
        response = self.obj.model.invoke("Hello, world!")
        self.assertIsInstance(response, AIMessage)
        # Verify the response has content (actual content will vary)
        self.assertIsNotNone(response.content)
        self.assertIsInstance(response.content, str)
        self.assertGreater(len(response.content), 0)


if __name__ == "__main__":
    unittest.main()
