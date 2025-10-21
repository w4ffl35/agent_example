# WorkflowManager Implementation Details

## Overview
The `WorkflowManager` class implements an explicit LangGraph `StateGraph` for the agent system. This provides visible state transitions, conditional routing, and memory persistence.

## File Location
`workflow_manager.py` (root directory)

## Architecture

### StateGraph Structure
```
START → "model" → (conditional) → "tools" → "model" → END
                       ↓
                     END (if no tool calls)
```

### Key Components

#### 1. Nodes
- **"model" node**: Executes `_call_model()` - invokes the LLM with trimmed context
- **"tools" node**: Executes tool calls using LangGraph's `ToolNode`

#### 2. Edges
- **START → "model"**: Begin with model inference
- **"model" → conditional**: Use `_should_continue()` to decide next step
  - If tool calls present → route to "tools" 
  - If no tool calls → route to END
- **"tools" → "model"**: After tool execution, return to model for synthesis

#### 3. State Management
- Uses `MessagesState` schema (built-in LangGraph state for chat)
- State contains `messages` list (HumanMessage, AIMessage, ToolMessage)
- Messages accumulate in conversation history

## Implementation Details

### Constructor
```python
def __init__(self, agent: Optional[Agent] = None, max_tokens: int = 2000)
```
- Accepts an `Agent` instance (wraps LLM + tools)
- Sets max token limit for context trimming (default: 2000)
- Creates `ToolNode` if agent has tools
- Calls `_define_nodes()` to build graph structure

### Message Trimming
```python
@property
def trimmer(self):
    return trim_messages(
        max_tokens=self._max_tokens,
        strategy="last",
        token_counter=self._token_counter,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )
```
**Why trimming matters**:
- LLMs have context window limits (e.g., 4K, 8K, 128K tokens)
- Long conversations exceed this limit
- Trimming keeps recent context within bounds
- Strategy "last" = keep most recent messages
- `include_system=True` = always keep system prompt
- `start_on="human"` = ensure context starts with user message

### Memory Persistence
```python
@property
def memory(self) -> MemorySaver:
    if self._memory is None:
        self._memory = MemorySaver()
    return self._memory
```
**MemorySaver checkpointer**:
- Stores conversation state in memory
- Enables multi-turn conversations
- Uses `thread_id` to separate conversation threads
- State persists across `invoke()` and `stream()` calls
- In-memory only (lost on restart) - tradeoff for simplicity

### Workflow Compilation
```python
@property
def compiled_workflow(self) -> CompiledStateGraph:
    if self._compiled_workflow is None:
        self._compiled_workflow = self.workflow.compile(checkpointer=self.memory)
    return self._compiled_workflow
```
**Compilation**:
- Converts StateGraph definition into executable workflow
- Adds checkpointer for state persistence
- Creates optimized execution plan
- Must compile before invoking

### Model Invocation
```python
def _call_model(self, state: MessagesState):
    trimmed_messages = self.trimmer.invoke(state["messages"])
    prompt = self.prompt_template.invoke(
        {"messages": trimmed_messages, "name": self._agent.name}
    )
    response = self._agent.invoke(prompt)
    return {"messages": [response]}
```
**Steps**:
1. Trim messages to fit context window
2. Build prompt from template (system prompt + message history)
3. Invoke agent (LLM with bound tools)
4. Return new message to append to state

**Key design**: Returns dict with "messages" key - LangGraph merges this into state

### Conditional Routing
```python
def _should_continue(self, state: MessagesState) -> str:
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return "end"
```
**Logic**:
- Examine last message in state (most recent AI response)
- If it contains `tool_calls`, route to "tools" node
- Otherwise, conversation is done, route to END

**This implements the ReAct pattern**:
- Reasoning (model thinks)
- Action (tool calls)
- Observation (tool results)
- Loop back for synthesis

### Streaming
```python
def stream(self, user_input: str):
    input_messages = [HumanMessage(user_input)]
    
    for event in self.compiled_workflow.stream(
        {"messages": input_messages}, 
        self.config,
        stream_mode="messages"
    ):
        if isinstance(message, AIMessage) and message.content:
            yield message
```
**Design choices**:
- `stream_mode="messages"` yields individual messages
- Filter to only AIMessage (skip ToolMessages)
- Provides real-time output to user
- Better UX than waiting for full response

## Design Decisions

### 1. Explicit StateGraph vs create_agent()
**Chose explicit StateGraph because**:
- Job requirements emphasize "Graph clarity: show how state moves and decisions are made"
- Visible nodes and edges demonstrate LangGraph understanding
- Full control over routing logic
- Can add custom nodes/edges easily
- Easier to explain and diagram

**Tradeoff**: More code vs using built-in `create_agent()` helper

### 2. InMemory MemorySaver
**Chose in-memory persistence because**:
- Simple for demo/interview purposes
- No external dependencies (Redis, Postgres)
- Fast and reliable
- Sufficient for single-user CLI

**Tradeoff**: State lost on restart (production would use persistent checkpointer)

### 3. Message Trimming (2000 tokens)
**Chose 2000 token limit because**:
- llama3.2 has limited context window
- Keeps conversations focused on recent context
- Prevents token overflow errors
- 2000 tokens ≈ 8000 characters of conversation

**Tradeoff**: May lose early conversation context in long sessions

### 4. ToolNode from prebuilt
**Chose LangGraph's ToolNode because**:
- Handles tool execution automatically
- Proper error handling built-in
- Returns ToolMessage objects correctly
- Standard pattern, no need to reinvent

## Interview Talking Points

### On StateGraph Architecture
"I implemented an explicit StateGraph with two nodes: 'model' for LLM inference and 'tools' for tool execution. The workflow uses conditional routing - after the model responds, _should_continue() checks if there are tool_calls. If yes, we route to the tools node, execute the tools, then loop back to the model for synthesis. This implements the ReAct pattern: Reason → Act → Observe."

### On Memory Management
"I use LangGraph's MemorySaver checkpointer for conversation persistence. It stores state in-memory keyed by thread_id. For production, I'd swap to a persistent checkpointer backed by Redis or Postgres, but in-memory is perfect for this demo - simple, fast, no external deps."

### On Message Trimming
"The trimmer keeps context under 2000 tokens using a 'last' strategy - it preserves the system prompt and the most recent messages. This prevents context overflow while maintaining conversation coherence. It's essential for long conversations that would otherwise exceed the LLM's context window."

### On Tool Routing
"The conditional edge from model to tools uses _should_continue() to inspect the last message. If the LLM wants to call a tool, the message has a tool_calls attribute. We route to the tools node, execute them, and return to the model so it can synthesize the tool results into a natural response. This loop continues until the model generates a response without tool calls."

## Code Quality Notes
- Lazy initialization pattern for properties (create on first access)
- Type hints throughout for clarity
- Proper separation of concerns (Agent vs WorkflowManager)
- Clean abstraction - app.py doesn't need to know about StateGraph internals
