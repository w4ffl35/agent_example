# System Architecture Overview

## High-Level Design

### Component Diagram
```
User Input
    ↓
App (CLI)
    ↓
WorkflowManager (StateGraph)
    ↓
Agent (LLM + Tools)
    ↓
ToolManager → RAGManager → Vector Store
```

### Data Flow
```
1. User types question in CLI
2. App creates HumanMessage, calls workflow_manager.stream()
3. WorkflowManager:
   a. Trims message history to fit context window
   b. Builds prompt (system + messages)
   c. Invokes Agent (LLM with bound tools)
4. Agent (ChatOllama):
   a. Processes prompt
   b. Decides if tools needed
   c. Returns AIMessage (maybe with tool_calls)
5. WorkflowManager conditional routing:
   a. If tool_calls → route to "tools" node
   b. If no tool_calls → route to END
6. Tools node (if triggered):
   a. Execute tool (retrieve_context)
   b. RAGManager searches vector store
   c. Returns ToolMessage with results
   d. Route back to "model" node
7. Agent synthesizes tool results into answer
8. Stream AIMessage content back to user
```

## Component Responsibilities

### App (app.py)
**Role**: CLI orchestration and user interaction
**Responsibilities**:
- Handle user input loop
- Manage application lifecycle (start/stop)
- Stream output to terminal
- Filter messages (only show AIMessage content)
- Configure agent folder paths

**Key design**: Modular architecture - agent folder determines system prompt and knowledge base

### WorkflowManager (workflow_manager.py)
**Role**: LangGraph StateGraph coordinator
**Responsibilities**:
- Define graph structure (nodes, edges)
- Implement conditional routing logic
- Trim messages to fit context window
- Manage conversation state via MemorySaver
- Compile and execute workflow

**Key design**: Explicit StateGraph for graph visibility (job requirement)

### Agent (agent.py)
**Role**: LLM wrapper with tool support
**Responsibilities**:
- Initialize ChatOllama model
- Bind tools to model
- Load system prompt
- Invoke/stream LLM calls

**Key design**: Simple wrapper, delegates to WorkflowManager for orchestration

### ToolManager (tool_manager.py)
**Role**: Tool creation and management
**Responsibilities**:
- Create retrieve_context tool
- Format tool output with source attribution
- Truncate content to prevent overwhelming model
- Coordinate with RAGManager

**Key design**: Separates tool logic from RAG implementation

### RAGManager (rag_manager.py)
**Role**: Document lifecycle management
**Responsibilities**:
- Load markdown documents from directory
- Split documents into chunks
- Generate embeddings
- Index in vector store
- Perform semantic search

**Key design**: Lazy initialization, auto-indexing on first search

## Key Design Decisions

### 1. Explicit StateGraph (WorkflowManager)
**Decision**: Use explicit LangGraph StateGraph vs LangChain's create_agent()

**Rationale**:
- Job requires "Graph clarity: show how state moves and decisions are made"
- Explicit nodes/edges demonstrate LangGraph understanding
- Full control over routing logic
- Easy to explain and diagram
- Can extend with custom nodes easily

**Tradeoff**: More code vs using built-in helper

### 2. Modular Agent Architecture
**Decision**: Folder-based agent structure (agent_folder/system_prompt.md + knowledge/)

**Rationale**:
- Create new agents without code changes
- Non-technical users can contribute knowledge
- Clean separation of concerns
- Demonstrates extensible design
- Easy to add new domains (dev_onboarding, customer_support, etc.)

**Tradeoff**: Slightly more complex paths, but huge usability win

### 3. InMemoryVectorStore
**Decision**: Use in-memory vector store vs persistent (ChromaDB, Pinecone)

**Rationale**:
- Simple, no external dependencies
- Fast and reliable
- Perfect for demo/interview
- Easy to set up and test

**Tradeoff**: Index rebuilt on each run (acceptable for demo, not for production)

### 4. Message Trimming (2000 tokens)
**Decision**: Trim conversation history to 2000 tokens

**Rationale**:
- llama3.2 has limited context window
- Prevents token overflow errors
- Keeps conversation focused
- Preserves system prompt + recent messages

**Tradeoff**: May lose early context in long conversations

### 5. k=2 Retrieval + 500 char Truncation
**Decision**: Retrieve 2 chunks, truncate each to 500 chars

**Rationale**:
- Focused retrieval (quality over quantity)
- Prevents overwhelming model with context
- Keeps responses crisp
- Reduces token usage

**Tradeoff**: May miss relevant info if too conservative

### 6. Temperature 0.7
**Decision**: Set LLM temperature to 0.7

**Rationale**:
- Balance between creativity and consistency
- 0.0 = too robotic for assistant role
- 1.0 = too random, may hallucinate
- 0.7 = natural but reliable

**Tradeoff**: Some response variability (acceptable for conversational agent)

### 7. Lazy Initialization Pattern
**Decision**: Properties initialize on first access

