from typing import List
from app import App
import unittest
import time


class AppWrapper(App):
    def __init__(self, user_input: List[str]):
        super().__init__()
        self._user_input = user_input
        self._input_index = 0

    def get_user_input(self) -> str:
        user_input = self._user_input[self._input_index]
        self._input_index = min(self._input_index + 1, len(self._user_input) - 1)
        return user_input


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = AppWrapper([""])

    def tearDown(self):
        self.app.quit()
        del self.app

    def test_instantiation(self):
        self.assertIsInstance(self.app, App)

    def test_has_public_methods(self):
        public_methods = [
            "run",
            "get_user_input",
            "quit",
        ]
        for method in public_methods:
            self.assertTrue(
                hasattr(self.app, method),
                f"App is missing public method: {method}",
            )
            self.assertTrue(
                callable(getattr(self.app, method, None)),
                f"App public method is not callable: {method}",
            )

    def test_has_public_properties(self):
        public_properties = [
            "is_running",
        ]
        for prop in public_properties:
            self.assertTrue(
                hasattr(self.app, prop),
                f"App is missing public property: {prop}",
            )

    def test_is_running(self):
        self.app.run()
        self.assertTrue(self.app.is_running)

    def test_is_not_running(self):
        self.assertFalse(self.app.is_running)
        self.app.run()
        self.assertTrue(self.app.is_running)
        self.app.quit()
        self.assertFalse(self.app.is_running)

    def test_get_user_input(self):
        user_input = self.app.get_user_input()
        self.assertIsInstance(user_input, str)

    def test_user_can_quit(self):
        quit_commands = ["quit", "exit"]
        for command in quit_commands:
            app = AppWrapper(user_input=[command])
            app.run()
            time.sleep(0.2)
            self.assertFalse(app.is_running)


if __name__ == "__main__":
    unittest.main()
