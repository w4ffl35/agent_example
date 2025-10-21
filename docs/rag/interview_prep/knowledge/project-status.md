# TODO List - Agent Take Home Exercise

## ⏱️ TIME ESTIMATES FOR REMAINING WORK

### Critical Features (Required for Submission)
- **Team Roster Tool** (simple non-RAG tool): 15-30 minutes
- **LangSmith Integration**: 1-2 hours
  - API key setup: 15 min
  - Code instrumentation: 30-45 min
  - Testing/verification: 30-45 min
- **Graph Diagram** (Mermaid): 30-45 minutes
- **Evaluation Dataset**: 45-60 minutes
  - Define test cases: 20 min
  - Write eval script: 25-40 min
- **Design Documentation**: 1-2 hours
  - Design decisions: 45-60 min
  - Tradeoffs section: 30-45 min
  - Future improvements: 15-30 min

**Total Estimated Time: 4-6 hours of focused work**

### Optional Features
- Docker setup: 30-45 minutes
- Guardrails/PII redaction: 1-2 hours
- Additional polish: 30-60 minutes

## 📚 RECOMMENDED READING MATERIAL

### LangChain Core Concepts (2-3 hours)
**Official Docs**:
- [LangChain Introduction](https://python.langchain.com/docs/get_started/introduction) - Start here
- [LCEL (LangChain Expression Language)](https://python.langchain.com/docs/concepts/#langchain-expression-language-lcel) - Core abstraction
- [Prompts and Prompt Templates](https://python.langchain.com/docs/concepts/#prompt-templates)
- [Chat Models vs LLMs](https://python.langchain.com/docs/concepts/#chat-models)
- [Tools and Tool Calling](https://python.langchain.com/docs/concepts/#tools) - CRITICAL for your project
- [Output Parsers](https://python.langchain.com/docs/concepts/#output-parsers)

**Key Concepts to Master**:
- Runnables and LCEL chains
- When to use `invoke()` vs `stream()` vs `batch()`
- Tool binding with `bind_tools()`
- Message types (HumanMessage, AIMessage, SystemMessage, ToolMessage)

### LangGraph State Management (2-3 hours)
**Official Docs**:
- [LangGraph Quick Start](https://langchain-ai.github.io/langgraph/tutorials/introduction/) - Essential
- [StateGraph Conceptual Guide](https://langchain-ai.github.io/langgraph/concepts/low_level/) - Deep dive
- [Nodes and Edges](https://langchain-ai.github.io/langgraph/concepts/low_level/#nodes) - Core building blocks
- [Conditional Edges](https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges) - Critical for your workflow
- [Persistence with Checkpointers](https://langchain-ai.github.io/langgraph/concepts/persistence/) - MemorySaver
- [Streaming](https://langchain-ai.github.io/langgraph/concepts/streaming/) - For your real-time output

**Key Concepts to Master**:
- StateGraph vs MessageGraph
- MessagesState schema (what you're using)
- How nodes modify state
- When to use conditional vs normal edges
- Checkpointer role in memory persistence
- Thread-based conversations with `thread_id`

**Your Implementation Deep Dive**:
- Read your own `workflow_manager.py` - understand every line
- Explain: Why `_define_nodes()` creates "model" and "tools" nodes
- Explain: How `_should_continue()` implements conditional routing
- Explain: What `trimmer` does and why it matters
- Explain: How `compile(checkpointer=...)` enables memory

### LangSmith Observability (1-2 hours)
**Official Docs**:
- [LangSmith Overview](https://docs.smith.langchain.com/) - What and why
- [Tracing](https://docs.smith.langchain.com/observability/tracing) - CRITICAL for your submission
- [Evaluation](https://docs.smith.langchain.com/evaluation) - For your eval dataset
- [Quick Start Guide](https://docs.smith.langchain.com/tutorials/quickstart)

**Key Concepts to Master**:
- What traces show (latency, token usage, tool calls)
- Environment variables: `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`
- How to view traces in UI
- Creating evaluation datasets
- Running evaluations and viewing results
- Custom metadata for runs

**Talking Points for Interview**:
- Why observability matters in production agents
- How LangSmith helps debug multi-step workflows
- Eval-driven development for agents
- Cost tracking with token usage

### RAG (Retrieval Augmented Generation) (2-3 hours)
**Official Docs**:
- [RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) - Complete walkthrough
- [Text Splitters](https://python.langchain.com/docs/concepts/#text-splitters) - RecursiveCharacterTextSplitter
- [Embeddings](https://python.langchain.com/docs/concepts/#embedding-models) - Vector representations
- [Vector Stores](https://python.langchain.com/docs/concepts/#vector-stores) - InMemoryVectorStore
- [Retrievers](https://python.langchain.com/docs/concepts/#retrievers) - Similarity search

**Key Concepts to Master**:
- Why RAG over fine-tuning (fresh data, lower cost, citations)
- Chunking strategies (size, overlap)
- Embedding models (what they do, why they matter)
- Similarity search (cosine similarity, top-k)
- Retrieval strategies (semantic search, MMR, hybrid)
- Context window management

**Your Implementation Deep Dive**:
- Read your `rag_manager.py` - understand lazy initialization pattern
- Explain: Why auto-index on search (convenience vs performance)
- Explain: Why chunk_size=1000, chunk_overlap=200
- Explain: Why k=2 retrieval (focused vs comprehensive)
- Explain: Why 500 char truncation (token limits, clarity)
- Explain: InMemoryVectorStore tradeoff (simplicity vs persistence)

**Advanced RAG Topics** (if you have time):
- Metadata filtering
- Parent Document Retriever
- Multi-query retrieval
- Re-ranking strategies
- Hybrid search (keyword + semantic)

### Agent Patterns & Architecture (1-2 hours)
**Official Docs**:
- [Agent Conceptual Guide](https://python.langchain.com/docs/concepts/#agents)
- [ReAct Pattern](https://python.langchain.com/docs/concepts/#react-agents) - Reasoning + Acting
- [Tool Calling](https://python.langchain.com/docs/concepts/#function-tool-calling)
- [Agent Executors](https://python.langchain.com/docs/concepts/#agents)

**Key Concepts to Master**:
- ReAct pattern: Thought → Action → Observation loop
- When agents should/shouldn't use tools
- Tool calling vs function calling (they're the same)
- Agent loops and error handling
- Multi-agent systems
- Human-in-the-loop patterns

**Your Implementation**:
- Explain your tool routing logic in `_should_continue()`
- Explain when your agent calls vs doesn't call tools
- Explain how you prevent infinite loops
- Explain how you handle tool errors

### LLM Fundamentals (Quick Review - 30 min)
**Core Concepts to Sound Expert On**:
- **Temperature**: 0 = deterministic, 1 = creative (you use 0.7 - why?)
- **Context Window**: Token limits (your trimmer handles this)
- **Tokens**: ~4 chars per token, affects cost and latency
- **Streaming**: Why it matters for UX
- **System Prompts**: Setting behavior and constraints
- **Few-shot Learning**: Examples in prompts
- **Prompt Engineering**: Clear instructions, examples, constraints

### Quick Reference Cheat Sheets
**LangChain**:
- `ChatPromptTemplate.from_messages()` - Create prompts
- `model.bind_tools(tools)` - Enable tool calling
- `model.invoke()` - Sync call
- `model.stream()` - Streaming call

**LangGraph**:
- `StateGraph(state_schema=MessagesState)` - Create graph
- `graph.add_node(name, func)` - Add processing step
- `graph.add_edge(START, "node")` - Direct routing
- `graph.add_conditional_edges(node, router_func)` - Conditional routing
- `graph.compile(checkpointer=MemorySaver())` - Add memory

**LangSmith**:
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "your-project"
```

### Interview Prep Strategy
1. **Deep dive your own code** (2 hours)
   - Read every file line-by-line
   - Explain each design decision out loud
   - Practice explaining the graph flow
   
2. **Practice explaining tradeoffs** (30 min)
   - InMemory vs persistent vector store
   - create_agent vs explicit StateGraph → You chose explicit StateGraph for visibility
   - Temperature 0.7 reasoning
   - k=2 retrieval vs more documents
   
3. **Prepare for "Why?" questions**
   - Why LangGraph over plain LangChain?
   - Why RAG over fine-tuning?
   - Why these specific documents in knowledge base?
   - Why modular folder structure?
   
4. **Demo practice** (1 hour)
   - Run through your app multiple times
   - Show different query types
   - Show how tools are called
   - Show memory persistence across questions
   - Be ready to show LangSmith traces

### Total Recommended Study Time: 8-12 hours
- LangChain: 2-3 hours
- LangGraph: 2-3 hours  
- LangSmith: 1-2 hours
- RAG: 2-3 hours
- Agents: 1-2 hours
- Your codebase: 2 hours
- Demo practice: 1 hour

**Priority**: Focus on LangGraph and RAG - these are your core implementation areas.

## 🎯 EXPLICITLY REQUIRED (From Instructions)

### ❌ CRITICAL - Must Complete Before Submission

#### LangSmith Integration (REQUIRED)
- [ ] Add LangSmith tracing instrumentation
- [ ] Configure LANGCHAIN_TRACING_V2 environment variable
- [ ] Add LANGCHAIN_API_KEY to environment
- [ ] Add LANGCHAIN_PROJECT configuration
- [ ] Ensure traces show up in LangSmith dashboard
- [ ] Add langsmith to requirements.txt
- [ ] Test that runs and metadata are visible in LangSmith UI

#### Evaluation Dataset (REQUIRED)
- [ ] Create one small eval dataset with expected outcomes
- [ ] Define test cases based on Developer Onboarding use case:
  - [ ] Test case 1: "How do I run tests?" → Should reference testing-guide.md
  - [ ] Test case 2: "Walk me through deploying to production" → Multi-step process
  - [ ] Test case 3: Follow-up question testing conversation memory
  - [ ] Test case 4: "What's the vacation policy?" → Should say "I don't know"
  - [ ] Test case 5: "Hello" → Should respond naturally without RAG
- [ ] Implement evaluation script/process
- [ ] Run evals and document results

#### Graph Diagram (REQUIRED)
- [ ] Create workflow visualization showing state and control flow
- [ ] Show how decisions are made and state transitions occur
- [ ] Include in README (Mermaid, draw.io, or screenshot)
- [ ] Clearly label: nodes, edges, decision points, state updates

#### Additional Tool Implementation (LIKELY REQUIRED)
**Issue**: Instructions say "At least one tool (could be a stubbed API, DB, or file system)" + separate RAG requirement suggests they want a tool BESIDES RAG.

Options to add:
- [ ] Option 1: Stub API tool (e.g., "check deployment status" hitting mock API)
- [ ] Option 2: File system tool (e.g., "list recent logs" reading from files)
- [ ] Option 3: Database query tool (stubbed - return mock user data)
- [ ] Option 4: GitHub API tool (stubbed - check PR status, recent commits)

**Recommendation**: Add a stubbed GitHub API tool for checking PR status or recent deployments - fits the Developer Onboarding theme.

### ⚠️ ARCHITECTURE CONCERN - Graph Visibility

**Current Issue**: We use `create_agent()` which hides LangGraph internals. Instructions emphasize "Graph clarity: show how state moves and decisions are made."

**Options**:
1. [ ] Keep create_agent() but create detailed diagram explaining internal flow
2. [ ] Refactor to explicit StateGraph with visible nodes/edges/routing
3. [ ] Hybrid: Use create_agent() but add custom nodes for complex logic

**Decision needed**: The instructions want to see graph/state clarity. Using create_agent() might not demonstrate this well enough.

## ✅ COMPLETED REQUIREMENTS

### Core Requirements Met
- [x] **Use LangChain** for model calls, tools, and RAG ✅
- [x] **Solve a problem end-to-end** - Developer Onboarding Assistant ✅
- [x] **RAG implementation** - Simple retrieval against knowledge base (13 docs) ✅
- [x] **At least one tool** - retrieve_context tool ✅ (but may need additional non-RAG tool)
- [x] **Streaming output** (nice-to-have) ✅

### Technical Implementation
- [x] LangGraph state management (via create_agent wrapper) ⚠️ (visibility concern)
- [x] LangChain integration for model calls (Ollama/llama3.2)
- [x] Memory persistence with MemorySaver
- [x] CLI application interface with threading
- [x] Unit tests (44 tests, 9 skipped)
- [x] Comprehensive README with setup instructions
- [x] Requirements.txt with dependencies

### RAG Implementation
- [x] InMemoryVectorStore
- [x] Document embeddings (Ollama llama3.2)
- [x] Retrieval tool (retrieve_context_tool)
- [x] Document loading from markdown
- [x] Text splitting with RecursiveCharacterTextSplitter
- [x] Automatic document indexing
- [x] Content truncation (500 char limit for focus)
- [x] Optimized retrieval (k=2 documents)

### Use Case - Developer Onboarding Assistant
- [x] Specific use case defined (USECASE.md)
- [x] System prompt configured for role
- [x] Complete knowledge base (13 comprehensive documents)
- [x] Example second agent (customer_support) showing modularity

### Documentation
- [x] README with quickstart instructions
- [x] CREATING_AGENTS.md guide
- [x] USECASE.md detailed use case
- [x] Code comments and docstrings

## 📋 REQUIRED DELIVERABLES CHECKLIST

Per instructions, must have:
- [x] **Repo** (exists)
- [ ] **README** with:
  - [x] Quickstart instructions ✅
  - [ ] Graph diagram ❌
  - [ ] Design notes: what you chose to do, and why ⚠️ (partial - needs expansion)
  - [ ] What you'd improve with more time ❌
- [ ] **LangSmith traces visible** ❌
- [ ] **Eval dataset with expected outcomes** ❌

## 🎁 NICE-TO-HAVES (From Instructions)

- [ ] **PII redaction or guardrails** - Content filtering, sensitive data handling
- [x] **Streaming output to interface** ✅ - Implemented with proper message filtering
- [ ] **Docker, Makefile, or simple setup script** - Easy deployment/setup

## 🔧 NOT REQUIRED (Good to Have but Not in Instructions)

### Modular Agent Architecture (Our Innovation)
- [x] Folder-based agent structure (agent_folder/system_prompt.md + knowledge/)
- [x] Easy agent creation - just add markdown files
- [x] Multiple example agents (dev_onboarding, customer_support)
- [x] CLI supports --agent_folder parameter
- [x] CREATING_AGENTS.md comprehensive guide

**Note**: This is creative/innovative but NOT explicitly required. Don't over-index on this.

### Code Quality Improvements
- [ ] Linting configuration (ruff, black, mypy)
- [ ] Integration tests (beyond unit tests)
- [ ] Pre-commit hooks
- [ ] Performance benchmarks
- [ ] Better error handling with custom exceptions
- [ ] Structured logging instead of print statements
- [ ] Configuration file (YAML/JSON)

### Enhanced Features
- [ ] Persistent vector store (ChromaDB, Pinecone)
- [ ] Multi-turn conversation improvements
- [ ] Additional tools beyond required minimum
- [ ] Web interface (they said CLI is fine)

## 🚨 CRITICAL ACTION ITEMS

### Priority 1 (BLOCKING SUBMISSION)
1. **Add LangSmith instrumentation** - Required for submission
2. **Create evaluation dataset** - Required for submission
3. **Create graph diagram** - Required for submission
4. **Add design rationale to README** - Required for submission
5. **Decide on graph visibility approach** - May need refactor

### Priority 2 (STRONGLY RECOMMENDED)
6. **Add non-RAG tool** - Instructions suggest tool + RAG separately
7. **Add "What I'd improve" section** - Required in README

### Priority 3 (NICE TO HAVE)
8. Docker/Makefile setup
9. PII redaction/guardrails

## 💭 KEY DECISIONS TO MAKE

### 1. Graph Architecture Decision (CRITICAL)
**Current**: Using `create_agent()` - simple but hides graph structure
**Problem**: Instructions emphasize "Graph clarity: show how state moves and decisions are made"

**Options**:
- **A**: Keep create_agent(), create very detailed diagram explaining the internal flow
  - Pros: Working code, simpler, less refactoring
  - Cons: May not demonstrate LangGraph understanding, less control
  
- **B**: Refactor to explicit StateGraph with nodes/edges
  - Pros: Shows clear understanding of LangGraph, explicit state transitions
  - Cons: More work, might break existing tests, more complex
  
- **C**: Hybrid - use create_agent() but add custom workflow around it
  - Pros: Balance of simplicity and visibility
  - Cons: Might feel forced

**Recommendation**: Need to decide based on how important "graph clarity" is to reviewers.

### 2. Additional Tool Decision
**Current**: Only have RAG retrieval tool
**Problem**: "At least one tool" + separate RAG requirement suggests they want both

**Recommended Addition**: Stubbed GitHub API tool
- Fits Developer Onboarding theme
- Shows ability to integrate external APIs
- Can be fully mocked/stubbed
- Examples: "check_pr_status", "get_recent_deployments", "list_open_issues"

### 3. Documentation Priority
**Must Add**:
1. Design decisions section - WHY we chose create_agent vs StateGraph, WHY modular architecture, etc.
2. Tradeoffs - InMemoryVectorStore vs persistent, temperature settings, etc.
3. What I'd improve - LangSmith earlier, more tools, persistent storage, etc.

## 📊 CURRENT STATUS vs REQUIREMENTS

| Requirement | Status | Notes |
|------------|--------|-------|
| LangGraph for state/control | ⚠️ | Using create_agent wrapper - visibility concern |
| LangChain for models/tools/RAG | ✅ | Complete |
| LangSmith instrumentation | ❌ | Not implemented |
| Solve problem end-to-end | ✅ | Developer Onboarding works |
| Graph clarity | ❌ | No diagram, hidden internal state |
| At least one tool | ⚠️ | Have RAG, may need additional non-RAG tool |
| RAG w/ knowledge base | ✅ | 13 documents, working retrieval |
| LangSmith traces visible | ❌ | Not implemented |
| Eval dataset | ❌ | Not implemented |
| Quickstart README | ✅ | Complete |
| Graph diagram | ❌ | Not created |
| Design notes | ⚠️ | Partial, needs expansion |
| What I'd improve | ❌ | Not written |

## 🎯 RECOMMENDED NEXT STEPS

1. **Decision**: Graph approach - keep create_agent() or refactor to StateGraph?
2. **Implement**: LangSmith tracing (CRITICAL)
3. **Implement**: Evaluation dataset with 5 test cases (CRITICAL)
4. **Create**: Graph diagram showing flow (CRITICAL)
5. **Add**: Second tool (stubbed GitHub API) (RECOMMENDED)
6. **Document**: Design decisions, tradeoffs, improvements (REQUIRED)
7. **Test**: Run through eval, verify LangSmith traces work
8. **Polish**: Clean up any rough edges, test end-to-end

## 🎨 EVALUATION CRITERIA ALIGNMENT

**Taste** - Does this feel demo-worthy?
- ✅ Modular document-driven architecture is creative
- ✅ Comprehensive knowledge base shows thought
- ⚠️ Need to ensure core requirements met first

**Clarity** - Is the graph/state easy to follow?
- ❌ No visible graph structure currently
- ❌ create_agent() hides state transitions
- 🎯 HIGHEST PRIORITY CONCERN

**Craft** - Are decisions explained? Tradeoffs sensible?
- ⚠️ Need to add design rationale section
- ⚠️ Need to document tradeoffs explicitly
- ✅ Code quality is good

**Vibes** - Curiosity, creativity, fun?
- ✅ Modular agent system shows creativity
- ✅ Multiple knowledge domains demonstrates thinking
- ✅ Good energy in the approach

**Overall**: Strong foundation, but missing critical explicit requirements (LangSmith, evals, graph visibility)

### Core Infrastructure
- [x] Basic LangGraph state management (via create_agent wrapper)
- [x] LangChain integration for model calls (using Ollama/llama3.2)
- [x] Agent class with model initialization and streaming
- [x] ~~WorkflowManager~~ (REMOVED - redundant with create_agent)
- [x] CLI application interface with threading
- [x] Memory persistence with MemorySaver (built into create_agent)
- [x] Message trimming for token management
- [x] Unit tests for App, ToolManager, and RAGManager (44 tests, 9 skipped)
- [x] Comprehensive README with setup and run instructions
- [x] Requirements.txt with core dependencies
- [x] Streaming output to interface (implemented in app.py with proper filtering)

### RAG (Retrieval Augmented Generation)
- [x] Set up vector store (InMemoryVectorStore)
- [x] Implement document embeddings (using Ollama llama3.2)
- [x] Add retrieval tool to fetch relevant documents (retrieve_context_tool)
- [x] Integrate retriever into the agent workflow (bound to agent via tools)
- [x] Document loading from markdown files
- [x] Text splitting with RecursiveCharacterTextSplitter
- [x] Automatic document indexing on search
- [x] RAGManager class with full document lifecycle
- [x] ToolManager class to manage RAG tool
- [x] Comprehensive unit tests for RAG functionality (19 tests passing)
- [x] Content truncation to prevent overwhelming the model (500 char limit)
- [x] Optimized retrieval (k=2 documents for focused results)

### Tool Implementation
- [x] Define RAG retrieval tool (retrieve_context)
- [x] Bind tools to the agent model (via create_agent)
- [x] Tool properly decorated with @tool decorator
- [x] Tool returns formatted context with source attribution
- [x] Test tool integration (test_tool_manager.py - 11 tests)
- [x] Tool includes clear usage instructions to prevent misuse

### Modular Agent Architecture
- [x] Folder-based agent structure (agent_folder/system_prompt.md + knowledge/)
- [x] Easy agent creation - just add markdown files, no code changes
- [x] Developer Onboarding Assistant (complete with 13 knowledge docs)
- [x] Customer Support Assistant (example with 2 knowledge docs)
- [x] CLI supports multiple agents via --agent_folder parameter
- [x] Automatic path resolution (system_prompt.md and knowledge/ subdirectory)

### Use Case Implementation - Developer Onboarding Assistant
- [x] System prompt configured for Developer Onboarding Assistant role
- [x] Specific use case defined (see USECASE.md)
- [x] Complete knowledge base content (13 comprehensive documents):
  - [x] setup-guide.md (dev environment setup)
  - [x] deployment-guide.md (deployment processes)
  - [x] coding-standards.md (Python formatting, linting, type hints)
  - [x] git-workflow.md (Git flow, branching, PRs)
  - [x] testing-guide.md (pytest, fixtures, coverage)
  - [x] architecture-overview.md (system architecture, patterns)
  - [x] ci-cd-pipeline.md (GitHub Actions, deployment automation)
  - [x] monitoring-logging.md (DataDog, Grafana, alerting)
  - [x] database-access.md (PostgreSQL, Redis, migrations)
  - [x] api-documentation.md (REST API, authentication)
  - [x] code-review-checklist.md (review criteria, best practices)
  - [x] incident-response.md (on-call, troubleshooting, post-mortems)
  - [x] security-practices.md (secrets, auth, vulnerabilities)
- [x] System prompt includes critical instructions to prevent raw tool output
- [x] System prompt includes examples of good vs bad responses
- [x] System prompt includes guidance on when to use/not use tools

### Documentation
- [x] Comprehensive README.md with:
  - [x] Feature overview
  - [x] Agent structure explanation
  - [x] Setup instructions
  - [x] Usage examples
  - [x] How to create new agents
  - [x] Example agents (dev_onboarding, customer_support)
  - [x] Architecture overview
  - [x] Design notes
- [x] CREATING_AGENTS.md - Complete guide for building new agents
- [x] USECASE.md - Detailed Developer Onboarding Assistant use case
- [x] Code is well-commented and readable

## ❌ INCOMPLETE - MUST HAVES

### LangSmith Integration (CRITICAL)
- [ ] Add LangSmith tracing instrumentation
- [ ] Configure LANGCHAIN_TRACING_V2 environment variable
- [ ] Add LANGCHAIN_API_KEY to environment
- [ ] Add LANGCHAIN_PROJECT configuration
- [ ] Ensure traces show up in LangSmith dashboard
- [ ] Add langsmith to requirements.txt

### Evaluation Dataset (CRITICAL)
- [ ] Create eval dataset with input/expected output pairs (based on USECASE.md)
  - [ ] Test case 1: Direct question ("How do I run tests?")
  - [ ] Test case 2: Multi-step process ("Walk me through deploying to production")
  - [ ] Test case 3: Follow-up question with context
  - [ ] Test case 4: Unknown information handling
  - [ ] Test case 5: Ambiguous query handling
- [ ] Implement evaluation script using LangSmith
- [ ] Document evaluation criteria
- [ ] Add eval results to README

### Graph Diagram (CRITICAL)
- [ ] Create workflow visualization (Mermaid, draw.io, or screenshot)
- [ ] Show agent execution flow (user input → tool call → response)
- [ ] Include in README or separate docs/

### Design Documentation
- [ ] Add "Design Decisions" section to README explaining:
  - [ ] Why create_agent() instead of explicit StateGraph
  - [ ] Modular folder-based architecture rationale
  - [ ] InMemoryVectorStore vs persistent store tradeoff
  - [ ] Content truncation strategy
  - [ ] Temperature setting (0.7) rationale
- [ ] Add "What I'd improve with more time" section
- [ ] Document tradeoffs and limitations

## 🎁 NICE-TO-HAVES

### Enhanced Features
- [ ] PII redaction or content guardrails
- [ ] Docker setup with Dockerfile
- [ ] Makefile for common operations
- [ ] Setup script for easy initialization
- [ ] Better error handling with custom exceptions
- [ ] Structured logging (instead of print statements)
- [ ] Configuration file for settings (YAML/JSON)
- [ ] Add additional tools beyond RAG (e.g., search tool, calculator)
- [ ] Persistent vector store (ChromaDB, Pinecone, etc.)
- [ ] Multi-turn conversation memory improvements

### Code Quality
- [ ] Add linting configuration (ruff, black, mypy)
- [ ] Add integration tests
- [ ] Add pre-commit hooks
- [ ] Improve error messages for common issues
- [ ] Add performance benchmarks

## 📋 PRIORITY ORDER

1. **LangSmith Integration** - Add tracing (CRITICAL REQUIREMENT)
2. **Evaluation Dataset** - Build test cases for LangSmith evals
3. **Graph Diagram** - Visualize the workflow
4. **Design Documentation** - Complete README with design decisions and improvements
5. **Nice-to-haves** - Add if time permits

## 🚨 STATUS SUMMARY

### What's Working Well ✅
- ✅ Modular, document-driven architecture - create agents with just markdown files
- ✅ Complete RAG implementation with automatic indexing and smart retrieval
- ✅ Comprehensive knowledge base (13 documents for Developer Onboarding)
- ✅ Proper streaming output with message filtering
- ✅ Strong test coverage (44 tests passing)
- ✅ Clean separation of concerns (App, ToolManager, RAGManager)
- ✅ Memory persistence across conversations
- ✅ Multiple example agents demonstrating flexibility
- ✅ Excellent documentation (README, CREATING_AGENTS, USECASE)

### Critical Gaps ❌
1. **LangSmith instrumentation** - No tracing/observability yet
2. **Evaluation dataset** - No defined test cases or eval framework
3. **Graph visualization** - No diagram of workflow/architecture
4. **Design rationale docs** - Missing explanation of key decisions

### Known Issues 🐛
- Agent may still occasionally echo tool output verbatim (system prompt tries to prevent this)
- Temperature at 0.7 may cause some response variability
- InMemoryVectorStore means index is rebuilt on each run (acceptable for demo)
- No retry logic for Ollama API calls
- No rate limiting or error recovery

### Architecture Notes 📐
- Using `create_agent()` wrapper which abstracts LangGraph StateGraph internally
- This provides state management, memory, and tool integration automatically
- Trade-off: Less control over graph structure, but simpler implementation
- If explicit graph nodes/edges needed, would require refactoring to use StateGraph directly

### Test Coverage 📊
- 44 unit tests total (9 skipped base class tests)
- RAGManager: 19 tests
- ToolManager: 11 tests  
- App: 11 tests
- All tests passing ✅
