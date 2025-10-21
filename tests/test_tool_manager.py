import tempfile
from pathlib import Path
from typing import Dict, List
import unittest
from functools import wraps
from tests.base_test_case import BaseTestCase
from tool_manager import ToolManager


def with_tool_manager(func):
    """Decorator that provides a ToolManager instance with a temporary directory."""

    @wraps(func)
    def wrapper(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_manager = ToolManager(
                rag_directory=tmpdir,
                provider_name="ollama",
                model_name="llama3.2",
            )
            return func(self, tool_manager, tmpdir)

    return wrapper


class TestToolManager(BaseTestCase):
    target_class = ToolManager
    public_methods = ["retrieve_context_tool"]
    public_properties = ["rag_manager"]
    _setup_kwargs = {
        "provider_name": "ollama",
        "model_name": "llama3.2",
    }

    @with_tool_manager
    def test_tool_manager_initialization(self, tool_manager, tmpdir):
        self.assertEqual(tool_manager.rag_directory, tmpdir)

    @with_tool_manager
    def test_retrieve_context_tool_creation(self, tool_manager, tmpdir):
        retrieve_context = tool_manager.retrieve_context_tool()
        self.assertIsNotNone(retrieve_context)
        self.assertTrue(hasattr(retrieve_context, "invoke"))

    @with_tool_manager
    def test_rag_manager_property(self, tool_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# Test\n\nTest content.")

        rag_manager = tool_manager.rag_manager

        self.assertIsNotNone(rag_manager)
        self.assertGreater(len(rag_manager.documents), 0)
        self.assertGreater(len(rag_manager.split_documents), 0)

    @with_tool_manager
    def test_retrieve_context_search(self, tool_manager, tmpdir):
        test_file = Path(tmpdir) / "test.md"
        test_file.write_text("# LangChain\n\nLangChain is a framework.")

        rag_manager = tool_manager.rag_manager
        results = rag_manager.search("LangChain", k=1)

        self.assertGreater(len(results), 0)
        self.assertIn("LangChain", results[0].page_content)

    @with_tool_manager
    def test_retrieve_context_no_documents(self, tool_manager, tmpdir):
        rag_manager = tool_manager.rag_manager

        self.assertEqual(len(rag_manager.documents), 0)


if __name__ == "__main__":
    unittest.main()
