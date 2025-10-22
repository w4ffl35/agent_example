import unittest
from controller import Controller


class TestAgentEvaluation(unittest.TestCase):
    def setUp(self):
        self.controller = Controller(agent_folder="dev_onboarding")

    def tearDown(self):
        del self.controller

    def test_testing_workflow_knowledge(self):
        result = self.controller.invoke("How do I run tests?")
        response = result["messages"][-1].content.lower()

        self.assertIn("pytest", response, "Response should mention pytest")

        print(f"\n✓ Test passed. Response preview:\n{response[:300]}...\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
