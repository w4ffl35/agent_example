# LangChain Agent Example

This is a simple agent that uses LangChain and LangGraph to load an agent with RAG capabilities and a
command prompt interface. The agent runs locally using the Gemma3 model via Ollama.

The point of this demo is to show a minimal example of how to set up an agent with LangChain 
that can be used as a customer service bot.

## Setup

### Install Ollama and Run Gemma3

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

```bash
python -m unittest discover -s tests
```
