# LangChain Agent Example

This is a simple agent that uses LangChain and LangGraph to load an agent with RAG capabilities and a
command prompt interface. The agent runs locally using Llama3.2 via Ollama.

## Setup

During setup you will be asked for a LangChain API key. If you wish to see LangSmith traces, you will need to create an API key and have that prepared before running the setup script.

Setup script:
```bash
./bin/setup.sh
```

## Run the application

```bash
source venv/bin/activate
python main.py
```

You will be asked for a username and password.
For this example you must use "admin" as username and "password" as password.

---

Alternatively, manual setup instructions:

### Install Ollama and Run Llama3.2

1. `curl -fsSL https://ollama.com/install.sh | sh`
2. `ollama run llama3.2`

### Create Virtual Environment and Install Dependencies

1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`

## Running the Example

```bash
python main.py
```

To quit, type `quit` and press Enter.

## Run tests

Unit tests
```bash
python -m unittest discover -v tests
```

Eval tests
```bash
python -m pytest eval_tests/test_dev_onboarding_agent.py -v
```
