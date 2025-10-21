import unittest

from tests.base_test_case import BaseTestCase
from workflow_manager import WorkflowManager


class TestWorkflowManager(BaseTestCase):
    public_methods = ["invoke"]

    def __init__(self, *args, **kwargs):
        self.target_class = WorkflowManager
        self._setup_args = []
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    unittest.main()
