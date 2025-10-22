from typing import List
from contextlib import contextmanager
from app import App
import unittest
import time
from io import StringIO
from unittest.mock import patch
from langchain_core.messages import AIMessage

from tests.base_test_case import BaseTestCase


@contextmanager
def mock_workflow_stream(app, content="test", capture_output=False):
    def mock_stream(*args, **kwargs):
        yield AIMessage(content=content)

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        with patch.object(
            app.controller.workflow_manager, "stream", side_effect=mock_stream
        ):
            if capture_output:
                yield mock_stdout
            else:
                yield


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
        "controller",
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
        with mock_workflow_stream(self.obj):
            self.obj.run()
            time.sleep(0.1)  # Give thread time to start
            self.assertTrue(self.obj.is_running)

    def test_is_not_running(self):
        self.assertFalse(self.obj.is_running)
        with mock_workflow_stream(self.obj):
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
        app = AppWrapper(user_input=["quit"])
        with mock_workflow_stream(app):
            app.run()
            # Wait for the thread to finish processing
            if app._run_thread and app._run_thread.is_alive():
                app._run_thread.join(timeout=2.0)
        self.assertFalse(app.is_running)

    def test_response(self):
        """Test that bot responses are printed in 'Bot: message' format."""
        app = AppWrapper(user_input=["Hello", "quit"])
        with mock_workflow_stream(
            app, content="Hi there!", capture_output=True
        ) as mock_stdout:
            app.run()
            time.sleep(0.2)  # Give thread time to process
            # Ensure thread finishes BEFORE StringIO context exits
            if app._run_thread and app._run_thread.is_alive():
                app._run_thread.join(timeout=1.0)

            output = mock_stdout.getvalue()
        self.assertIn("Bot:", output, "Expected 'Bot:' prefix in output")


if __name__ == "__main__":
    unittest.main()
