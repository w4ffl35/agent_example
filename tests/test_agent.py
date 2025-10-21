import unittest

from tests.base_test_case import BaseTestCase
from agent import Agent
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.prompt_values import ChatPromptValue, PromptValue


class TestAgent(BaseTestCase):
    public_methods = [
        "invoke",
        "stream",
    ]
    public_properties = ["model", "system_prompt", "name"]

    def __init__(self, *args, **kwargs):
        self.target_class = Agent
        self._setup_args = []
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.prompt_value = ChatPromptValue(
            messages=[
                SystemMessage(content="You are an ai assistant."),
                HumanMessage(content="Hello"),
            ]
        )
        super().setUp()

        class MockModel:
            def invoke(self, prompt: PromptValue) -> AIMessage:
                return AIMessage(content="Mock response")

        self.obj._model = MockModel()

    def test_invoke_returns_message(self):
        result = self.obj.invoke(self.prompt_value)
        self.assertIsNotNone(result)

    def test_model_is_initialized(self):
        model = self.obj.model
        self.assertIsNotNone(model)

    def test_invoke_method_calls_invoke_on_model(self):
        response = self.obj.invoke(self.prompt_value)
        self.assertIsInstance(response, AIMessage)
        self.assertEqual(response.content, "Mock response")

    def test_name_propery(self):
        agent = Agent(name="foobar")
        self.assertEqual(agent.name, "foobar")


if __name__ == "__main__":
    unittest.main()
