import tempfile
import os
from pathlib import Path
from functools import wraps
from tests.base_test_case import BaseTestCase
from rag_manager import RAGManager
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document


def with_temp_rag(func):
    """Decorator that provides a RAGManager instance with a temporary directory."""

    @wraps(func)
    def wrapper(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmpdir:
            rag_manager = RAGManager(
                provider_name="ollama",
                model_name="llama3.2",
                rag_directory=tmpdir,
                **kwargs
            )
            return func(self, rag_manager, tmpdir)

    return wrapper


class TestRAGManager(BaseTestCase):
    target_class = RAGManager
    _setup_args = ["ollama", "llama3.2", "docs/rag"]
    public_properties = [
        "vector_store",
        "embeddings",
        "text_splitter",
        "documents",
        "rag_path",
        "split_documents",
        "index_documents",
    ]
    public_methods = ["search"]

    def test_embeddings_type(self):
        self.assertIsInstance(self.obj.embeddings, OllamaEmbeddings)

    def test_vector_store_type(self):
        self.assertIsInstance(self.obj.vector_store, InMemoryVectorStore)

    def test_default_rag_directory(self):
        rag_manager = RAGManager(
            provider_name="ollama", model_name="llama3.2", rag_directory="docs/rag"
        )
        self.assertEqual(rag_manager.rag_directory, "docs/rag")

    def test_custom_rag_directory(self):
        rag_manager = RAGManager(
            provider_name="ollama", model_name="llama3.2", rag_directory="custom/path"
        )
        self.assertEqual(rag_manager.rag_directory, "custom/path")

    def test_default_chunk_size(self):
        rag_manager = RAGManager(
            provider_name="ollama", model_name="llama3.2", rag_directory="docs/rag"
        )
        self.assertEqual(rag_manager.chunk_size, 1000)

    def test_custom_chunk_size(self):
        rag_manager = RAGManager(
            provider_name="ollama",
            model_name="llama3.2",
            rag_directory="docs/rag",
            chunk_size=500,
        )
        self.assertEqual(rag_manager.chunk_size, 500)

    @with_temp_rag
    def test_load_documents_empty_directory(self, rag_manager, tmpdir):
        docs = rag_manager.documents
        self.assertEqual(len(docs), 0)

    @with_temp_rag
    def test_load_documents_with_markdown(self, rag_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is a test.")

        docs = rag_manager.documents

        self.assertGreater(len(docs), 0)
        self.assertIsInstance(docs[0], Document)

    @with_temp_rag
    def test_split_documents(self, rag_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# Test\n\n" + "word " * 500)

        # Need to recreate with custom chunk settings
        rag_manager = RAGManager(
            provider_name="ollama",
            model_name="llama3.2",
            rag_directory=tmpdir,
            chunk_size=100,
            chunk_overlap=20,
        )
        splits = rag_manager.split_documents

        self.assertGreater(len(splits), 1)
        self.assertIsInstance(splits[0], Document)

    @with_temp_rag
    def test_index_documents(self, rag_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is a test.")

        document_ids = rag_manager.index_documents

        self.assertGreater(len(document_ids), 0)
        self.assertIsInstance(document_ids[0], str)

    @with_temp_rag
    def test_search(self, rag_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# LangChain\n\nLangChain is a framework.")

        rag_manager.index_documents

        results = rag_manager.search("LangChain", k=1)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], Document)

    @with_temp_rag
    def test_documents_property(self, rag_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# Test")

        self.assertGreater(len(rag_manager.documents), 0)

    @with_temp_rag
    def test_split_documents_returns_splits(self, rag_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# Test\n\n" + "word " * 500)

        # Need to recreate with custom chunk settings
        rag_manager = RAGManager(
            provider_name="ollama",
            model_name="llama3.2",
            rag_directory=tmpdir,
            chunk_size=100,
            chunk_overlap=20,
        )

        self.assertGreater(len(rag_manager.split_documents), 0)
