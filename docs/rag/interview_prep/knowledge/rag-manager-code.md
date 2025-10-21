# RAGManager Implementation Details

## Overview
The `RAGManager` class handles the complete document lifecycle for Retrieval Augmented Generation (RAG): loading, splitting, embedding, indexing, and searching.

## File Location
`rag_manager.py` (root directory)

## RAG Pipeline

```
Load Documents → Split into Chunks → Generate Embeddings → Index in Vector Store → Search
```

## Implementation Details

### Constructor Parameters
```python
def __init__(
    self,
    provider_name: str,          # "ollama"
    model_name: str,              # "llama3.2"
    rag_directory: str,           # "docs/rag/dev_onboarding/knowledge"
    chunk_size: int = 1000,       # Characters per chunk
    chunk_overlap: int = 200,     # Overlap between chunks
    vector_store_class: Type[VectorStore] = InMemoryVectorStore,
)
```

### 1. Document Loading
```python
@property
def documents(self) -> List[Document]:
    if self._documents is None:
        self._documents = [
            Document(
                page_content=md_file.read_text(encoding="utf-8"),
                metadata={"source": str(md_file)},
            )
            for md_file in self.rag_path.glob("**/*.md")
        ]
    return self._documents
```

**Design**:
- Recursively finds all `.md` files in knowledge directory
- Each file becomes one Document object
- Metadata tracks source file for citations
- Lazy loading (only loads when accessed)

**Interview talking point**: "Why markdown? It's human-readable, version controllable, and easy for non-engineers to contribute to. Perfect for knowledge bases."

### 2. Text Splitting
```python
@property
def text_splitter(self) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=self.chunk_size,      # 1000 chars
        chunk_overlap=self.chunk_overlap, # 200 chars  
        add_start_index=True,
    )
```

**Why RecursiveCharacterTextSplitter?**
- Splits on natural boundaries (paragraphs, sentences)
- Respects markdown structure
- Better than naive character splitting
- Preserves context across chunks with overlap

**Chunk size (1000 chars)**:
- ~250 tokens per chunk
- Balances specificity vs context
- Too small = loses context
- Too large = less precise retrieval

**Chunk overlap (200 chars)**:
- Prevents information loss at boundaries
- Example: Important info spanning two chunks stays connected
- 20% overlap is a good default

**add_start_index=True**:
- Tracks where chunk came from in original document
- Useful for citing specific sections

### 3. Embeddings
```python
@property
def embeddings(self) -> Embeddings:
    if self._embeddings is None:
        self._embeddings = init_embeddings(f"{self.provider_name}:{self.model_name}")
    return self._embeddings
```

**What are embeddings?**
- Vector representations of text
- Similar meaning = similar vectors
- Enables semantic search (not just keyword matching)
- llama3.2 embeddings are ~4096 dimensions

**Why Ollama embeddings?**
- Local execution (no API costs, privacy)
- Same model for consistency (llama3.2)
- Fast inference
- No external dependencies

### 4. Vector Store
```python
@property
def vector_store(self) -> Type[VectorStore]:
    if self._vector_store is None:
        self._vector_store = self.vector_store_class_(self.embeddings)
    return self._vector_store
```

**InMemoryVectorStore choice**:
- Simple, fast, no setup
- Perfect for demo/interview
- Tradeoff: Rebuilt on every run
- Production alternative: ChromaDB, Pinecone, Weaviate

### 5. Indexing (Lazy Auto-Index)
```python
@property
def index_documents(self) -> List[str]:
    if self._document_ids is None:
        self._document_ids = self.vector_store.add_documents(self.split_documents)
    return self._document_ids
```

**Lazy initialization pattern**:
- Don't index until first search
- Saves time if RAG never used
- Properties auto-trigger dependencies

### 6. Search
```python
def search(self, query: str, k: int = 2) -> List[Document]:
    # Auto-index on first search
    if not self._document_ids:
        self.index_documents
    
    return self.vector_store.similarity_search(query, k=k)
```

**k=2 choice**:
- Retrieve 2 most relevant chunks
- Keeps context focused
- Prevents overwhelming the model
- Tradeoff: May miss relevant info if too low

