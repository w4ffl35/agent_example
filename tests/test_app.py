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

    def get_user_input(self) -> str:
        user_input = self._user_input[self._input_index]
        self._input_index = min(self._input_index + 1, len(self._user_input) - 1)
        return user_input


class TestApp(BaseTestCase):
    target_class = AppWrapper
    _setup_args = [[""]]  # AppWrapper expects user_input list
    public_methods = [
        "run",
        "get_user_input",
        "quit"
    ]
    public_properties = [
        "is_running",
        "workflow_manager",
        "agent",
        "agent_name",
        "system_prompt_path",
        "system_prompt",
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
        # Mock workflow to prevent real execution and suppress output
        mock_response = {"messages": [HumanMessage(content="test")]}
        with patch("sys.stdout", new_callable=StringIO):  # Suppress print output
            with patch.object(
                self.obj.workflow_manager, "invoke", return_value=mock_response
            ):
                self.obj.run()
                time.sleep(0.1)  # Give thread time to start
                self.assertTrue(self.obj.is_running)

    def test_is_not_running(self):
        self.assertFalse(self.obj.is_running)
        # Mock workflow to prevent real execution and suppress output
        mock_response = {"messages": [HumanMessage(content="test")]}
        with patch("sys.stdout", new_callable=StringIO):  # Suppress print output
            with patch.object(
                self.obj.workflow_manager, "invoke", return_value=mock_response
            ):
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
            # Mock workflow to prevent real execution and suppress output
            mock_response = {"messages": [HumanMessage(content="test")]}
            with patch("sys.stdout", new_callable=StringIO):  # Suppress print output
                with patch.object(
                    app.workflow_manager, "invoke", return_value=mock_response
                ):
                    app.run()
                    time.sleep(0.2)
                    # Ensure thread finishes
                    if app._run_thread and app._run_thread.is_alive():
                        app._run_thread.join(timeout=1.0)
            self.assertFalse(app.is_running)

    def test_response(self):
        """Test that bot responses are printed in 'Bot: message' format."""
        mock_workflow_response = {
            "messages": [HumanMessage(content="Hello"), AIMessage(content="Hi there!")]
        }

        app = AppWrapper(user_input=["Hello", "quit"])
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # Mock the workflow_manager.invoke to avoid real LangGraph execution
            with patch.object(
                app.workflow_manager, "invoke", return_value=mock_workflow_response
            ):
                app.run()
                time.sleep(0.2)  # Give thread time to process
                # Ensure thread finishes BEFORE StringIO context exits
                if app._run_thread and app._run_thread.is_alive():
                    app._run_thread.join(timeout=1.0)

            output = mock_stdout.getvalue()

        self.assertIn("Bot:", output, "Expected 'Bot:' prefix in output")


if __name__ == "__main__":
    unittest.main()
