from typing import List
from app import App
import unittest
import time

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
        "quit",
    ]
    public_properties = [
        "is_running",
    ]

    def tearDown(self):
        self.obj.quit()
        super().tearDown()

    def test_is_running(self):
        self.obj.run()
        self.assertTrue(self.obj.is_running)

    def test_is_not_running(self):
        self.assertFalse(self.obj.is_running)
        self.obj.run()
        self.assertTrue(self.obj.is_running)
        self.obj.quit()
        self.assertFalse(self.obj.is_running)

    def test_get_user_input(self):
        user_input = self.obj.get_user_input()
        self.assertIsInstance(user_input, str)

    def test_user_can_quit(self):
        quit_commands = ["quit", "exit"]
        for command in quit_commands:
            app = AppWrapper(user_input=[command])
            app.run()
            time.sleep(0.2)
            self.assertFalse(app.is_running)

    def test_workflow_manager_invoke_is_called(self):
        pass


if __name__ == "__main__":
    unittest.main()