**Similarity search**:
- Embeds query into same vector space
- Calculates cosine similarity with all document vectors
- Returns top-k closest matches
- This is semantic search (meaning-based, not keyword)

## Design Decisions

### 1. Lazy Loading Throughout
**Why?**
- Don't load/embed until needed
- Faster startup time
- Memory efficient
- Properties trigger initialization automatically

**Example flow**:
```
User calls search() 
  → Needs index_documents
    → Needs split_documents
      → Needs documents
        → Loads markdown files
      → Splits into chunks
    → Needs vector_store
      → Needs embeddings
        → Initializes Ollama
      → Creates InMemoryVectorStore
    → Indexes all chunks
  → Performs similarity search
```

### 2. Auto-Indexing on Search
```python
if not self._document_ids:
    self.index_documents
```
**Why?**
- Convenience - don't need separate index step
- Ensures index exists before searching
- One-time cost on first search

**Tradeoff**: First search is slower (indexing overhead)

### 3. Metadata Tracking
```python
metadata={"source": str(md_file)}
```
**Why?**
- Citations - tell user where info came from
- Debugging - know which doc was retrieved
- Trust - users can verify information

## Interview Talking Points

### On RAG vs Fine-Tuning
"RAG is often better for business use cases because:
1. Fresh data - update knowledge base without retraining
2. Lower cost - no GPU hours for training
3. Transparency - can cite sources
4. Domain flexibility - swap knowledge bases easily
5. Faster iteration - add documents vs retrain models"

### On Chunking Strategy
"I chose 1000 character chunks with 200 char overlap using RecursiveCharacterTextSplitter. This balances precision and context - chunks are small enough for focused retrieval but large enough to maintain meaning. The overlap prevents information loss at chunk boundaries. RecursiveCharacterTextSplitter respects markdown structure, which is important for our documentation."

### On Vector Store Choice
"I used InMemoryVectorStore for simplicity and demo purposes. It's fast, reliable, and has no external dependencies. The tradeoff is that the index rebuilds on every app restart. In production, I'd use ChromaDB or Pinecone for persistence, but for a take-home interview, simplicity wins."

### On Search Parameters
"I set k=2 for retrieval - this returns the two most semantically similar chunks. More chunks risk overwhelming the context window and adding noise. Fewer chunks risk missing relevant info. 2 is a sweet spot for focused, high-quality retrieval. This also helps with the 500-character truncation in the tool - we get the most relevant excerpts."

### On Semantic Search
"The vector store uses cosine similarity to find semantically similar content. When a user asks 'how do I deploy?', it matches documents about deployment even if they don't contain the exact word 'deploy'. This is way better than keyword search - it understands meaning and intent."

## Common Interview Questions

**Q: Why RecursiveCharacterTextSplitter?**
A: "It splits text recursively on natural boundaries - paragraphs, then sentences, then words. This preserves semantic meaning better than naive character splitting. For markdown documentation, this maintains structure like code blocks and lists intact."

**Q: What if a user query needs more than k=2 chunks?**
A: "Good question. I chose k=2 to keep context focused, but it's parameterizable. In production, I'd experiment with different k values and potentially use MMR (Maximal Marginal Relevance) to get diverse but relevant chunks. Could also implement adaptive k based on query complexity."

**Q: How would you handle documents in different formats?**
A: "I'd use LangChain's document loaders - DirectoryLoader with different parsers. PDFs via PyPDFLoader, DOCx via Docx2txtLoader, etc. All get converted to Document objects with metadata, then follow the same splitting/embedding pipeline."

**Q: How do embeddings work?**
A: "The embedding model (llama3.2 in this case) converts text into high-dimensional vectors - think of it as coordinates in semantic space. Similar meaning = nearby vectors. The vector store uses cosine similarity to find which document vectors are closest to the query vector. This enables semantic search."

## Performance Considerations

**Current bottlenecks**:
1. Indexing on first search (one-time cost)
2. Embedding generation (depends on Ollama speed)
3. No caching of search results

**Production improvements**:
- Persistent vector store (pre-index documents)
- Batch embedding for faster indexing
- Cache frequent queries
- Async embedding generation
- Metadata filtering for faster search
