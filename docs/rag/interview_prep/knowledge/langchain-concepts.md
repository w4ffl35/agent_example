# Core LangChain & LangGraph Concepts

## LangChain vs LangGraph

### LangChain
**What**: Framework for composing LLM applications
**Use for**: 
- Simple chains (prompt → model → output)
- Tool calling
- RAG pipelines
- Linear workflows

**Key abstractions**:
- `ChatPromptTemplate` - Format prompts
- `ChatModel.invoke()` - Call LLM
- `bind_tools()` - Enable tool calling
- `LCEL` - Chain components with `|` operator

### LangGraph
**What**: State machine framework built on LangChain
**Use for**:
- Multi-step agent workflows
- Conditional routing (if/else logic)
- Cycles and loops
- Complex state management
- Explicit control flow

**Key abstractions**:
- `StateGraph` - Define nodes and edges
- `MessagesState` - Built-in state for chat
- `add_node()` - Add processing steps
- `add_edge()` - Connect nodes
- `add_conditional_edges()` - Add routing logic
- `compile()` - Create executable workflow

**When to use LangGraph over LangChain**:
- Need visibility into state transitions (our case!)
- Conditional logic based on LLM output
- Multi-agent systems
- Human-in-the-loop workflows
- Complex error handling/retry logic

## StateGraph Architecture

### Our Implementation
```python
# Create graph
workflow = StateGraph(state_schema=MessagesState)

# Add nodes
workflow.add_node("model", call_model_function)
workflow.add_node("tools", tool_node)

# Add edges
workflow.add_edge(START, "model")
workflow.add_conditional_edges(
    "model",
    should_continue_function,
    {"tools": "tools", "end": END}
)
workflow.add_edge("tools", "model")

# Compile with memory
app = workflow.compile(checkpointer=MemorySaver())
```

### MessagesState
```python
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

**What it provides**:
- `messages` list - Conversation history
- Automatic message appending (via `add_messages` reducer)
- Standard format for chat applications

**Message types**:
- `HumanMessage` - User input
- `AIMessage` - LLM response (may contain `tool_calls`)
- `ToolMessage` - Tool execution results
- `SystemMessage` - System instructions

### Nodes
**What**: Functions that process state
**Signature**: `def node(state: MessagesState) -> dict`
**Returns**: Dictionary to update state (gets merged)

Example:
```python
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}  # Appends to messages list
```

### Edges
**Normal edges**: Always follow this path
```python
workflow.add_edge(START, "model")  # Always start with model
workflow.add_edge("tools", "model")  # Always return to model after tools
```

**Conditional edges**: Route based on function
```python
workflow.add_conditional_edges(
    "model",                    # From this node
    should_continue,            # Call this function
    {"tools": "tools", "end": END}  # Map return value to next node
)
```

### Checkpointers (Memory)
**Purpose**: Persist state between invocations
**Types**:
- `MemorySaver()` - In-memory (our choice)
- `SqliteSaver()` - SQLite database
- `PostgresSaver()` - PostgreSQL
- Custom implementations

**How it works**:
- State saved after each node execution
- `thread_id` identifies conversation
- Can replay from any checkpoint
- Enables multi-turn conversations

**Our usage**:
```python
config = {"configurable": {"thread_id": "1"}}
app.invoke({"messages": [...]}, config)
```

## Tool Calling

### Tool Definition
```python
from langchain_core.tools import tool

@tool
def retrieve_context(query: str) -> str:
    """Search knowledge base for relevant information.
    
    Args:
        query: Search query describing what information is needed
    """
    # Implementation
    return results
