from typing import List
from app import App
import unittest
import time
from io import StringIO
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage

from tests.base_test_case import BaseTestCase


class AppWrapper(App):
    def __init__(self, user_input: List[str]):
        super().__init__()
        self._user_input = user_input
        self._input_index = 0
        # Initialize _model to avoid AttributeError
        self._model = None

    def get_user_input(self) -> str:
        user_input = self._user_input[self._input_index]
        self._input_index = min(self._input_index + 1, len(self._user_input) - 1)
        return user_input


class TestApp(BaseTestCase):
    target_class = AppWrapper
    _setup_args = [[""]]  # AppWrapper expects user_input list
    public_methods = ["run", "get_user_input", "quit"]
    public_properties = [
        "is_running",
        "config",
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
    ]

    def tearDown(self):
        # Suppress any output during teardown
        with patch("sys.stdout", new_callable=StringIO):
            # Ensure the app is stopped and thread is joined before cleanup
            if self.obj.is_running:
                self.obj.quit()
            # Wait for thread to finish if it was started
            if (
                hasattr(self.obj, "_run_thread")
                and self.obj._run_thread
                and self.obj._run_thread.is_alive()
            ):
                self.obj._run_thread.join(timeout=1.0)
        super().tearDown()

    def test_is_running(self):
        # Mock agent stream to prevent real execution and suppress output
        def mock_stream(*args, **kwargs):
            yield (AIMessage(content="test"), {})

        with patch("sys.stdout", new_callable=StringIO):  # Suppress print output
            with patch.object(self.obj.agent, "stream", side_effect=mock_stream):
                self.obj.run()
                time.sleep(0.1)  # Give thread time to start
                self.assertTrue(self.obj.is_running)

    def test_is_not_running(self):
        self.assertFalse(self.obj.is_running)

        # Mock agent stream to prevent real execution and suppress output
        def mock_stream(*args, **kwargs):
            yield (AIMessage(content="test"), {})

        with patch("sys.stdout", new_callable=StringIO):  # Suppress print output
            with patch.object(self.obj.agent, "stream", side_effect=mock_stream):
                self.obj.run()
                time.sleep(0.1)  # Give thread time to start
                self.assertTrue(self.obj.is_running)
                self.obj.quit()
                time.sleep(0.1)  # Give thread time to stop
                self.assertFalse(self.obj.is_running)

    def test_get_user_input(self):
        user_input = self.obj.get_user_input()
        self.assertIsInstance(user_input, str)

    def test_user_can_quit(self):
        quit_commands = ["quit", "exit"]
        for command in quit_commands:
            app = AppWrapper(user_input=[command])

            # Mock agent stream to prevent real execution and suppress output
            def mock_stream(*args, **kwargs):
                yield (AIMessage(content="test"), {})

            with patch("sys.stdout", new_callable=StringIO):  # Suppress print output
                with patch.object(app.agent, "stream", side_effect=mock_stream):
                    app.run()
                    time.sleep(0.2)
                    # Ensure thread finishes
                    if app._run_thread and app._run_thread.is_alive():
                        app._run_thread.join(timeout=1.0)
            self.assertFalse(app.is_running)

    def test_response(self):
        """Test that bot responses are printed in 'Bot: message' format."""
        app = AppWrapper(user_input=["Hello", "quit"])

        def mock_stream(*args, **kwargs):
            yield (AIMessage(content="Hi there!"), {})

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # Mock the agent.stream to avoid real LangGraph execution
            with patch.object(app.agent, "stream", side_effect=mock_stream):
                app.run()
                time.sleep(0.2)  # Give thread time to process
                # Ensure thread finishes BEFORE StringIO context exits
                if app._run_thread and app._run_thread.is_alive():
                    app._run_thread.join(timeout=1.0)

            output = mock_stdout.getvalue()

        self.assertIn("Bot:", output, "Expected 'Bot:' prefix in output")

    def test_model_is_initialized(self):
        """Test that the model property is initialized correctly."""
        model = self.obj.model
        self.assertIsNotNone(model)

    def test_agent_is_initialized(self):
        """Test that the agent property is initialized correctly."""

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
        app = AppWrapper(user_input=[""])
        app.agent_name = "TestBot"
        self.assertEqual(app.agent_name, "TestBot")


if __name__ == "__main__":
    unittest.main()