**Rationale**:
- Faster startup (don't load until needed)
- Memory efficient
- Clear dependency chains
- Automatic error handling (fails at use time, not init time)

**Tradeoff**: First use slightly slower, but better overall

### 8. Streaming Output
**Decision**: Stream AIMessage content in real-time

**Rationale**:
- Better UX (see progress)
- Natural conversation feel
- Can cancel long responses
- Modern AI app pattern

**Tradeoff**: Slightly more complex message filtering

## Production Improvements

### If Building This for Production:

1. **Persistent Vector Store**
   - Replace InMemoryVectorStore with ChromaDB or Pinecone
   - Pre-index documents (don't rebuild every time)
   - Enable metadata filtering

2. **Persistent Checkpointer**
   - Replace MemorySaver with PostgresSaver
   - Enable multi-user support
   - Allow conversation replay

3. **Error Handling**
   - Retry logic for LLM API calls
   - Graceful degradation if tools fail
   - Better error messages to users
   - Logging and alerting

4. **Observability**
   - LangSmith tracing (already planned)
   - Metrics: latency, token usage, tool calls
   - Dashboards for monitoring
   - Cost tracking

5. **Evaluation Framework**
   - Regression test suite
   - Automated evals on every change
   - A/B testing different prompts/parameters
   - Human feedback loop

6. **Scale & Performance**
   - Async LLM calls
   - Batch embedding generation
   - Cache frequent queries
   - Load balancing

7. **Security & Compliance**
   - PII detection and redaction
   - Input validation
   - Rate limiting
   - Audit logging
   - Content filtering

8. **Enhanced RAG**
   - Hybrid search (semantic + keyword)
   - Re-ranking with cross-encoder
   - Query expansion
   - Parent document retrieval
   - Metadata filtering

## Architecture Patterns Used

### 1. Lazy Initialization
Properties load on first access, not in constructor
```python
@property
def documents(self):
    if self._documents is None:
        self._documents = load_documents()
    return self._documents
```

### 2. Strategy Pattern
Vector store class is configurable
```python
def __init__(self, vector_store_class: Type[VectorStore] = InMemoryVectorStore)
```

### 3. Dependency Injection
Agent receives tools from outside
```python
def __init__(self, tools: List[Callable] = None)
```

### 4. Facade Pattern
ToolManager hides RAGManager complexity
```python
retrieve_context_tool()  # Simple interface, complex implementation
```

### 5. Builder Pattern
StateGraph construction
```python
workflow = StateGraph(state_schema=MessagesState)
workflow.add_node(...)
workflow.add_edge(...)
app = workflow.compile(...)
```

## Testing Strategy

### Unit Tests (66 tests, all passing)
- **RAGManager**: Document loading, splitting, indexing, search
- **ToolManager**: Tool creation, formatting, execution
- **WorkflowManager**: Graph structure, memory, invocation
- **Agent**: Model initialization, tool binding
- **App**: User interaction, streaming, quit handling

### Test Coverage Areas
✅ Happy paths (successful queries)
✅ Edge cases (empty directories, no documents)
✅ Error handling (invalid input)
✅ Property initialization (lazy loading)
✅ Message filtering (streaming)

### Integration Testing (Manual)
- End-to-end user queries
- Multi-turn conversations
- Tool calling behavior
- Memory persistence

## File Structure
```
agent/
├── app.py              # CLI application
├── agent.py            # LLM wrapper
├── workflow_manager.py # StateGraph coordinator
├── tool_manager.py     # Tool creation
├── rag_manager.py      # RAG implementation
├── main.py             # Entry point
├── requirements.txt    # Dependencies
├── README.md           # Documentation
├── docs/
│   └── rag/
│       ├── dev_onboarding/       # Developer assistant
│       │   ├── system_prompt.md
│       │   └── knowledge/        # 13 documents
│       ├── customer_support/     # Support assistant
│       │   ├── system_prompt.md
│       │   └── knowledge/        # 2 documents
│       └── interview_prep/       # Interview practice
│           ├── system_prompt.md
│           └── knowledge/        # This file + others
└── tests/
    ├── test_app.py
    ├── test_agent.py
    ├── test_workflow_manager.py
    ├── test_tool_manager.py
    └── test_rag_manager.py
```

## Interview Talking Points

### On the overall architecture
"The system uses a layered architecture. At the top, App handles CLI interaction. WorkflowManager orchestrates the LangGraph StateGraph with explicit nodes for model and tools. Agent wraps the LLM with bound tools. ToolManager creates the retrieve_context tool, which delegates to RAGManager for semantic search. Each component has a single responsibility, making the system testable and maintainable."

### On state management
"I use LangGraph's StateGraph with MessagesState for conversation management. The WorkflowManager defines two nodes: 'model' for LLM inference and 'tools' for tool execution. Conditional routing checks if the AI wants to call tools. If yes, we execute them and loop back to the model for synthesis. MemorySaver provides conversation persistence keyed by thread_id."

### On the modular agent design
"Instead of hardcoding one agent, I built a folder-based system. Each agent is a directory with system_prompt.md and a knowledge/ folder of documents. To create a new agent, you just add markdown files - no code changes needed. This demonstrates extensible design and separates domain knowledge from code logic."

### On RAG implementation
"RAG follows a standard pipeline: load documents, split into chunks (1000 chars, 200 overlap), generate embeddings (Ollama llama3.2), index in vector store (InMemory for simplicity), and search with k=2 retrieval. I chose RecursiveCharacterTextSplitter to respect document structure. Content is truncated to 500 chars to keep context focused."

### On production readiness
"This is production-inspired but optimized for a demo. For real production, I'd add: persistent vector store (ChromaDB), persistent checkpointer (PostgreSQL), error retry logic, LangSmith monitoring, evaluation framework, PII redaction, and async LLM calls. The architecture supports all of this - just swap implementations."
