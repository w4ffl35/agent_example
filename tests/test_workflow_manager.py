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
    ]
    public_properties = [
        "workflow",
        "memory",
        "messages",
        "compiled_workflow",
        "prompt_template",
        "config",
        "tool_node",
        "agent_has_tools",
    ]

    def __init__(self, *args, **kwargs):
        self.target_class = WorkflowManager
        self._setup_args = []
        super().__init__(*args, **kwargs)

    def test_workflow_type(self):
        self.assertIsInstance(self.obj.workflow, StateGraph)

    def test_memory_type(self):
        self.assertIsInstance(self.obj.memory, MemorySaver)

    def test_messages_type(self):
        messages = self.obj.messages
        self.assertIsInstance(messages, list)
        message = messages[0]
        self.assertIsInstance(message, tuple)
        self.assertEqual(len(message), 2)
        self.assertIsInstance(message[0], str)
        self.assertIsInstance(message[1], str)

        message = messages[1]
        self.assertEqual(message.__class__.__name__, "MessagesPlaceholder")
        self.assertEqual(message.variable_name, "messages")

    def test_invoke_return_type(self):
        mock_response = {"messages": [HumanMessage(content="Hello")]}
        with patch.object(
            self.obj.compiled_workflow, "invoke", return_value=mock_response
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
            self.obj.compiled_workflow, "invoke", return_value=mock_response
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

    def test_prompt_template_type(self):
        prompt_template = self.obj.prompt_template
        self.assertEqual(prompt_template.__class__.__name__, "ChatPromptTemplate")


if __name__ == "__main__":
    unittest.main()
