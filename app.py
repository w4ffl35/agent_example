import os
import sys
import threading
from typing import List, Optional, Callable
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from tool_manager import ToolManager
from workflow_manager import WorkflowManager


class App:
    _is_running: bool = False
    _run_thread: threading.Thread = None
    _workflow_manager: Optional[WorkflowManager] = None
    _agent = None
    _model = None

    def __init__(
        self,
        system_prompt_path: str = "docs/system_prompt.md",
        agent_name: str = "Bot",
        tools: Optional[List[callable]] = None,
        provider_name: str = "ollama",
        model_name: str = "llama3.2",
        rag_directory: str = "docs/rag",
    ):
        self.tool_manager = ToolManager(
            rag_directory=rag_directory,
            provider_name=provider_name,
            model_name=model_name,
        )
        self._tools = tools
        self._default_system_prompt = "You are a helpful assistant."
        self.system_prompt_path = system_prompt_path
        self.agent_name = agent_name
        self._run_thread = threading.Thread(target=self._run_app)
        self._provider_name = provider_name
        self._model_name = model_name
        self.rag_directory = rag_directory

    @property
    def tools(self) -> List[Callable]:
        """
        Defaults to RAG tool
        """
        return (
            self._tools if self._tools else [self.tool_manager.retrieve_context_tool()]
        )

    @property
    def model(self):
        if self._model is None:
            self._model = ChatOllama(model=self._model_name, temperature=0)
        return self._model

    @property
    def system_prompt(self) -> str:
        if not os.path.exists(self.system_prompt_path):
            return self._default_system_prompt
        with open(self.system_prompt_path, "r") as f:
            return f.read()

    @property
    def agent(self):
        if self._agent is None:
            self._agent = create_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=self.system_prompt,
                name=self.agent_name,
            )
        return self._agent

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def workflow_manager(self) -> WorkflowManager:
        if self._workflow_manager is None:
            self._workflow_manager = WorkflowManager(agent=self.agent)
        return self._workflow_manager

    def run(self):
        self._is_running = True
        self._run_thread.start()

    def get_user_input(self) -> str:
        return input("User: ")

    def quit(self):
        self._is_running = False

    def join(self, timeout=None):
        """Wait for the app thread to finish."""
        if self._run_thread and self._run_thread.is_alive():
            self._run_thread.join(timeout=timeout)

    def _handle_request(self, user_input: str):
        if user_input.lower() in {"exit", "quit"}:
            self.quit()
            return
        print(f"{self.agent_name}: ", end="", flush=True)
        for chunk in self.workflow_manager.stream(user_input):
            if hasattr(chunk, "content"):
                sys.stdout.write(chunk.content)
                sys.stdout.flush()
        print()

    def _run_app(self):
        while self.is_running:
            user_input = self.get_user_input()
            self._handle_request(user_input)
