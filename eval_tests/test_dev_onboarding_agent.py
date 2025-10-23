import pytest
from dotenv import load_dotenv
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT, CONCISENESS_PROMPT
from controller import Controller
from langsmith import testing as t

load_dotenv()


correctness_evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    feedback_key="correctness",
    model="ollama:llama3.2",
)

conciseness_evaluator = create_llm_as_judge(
    prompt=CONCISENESS_PROMPT,
    feedback_key="conciseness",
    model="ollama:llama3.2",
)

EVAL_DATASET = [
    {
        "prompt": "How do I run tests?",
        "reference_output": "To run tests, use pytest. You can run all tests with 'pytest' or specific test files with 'pytest path/to/test_file.py'. Use 'pytest -v' for verbose output.",
    },
    {
        "prompt": "How do I deploy the application?",
        "reference_output": "Follow the deployment guide which includes: 1) Build the application, 2) Configure environment variables, 3) Deploy to the target environment (staging/production), 4) Verify the deployment with health checks.",
    },
    {
        "prompt": "How do I set up my local development environment?",
        "reference_output": "Install Python dependencies using 'pip install -r requirements.txt', set up environment variables in .env file, install any system dependencies, and configure your IDE with the project settings.",
    },
    {
        "prompt": "What are the coding standards I should follow?",
        "reference_output": "Follow PEP 8 style guidelines for Python code. Use meaningful variable names, write docstrings for functions and classes, keep functions small and focused, and ensure code is properly tested before committing.",
    },
]


def run_test_case(test_case: dict):
    inputs = test_case["prompt"]
    reference_outputs = test_case["reference_output"]

    controller = Controller(agent_folder="dev_onboarding")
    result = controller.workflow_manager.invoke(inputs)
    outputs = result["messages"][-1].content

    t.log_inputs({"question": inputs})
    t.log_outputs({"answer": outputs})
    t.log_reference_outputs({"answer": reference_outputs})

    correctness_result = correctness_evaluator(
        inputs=inputs, outputs=outputs, reference_outputs=reference_outputs
    )

    conciseness_result = conciseness_evaluator(
        inputs=inputs, outputs=outputs, reference_outputs=reference_outputs
    )

    print(f"\n✓ Test completed: {inputs}")
    print(f"Response: {outputs[:200]}...")
    print(f"Correctness: {correctness_result}")
    print(f"Conciseness: {conciseness_result}")


@pytest.mark.langsmith
def test_run_tests_question():
    run_test_case(EVAL_DATASET[0])


@pytest.mark.langsmith
def test_deployment_question():
    run_test_case(EVAL_DATASET[1])


@pytest.mark.langsmith
def test_setup_environment_question():
    run_test_case(EVAL_DATASET[2])


@pytest.mark.langsmith
def test_coding_standards_question():
    run_test_case(EVAL_DATASET[3])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
