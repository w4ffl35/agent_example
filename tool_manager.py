from typing import List, Optional, Callable
from langchain.tools import tool
from rag_manager import RAGManager
import json


class ToolManager:
    _rag_manager: Optional[RAGManager] = None

    def __init__(
        self,
        rag_directory: str,
        provider_name: str,
        model_name: str,
        extra_files: Optional[List[str]] = None,
    ):
        self.rag_directory = rag_directory
        self.provider_name = provider_name
        self.model_name = model_name
        self.extra_files = extra_files or []
        self.employee_db = "data/employee_db.json"

    @property
    def rag_manager(self) -> RAGManager:
        if self._rag_manager is None:
            self._rag_manager = RAGManager(
                provider_name=self.provider_name,
                model_name=self.model_name,
                rag_directory=self.rag_directory,
                extra_files=self.extra_files,
            )
        return self._rag_manager

    def retrieve_context_tool(self) -> Callable:
        @tool
        def retrieve_context(query: str) -> str:
            """Retrieve relevant information from the developer onboarding knowledge base.

            Use this tool ONLY when you need to look up specific technical information
            to answer the user's question. Do NOT use this for greetings or general chat.

            Args:
                query: A specific search query about what technical information you need

            Returns:
                Relevant documentation excerpts, or a message if nothing relevant was found.
            """
            rag_manager = self.rag_manager
            retrieved_docs = rag_manager.search(query, k=2)

            if not retrieved_docs:
                return "No relevant information found in the knowledge base."

            # Format results for the agent to use - keep it concise
            context_parts = []
            for i, doc in enumerate(retrieved_docs, 1):
                source = doc.metadata.get("source", "unknown")
                # Extract just the filename for cleaner output
                filename = source.split("/")[-1] if "/" in source else source
                # Limit content length to avoid overwhelming the model
                content = (
                    doc.page_content[:500] + "..."
                    if len(doc.page_content) > 500
                    else doc.page_content
                )
                context_parts.append(f"[From {filename}]\n{content}")

            return "\n\n".join(context_parts)

        return retrieve_context

    def employee_lookup_tool(self) -> Callable:
        @tool
        def employee_lookup(employee_name: str) -> str:
            """Lookup basic information about an employee.

            Args:
                employee_name: The full name of the employee to look up.

            Returns:
                A string with the employee's role and department, or a message if not found.
            """
            with open(self.employee_db, "r") as f:
                employee_directory = json.load(f)
                info = employee_directory.get(employee_name)
                if info:
                    return f"{employee_name} is a {info}."
            return f"No information found for employee: {employee_name}."

        return employee_lookup

    def create_employee_profile_tool(self) -> Callable:
        @tool
        def create_employee_profile(
            username: str, employee_name: str, role: str, department: str
        ) -> str:
            """Create a new employee profile in the directory.

            Args:
                username: The username of the new employee.
                employee_name: The full name of the employee.
                role: The role/title of the employee.
                department: The department the employee belongs to.

            Returns:
                A confirmation message.
            """
            # Read existing database
            try:
                with open(self.employee_db, "r") as f:
                    content = f.read().strip()
                    employee_db = json.loads(content) if content else {}
            except FileNotFoundError:
                employee_db = {}

            # Add new employee
            employee_db[employee_name] = {
                "username": username,
                "role": role,
                "department": department,
            }

            # Write back to file
            with open(self.employee_db, "w") as f:
                json.dump(employee_db, f, indent=4)

            return f"✓ Created profile for {username}: {employee_name}, Role: {role}, Department: {department}."

        return create_employee_profile
