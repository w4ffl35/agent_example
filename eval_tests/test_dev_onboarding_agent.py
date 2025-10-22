import unittest
import json
from controller import Controller


class TestAgentEvaluation(unittest.TestCase):
    def setUp(self):
        self.controller = Controller(agent_folder="dev_onboarding")
        self.evaluator = Controller(
            agent_folder="eval_agent", temperature=0.1, tools=[]
        )

    def tearDown(self):
        del self.controller

    def _evaluate_response(
        self, prompt: str, response: str, criteria: str
    ) -> tuple[bool, str]:
        """Use LLM evaluator to assess if response meets criteria."""
        eval_prompt = f"""Evaluate this response against the criteria.

User Question: {prompt}

Agent Response: {response}

Evaluation Criteria: {criteria}

Carefully check if the agent response meets the evaluation criteria.
If the response satisfies the criteria, return PASS even if it also provides
additional helpful context or suggestions. Extra information is acceptable so
long as it does not contradict the criteria. Only return FAIL when the response
is missing required elements, is incorrect, or directly violates the criteria.
Respond with JSON only in this exact format:
{{"result": "PASS", "reason": "explanation"}} or {{"result": "FAIL", "reason": "explanation"}}
"""
        result = self.evaluator.invoke(eval_prompt)
        eval_output = result["messages"][-1].content

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in eval_output:
            eval_output = eval_output.split("```json")[1].split("```")[0].strip()
        elif "```" in eval_output:
            eval_output = eval_output.split("```")[1].split("```")[0].strip()

        eval_result = json.loads(eval_output)
        passed = eval_result["result"] == "PASS"
        reason = eval_result["reason"]

        return passed, reason

    def _get_response(self, prompt: str) -> str:
        result = self.controller.invoke(prompt)
        response = result["messages"][-1].content
        return response

    def assert_response_true(
        self, prompt: str, response: str, criteria: str
    ) -> tuple[bool, str]:
        passed, reason = self._evaluate_response(prompt, response, criteria)
        print(f"\n{'✓' if passed else '✗'} Evaluation Result:")
        print(f"Assessment: {reason}\n")
        self.assertTrue(passed, f"Evaluation failed: {reason}")

    def test_workflow_knowledge(self):
        """Test that the agent can answer questions about running tests."""
        prompt = "How do I run tests?"
        response = self._get_response(prompt)

        print("Response: ", response[:200], "...\n")

        self.assertIn(
            "pytest",
            response.lower(),
            "Response must mention 'pytest' testing framework",
        )

        self.assert_response_true(
            prompt,
            response,
            "The response mentions `pytest`",
        )

        self.assert_response_true(
            prompt,
            response,
            "The response provides actionable information about how to run tests (e.g., mentions commands or steps to execute tests).",
        )


if __name__ == "__main__":
    unittest.main()
