import unittest
from langchain_core.messages import AIMessage

from tests.base_test_case import BaseTestCase
from controller import Controller


class TestController(BaseTestCase):
    target_class = Controller
    _setup_args = []  # Controller uses default agent_folder
    public_methods = ["stream", "invoke"]
    public_properties = [
        "agent",
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

    def test_agent_is_initialized(self):
        # Mock the model to avoid actually initializing Ollama
        class MockModel:
            def bind_tools(self, tools, **kwargs):
                return self

        class MockAgent:
            def invoke(self, state):
                return {"messages": [AIMessage(content="Mock response")]}

        self.obj._model = MockModel()
        self.obj._agent = MockAgent()

        agent = self.obj.agent
        self.assertIsNotNone(agent)

    def test_agent_name_property(self):
        """Test that agent_name property works correctly."""
        controller = Controller()
        controller.agent_name = "TestBot"
        self.assertEqual(controller.agent_name, "TestBot")


if __name__ == "__main__":
    unittest.main()
