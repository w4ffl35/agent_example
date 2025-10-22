import unittest
from unittest.mock import patch
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from tests.base_test_case import BaseTestCase
from workflow_manager import WorkflowManager


class TestWorkflowManager(BaseTestCase):
    public_methods = [
        "invoke",
        "stream",
        "clear_memory",
    ]
    public_properties = []

    def __init__(self, *args, **kwargs):
        self.target_class = WorkflowManager
        self._setup_args = []
        super().__init__(*args, **kwargs)

    def test_invoke_return_type(self):
        mock_response = {"messages": [HumanMessage(content="Hello")]}
        with patch.object(
            self.obj._compiled_workflow, "invoke", return_value=mock_response
        ):
            result = self.obj.invoke("Hello")
        self.assertIsInstance(result, dict)

    def test_invoke_return_structure(self):
        mock_response = {
            "messages": [
                HumanMessage(content="Hello, how are you?"),
                AIMessage(content="I'm doing well, thank you!"),
            ]
        }

        with patch.object(
            self.obj._compiled_workflow, "invoke", return_value=mock_response
        ):
            result = self.obj.invoke("Hello, how are you?")

        self.assertIsInstance(result, dict, "invoke() should return a dictionary")
        self.assertIn("messages", result, "Return dict should contain 'messages' key")

        messages = result["messages"]
        self.assertIsInstance(messages, list, "'messages' should be a list")

        self.assertGreater(len(messages), 0, "'messages' list should not be empty")

        for msg in messages:
            self.assertTrue(
                hasattr(msg, "content"),
                f"Message object should have 'content' attribute, got {type(msg).__name__}",
            )

        first_message = messages[0]
        self.assertEqual(
            first_message.__class__.__name__,
            "HumanMessage",
            "First message should be a HumanMessage",
        )
        self.assertEqual(
            first_message.content,
            "Hello, how are you?",
            "HumanMessage content should match input",
        )


if __name__ == "__main__":
    unittest.main()
