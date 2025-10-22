import unittest
import json
from controller import Controller


class TestAgentEvaluation(unittest.TestCase):
    # Eval dataset: question, expected_keywords, criteria
    EVAL_DATASET = [
        {
            "prompt": "How do I run tests?",
            "expected_keywords": ["pytest"],
            "criteria": "The response must mention 'pytest' and provide actionable steps for running tests.",
        },
        {
            "prompt": "How do I deploy the application?",
            "expected_keywords": ["deploy"],
            "criteria": "The response provides deployment-related information such as steps, commands, or processes.",
        },
        {
            "prompt": "How do I set up my local development environment?",
            "expected_keywords": ["install", "requirements", "dependencies"],
            "criteria": "The response must provide concrete setup steps including dependency installation.",
        },
        {
            "prompt": "What are the coding standards I should follow?",
            "expected_keywords": ["code", "standard", "style"],
            "criteria": "The response must reference coding standards or style guidelines for the project.",
        },
    ]

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
        print("Response: ", response[:200], "...\n")
        return response

    def assert_response_true(
        self, prompt: str, response: str, criteria: str
    ) -> tuple[bool, str]:
        passed, reason = self._evaluate_response(prompt, response, criteria)
        print(f"\n{'✓' if passed else '✗'} Evaluation Result:")
        print(f"Assessment: {reason}\n")
        self.assertTrue(passed, f"Evaluation failed: {reason}")

    def test_eval_dataset(self):
        """Run the full eval dataset and report results."""
        results = []

        print("\n" + "=" * 80)
        print("RUNNING EVALUATION DATASET")
        print("=" * 80)

        for i, test_case in enumerate(self.EVAL_DATASET, 1):
            print(f"\n[Test {i}/{len(self.EVAL_DATASET)}] {test_case['prompt']}")
            print("-" * 80)

            response = self._get_response(test_case["prompt"])

            # Check expected keywords
            keywords_found = [
                kw
                for kw in test_case["expected_keywords"]
                if kw.lower() in response.lower()
            ]
            keywords_pass = len(keywords_found) > 0

            # LLM evaluation
            llm_pass, llm_reason = self._evaluate_response(
                test_case["prompt"], response, test_case["criteria"]
            )

            # Overall pass/fail
            test_passed = keywords_pass and llm_pass

            results.append(
                {
                    "prompt": test_case["prompt"],
                    "passed": test_passed,
                    "keywords_found": keywords_found,
                    "llm_evaluation": llm_reason,
                }
            )

            print(
                f"{'✓' if keywords_pass else '✗'} Keywords: {keywords_found if keywords_found else 'None found'}"
            )
            print(f"{'✓' if llm_pass else '✗'} LLM Evaluation: {llm_reason}")
            print(f"{'✓ PASS' if test_passed else '✗ FAIL'} Overall Result\n")

        # Summary
        passed_count = sum(1 for r in results if r["passed"])
        print("\n" + "=" * 80)
        print(f"EVALUATION SUMMARY: {passed_count}/{len(results)} tests passed")
        print("=" * 80 + "\n")

        # Assert all passed
        failed_tests = [r for r in results if not r["passed"]]
        if failed_tests:
            failure_msg = "\n".join(
                [f"- {t['prompt']}: {t['llm_evaluation']}" for t in failed_tests]
            )
            self.fail(f"{len(failed_tests)} test(s) failed:\n{failure_msg}")


if __name__ == "__main__":
    unittest.main()