```

**Key elements**:
- `@tool` decorator - Makes function LangChain-compatible
- Docstring - LLM sees this as tool description
- Type hints - Define parameter types
- Return type - What the tool produces

### Tool Binding
```python
model_with_tools = model.bind_tools([retrieve_context])
```

**What this does**:
- Adds tool schemas to LLM request
- LLM can now output `tool_calls` in response
- Doesn't execute tools - just makes LLM aware

### Tool Execution
```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([retrieve_context])
workflow.add_node("tools", tool_node)
```

**ToolNode**:
- Takes AIMessage with `tool_calls`
- Executes each tool
- Returns list of ToolMessage with results
- Handles errors automatically

### ReAct Pattern
**Reasoning and Acting**:
1. **Reason**: LLM thinks about the task
2. **Act**: LLM decides to call tool(s)
3. **Observe**: Tool results added to context
4. **Reason**: LLM synthesizes tool results
5. Repeat if needed

**Our implementation**:
```
User: "How do I deploy?"
  → Model reasons: "I need deployment docs"
  → Model acts: tool_calls=[retrieve_context("deployment")]
  → Route to tools node
  → Tools execute: returns deployment guide excerpt
  → Route back to model
  → Model synthesizes: "To deploy, follow these steps..."
```

## Message Trimming

### Why Trim?
- LLMs have token limits (context window)
- Long conversations exceed limits
- Need to keep relevant context, discard old messages

### Our Strategy
```python
trim_messages(
    max_tokens=2000,
    strategy="last",
    include_system=True,
    start_on="human"
)
```

**Parameters**:
- `max_tokens=2000` - Keep under this limit
- `strategy="last"` - Keep most recent messages
- `include_system=True` - Always keep system prompt
- `start_on="human"` - Ensure context starts with user message

**Why "last" strategy?**
- Recent context most relevant
- Maintains conversation flow
- Earlier messages less important

## Streaming

### Why Stream?
- Better UX (real-time output)
- See progress for long responses
- Can cancel if needed

### Implementation
```python
for event in app.stream(input, config, stream_mode="messages"):
    message = event[0]
    if isinstance(message, AIMessage) and message.content:
        print(message.content, end="", flush=True)
```

**Stream modes**:
- `"messages"` - Yields individual messages (our choice)
- `"values"` - Yields full state after each node
- `"updates"` - Yields state deltas

**Why filter to AIMessage?**
- Skip ToolMessage (internal tool results)
- Only show user-facing content
- Cleaner output

## LangSmith Integration

### Purpose
- **Tracing**: See every LLM call, tool call, latency
- **Debugging**: Inspect what went wrong
- **Evaluation**: Test agent on datasets
- **Monitoring**: Track production metrics

### Setup
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "your-project-name"
```

### What Gets Traced
- Every LLM invoke/stream call
- Tool executions
- Chain steps
- Latency for each step
- Token usage
- Errors and exceptions

### Evaluation
```python
from langsmith import Client

client = Client()

# Create dataset
dataset = client.create_dataset("test-cases")
client.create_examples(
    dataset_id=dataset.id,
    inputs=[{"query": "How do I deploy?"}],
    outputs=[{"expected": "deployment guide steps"}]
)

# Run eval
results = client.evaluate(
    app.invoke,
    data=dataset.name,
    evaluators=[correct_answer_evaluator]
)
```

## Interview Talking Points

### On choosing LangGraph
"I used LangGraph instead of plain LangChain because the job requirements emphasized 'Graph clarity: show how state moves and decisions are made.' An explicit StateGraph with visible nodes, edges, and conditional routing demonstrates this clearly. It also gives me full control over the agent loop - I can see exactly when tools are called and how state transitions."

### On MessagesState
"MessagesState is LangGraph's built-in state schema for chat. It provides a messages list with automatic appending via the add_messages reducer. When a node returns {'messages': [new_msg]}, LangGraph merges it into the state rather than replacing. This makes conversation history management automatic."

### On MemorySaver
"I chose MemorySaver for checkpointing because it's simple and perfect for a demo. It stores conversation state in memory keyed by thread_id. The tradeoff is state is lost on restart, but that's acceptable here. Production would use SqliteSaver or PostgresSaver for persistence."

### On Tool Calling
"My agent uses bind_tools() to make the LLM aware of available tools. When the LLM wants information, it outputs tool_calls in its response. My conditional edge detects this and routes to the ToolNode, which executes the tools and returns ToolMessages. Then we loop back to the model so it can synthesize the results into a natural answer. This implements the ReAct pattern."

### On Streaming
"I implemented streaming with stream_mode='messages' for real-time output. The code filters to only yield AIMessages with content, skipping internal ToolMessages. This gives users immediate feedback as the agent thinks, much better UX than waiting for the complete response."
