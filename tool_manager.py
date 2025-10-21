from typing import Optional, Callable
from langchain.tools import tool
from rag_manager import RAGManager


class ToolManager:
    _rag_manager: Optional[RAGManager] = None

    def __init__(self, rag_directory: str, provider_name: str, model_name: str):
        self.rag_directory = rag_directory
        self.provider_name = provider_name
        self.model_name = model_name

    @property
    def rag_manager(self) -> RAGManager:
        if self._rag_manager is None:
            self._rag_manager = RAGManager(
                provider_name=self.provider_name,
                model_name=self.model_name,
                rag_directory=self.rag_directory,
            )
        return self._rag_manager

    def retrieve_context_tool(self) -> Callable:
        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str) -> tuple[str, list]:
            """Retrieve information from the knowledge base to help answer a query."""
            rag_manager = self.rag_manager
            retrieved_docs = rag_manager.search(query, k=2)

            if not retrieved_docs:
                return "No relevant information found in the knowledge base.", []

            serialized = "\n\n".join(
                f"Source: {doc.metadata.get('source', 'unknown')}\nContent: {doc.page_content}"
                for doc in retrieved_docs
            )

            return serialized, retrieved_docs

        return retrieve_context
