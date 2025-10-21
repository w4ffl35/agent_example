from typing import Optional, List, Type
from pathlib import Path
from langchain_core.vectorstores import VectorStore, InMemoryVectorStore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain.embeddings import init_embeddings


class RAGManager:
    _embeddings: Optional[Embeddings] = None
    _vector_store: Optional[VectorStore] = None
    _documents: Optional[List[Document]] = None
    _split_documents: Optional[List[Document]] = None
    _document_ids: Optional[List[str]] = None

    def __init__(
        self,
        provider_name: str,
        model_name: str,
        rag_directory: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        vector_store_class: Type[VectorStore] = InMemoryVectorStore,
        extra_files: Optional[List[str]] = None
    ):
        """
        :param provider_name: The name of the embedding provider.
        :param model_name: The name of the Ollama model to use for embeddings.
        :param rag_directory: The directory containing markdown files for RAG.
        :param chunk_size: The size of each text chunk in characters for indexing.
        :param chunk_overlap: The number of overlapping characters between chunks.
        :param vector_store_class: The vector store class to use for storing embeddings.
        """
        self.provider_name = provider_name
        self.model_name = model_name
        self.rag_directory = rag_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store_class_ = vector_store_class
        self.extra_files = extra_files or []

    @property
    def embeddings(self) -> Embeddings:
        if self._embeddings is None:
            self._embeddings = init_embeddings(
                f"{self.provider_name}:{self.model_name}"
            )
        return self._embeddings

    @property
    def vector_store(self) -> Type[VectorStore]:
        if self._vector_store is None:
            self._vector_store = self.vector_store_class_(self.embeddings)
        return self._vector_store

    @property
    def text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Splits text into chunks for indexing.

        This could be improved with a more intelligent text splitter
        to ensure we are not cutting off important information.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            add_start_index=True,
        )

    @property
    def rag_path(self) -> Path:
        return Path(self.rag_directory)

    @property
    def documents(self) -> List[Document]:
        if self._documents is None:
            self._documents = self._load_markdown_documents()
            self._documents.extend(
                self._load_extra_files()
            )
        return self._documents

    @property
    def split_documents(self) -> List[Document]:
        """
        Splits the loaded documents into chunks for indexing.
        Returns the list of split documents.
        """
        if self._split_documents is None:
            self._split_documents = self.text_splitter.split_documents(self.documents)
        return self._split_documents

    @property
    def index_documents(self) -> List[str]:
        """
        Indexes the split documents into the vector store.
        Returns the list of document IDs.
        """
        if self._document_ids is None:
            self._document_ids = self.vector_store.add_documents(self.split_documents)
        return self._document_ids

    def _load_markdown_documents(self) -> List[Document]:
        return (
            [
                Document(
                    page_content=md_file.read_text(encoding="utf-8"),
                    metadata={"source": str(md_file)},
                )
                for md_file in self.rag_path.glob("**/*.md")
            ]
            if self.rag_path.exists()
            else []
        )

    def _load_extra_files(self) -> List[Document]:
        documents = []
        for file_path in self.extra_files:
            path = Path(file_path)
            if path.exists() and path.is_file():
                documents.append(
                    Document(
                        page_content=path.read_text(encoding="utf-8"),
                        metadata={"source": str(path)},
                    )
                )
        return documents

    def search(self, query: str, k: int = 2) -> List[Document]:
        """
        Searches the vector store for documents similar to the query.
        Automatically indexes documents if not already indexed.

        :param query: The search query.
        :param k: The number of results to return.
        :return: A list of the top k most similar documents.
        """
        # Ensure documents are indexed before searching
        _ = self.index_documents
        return self.vector_store.similarity_search(query, k=k)
