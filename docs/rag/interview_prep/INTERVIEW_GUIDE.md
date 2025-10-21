# Interview Preparation Agent - Quick Start

## Purpose
This agent will interview YOU for the Senior Agent Engineer role. It will quiz you on:
- Your codebase implementation
- LangChain/LangGraph/LangSmith concepts
- RAG architecture
- Design decisions and tradeoffs
- Job requirements

## How to Use

### Run the Interview
```bash
python main.py --agent_folder interview_prep --agent_name "Interviewer"
```

### What to Expect
1. **Phase 1: Codebase Questions** (3-4 questions)
   - "Walk me through your StateGraph architecture..."
   - "Explain your RAG implementation..."
   - "How does conditional routing work?"

2. **Phase 2: Conceptual Knowledge** (3-4 questions)
   - "Explain LangChain vs LangGraph..."
   - "What is RAG and why use it?"
   - "Explain the ReAct pattern..."

3. **Phase 3: Design & Tradeoffs** (2-3 questions)
   - "Why temperature 0.7?"
   - "Why k=2 retrieval?"
   - "What would you improve?"

4. **Phase 4: Production Thinking** (2-3 questions)
   - "How to handle rate limiting?"
   - "What metrics to track?"
   - "How to debug in production?"

5. **Final Feedback**
   - Overall assessment (STRONG HIRE / HIRE / MAYBE / NO HIRE)
   - Strengths (3 specific points)
   - Areas for improvement (3 specific points)
   - Study recommendations

## Knowledge Base Contents

The agent has access to:
1. **job-requirements.md** - Full INSTRUCTIONS.md from the job posting
2. **project-status.md** - Your TODO list and current status
3. **usecase.md** - Developer Onboarding use case details
4. **workflow-manager-code.md** - Deep dive on StateGraph implementation
5. **rag-manager-code.md** - Deep dive on RAG implementation
6. **langchain-concepts.md** - Core LangChain/LangGraph concepts
7. **architecture.md** - System design overview

## Tips for Success

### Be Specific
❌ "We use RAG for retrieval"
✅ "We use RecursiveCharacterTextSplitter with 1000 char chunks and 200 char overlap, then embed with Ollama llama3.2 into an InMemoryVectorStore. We retrieve k=2 chunks and truncate to 500 chars to keep context focused."

### Reference Your Code
❌ "The workflow handles tool calls"
✅ "In workflow_manager.py, the _should_continue() method checks if the last AIMessage has tool_calls. If yes, we route to the tools node, execute them, then loop back to model for synthesis."

### Explain Tradeoffs
❌ "We use InMemoryVectorStore"
✅ "We use InMemoryVectorStore for simplicity and fast setup, perfect for a demo. The tradeoff is the index rebuilds on restart. Production would use ChromaDB for persistence."

### Say "I Don't Know" When Needed
If you don't know something, say so! Then explain how you'd figure it out:
❌ *Makes up answer*
✅ "I'm not sure about that specific detail. I'd check the LangGraph docs on conditional edges, or look at the prebuilt agent implementations for examples."

### Use the Tool
The interviewer can use retrieve_context to check your implementation. Be accurate!

## Practice Runs

### Run 1: Warm Up
- Get comfortable with the format
- Practice explaining your code
- Note what you struggle with

### Run 2: Deep Dive
- Focus on areas you struggled with
- Practice tradeoff explanations
- Work on being concise

### Run 3: Polish
- Smooth delivery
- Confident answers
- Quick retrieval from memory

## Study Before Running

1. **Read Your Code** (1 hour)
   - workflow_manager.py line by line
   - rag_manager.py line by line
   - agent.py, tool_manager.py, app.py

2. **Review Concepts** (2 hours)
   - Read langchain-concepts.md
   - Read architecture.md
   - Practice explaining out loud

3. **Memorize Key Numbers**
   - chunk_size: 1000
   - chunk_overlap: 200
   - k=2 retrieval
   - 500 char truncation
   - 2000 token trim limit
   - temperature: 0.7
   - 66 tests passing

4. **Prepare Tradeoff Explanations**
   - InMemory vs persistent vector store
   - Explicit StateGraph vs create_agent
   - Temperature 0.7 reasoning
   - k=2 vs more chunks

## Common Weak Points (Study These!)

### LangGraph Confusion
- **Difference between nodes and edges**
  - Nodes: Functions that process state
  - Edges: Connections between nodes
- **When to use conditional edges**
  - When routing depends on state content
  - Our case: check if tool_calls present

### RAG Confusion
- **What are embeddings?**
  - Vector representations of text meaning
  - Similar text = similar vectors
- **What is semantic search?**
  - Search by meaning, not keywords
  - Uses cosine similarity on vectors

### StateGraph Confusion
- **What is MessagesState?**
  - Built-in state schema for chat
  - Has messages list with add_messages reducer
- **What does compile() do?**
  - Converts StateGraph to executable workflow
  - Adds checkpointer for memory

### Tool Calling Confusion
- **What is bind_tools()?**
  - Makes LLM aware of available tools
  - Enables tool_calls in AIMessage
- **What is ToolNode?**
  - Executes tools from tool_calls
  - Returns ToolMessage with results

## After the Interview

1. **Note gaps** - Write down what you struggled with
2. **Study those topics** - Focus on weak areas
3. **Read the docs** - Official LangChain/LangGraph docs
4. **Run again** - Practice until smooth
5. **Real interview** - You'll be ready!

## Emergency Cheat Sheet

### Graph Flow
START → model → (has tool_calls?) → tools → model → END

### Key Files
- workflow_manager.py: StateGraph + routing
- rag_manager.py: Document → chunks → embeddings → search
- agent.py: LLM + tools wrapper
- tool_manager.py: retrieve_context tool
- app.py: CLI orchestration

### Key Concepts
- **LangGraph**: State machine for agents
- **StateGraph**: Define nodes + edges
- **MessagesState**: Chat state schema
- **MemorySaver**: In-memory conversation persistence
- **ToolNode**: Executes tool calls
- **trim_messages**: Keeps context under token limit
- **Embeddings**: Text → vectors for semantic search
- **RAG**: Retrieval Augmented Generation (better than fine-tuning)
- **ReAct**: Reason → Act → Observe loop

### Numbers to Memorize
- chunk_size: 1000 characters
- chunk_overlap: 200 characters
- k: 2 documents retrieved
- truncation: 500 characters per document
- max_tokens: 2000 for trimming
- temperature: 0.7
- tests: 66 passing (15 skipped base class tests)

Good luck! You got this! 🚀
