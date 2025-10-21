import os
import sys
import threading
from typing import List, Optional, Callable
from langchain_core.messages import AIMessage
from tool_manager import ToolManager
from agent import Agent
from workflow_manager import WorkflowManager


class App:
    _is_running: bool = False
    _run_thread: threading.Thread = None
    _agent = None
    _workflow_manager = None

    def __init__(
        self,
        agent_folder: str = "dev_onboarding",
        agent_name: str = "Bot",
        tools: Optional[List[callable]] = None,
        provider_name: str = "ollama",
        model_name: str = "llama3.2",
        base_path: str = "docs/rag",
        extra_files: Optional[List[str]] = None,
    ):
        # Construct paths based on agent_folder
        self.agent_folder = agent_folder
        self.base_path = base_path
        self.agent_path = os.path.join(base_path, agent_folder)
        self.system_prompt_path = os.path.join(self.agent_path, "system_prompt.md")
        self.knowledge_directory = os.path.join(self.agent_path, "knowledge")
        self.extra_files = extra_files or []

        self.tool_manager = ToolManager(
            rag_directory=self.knowledge_directory,
            provider_name=provider_name,
            model_name=model_name,
            extra_files=self.extra_files,
        )
        self._tools = tools
        self._default_system_prompt = "You are a helpful assistant."
        self.agent_name = agent_name
        self._run_thread = threading.Thread(target=self._run_app)
        self._provider_name = provider_name
        self._model_name = model_name

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
        """Access the underlying model from the agent."""
        return self.agent.model

    @property
    def agent(self):
        if self._agent is None:
            self._agent = Agent(
                model_name=self._model_name,
                system_prompt=self.system_prompt,
                tools=self.tools,
                name=self.agent_name,
                temperature=0.7,
            )
        return self._agent

    @property
    def workflow_manager(self):
        if self._workflow_manager is None:
            self._workflow_manager = WorkflowManager(agent=self.agent)
        return self._workflow_manager

    @property
    def system_prompt(self) -> str:
        if not os.path.exists(self.system_prompt_path):
            return self._default_system_prompt
        with open(self.system_prompt_path, "r") as f:
            return f.read()

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def config(self) -> dict:
        """Configuration for agent with memory thread_id."""
        return {"configurable": {"thread_id": "1"}}

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

    def _do_quit(self, user_input: str) -> bool:
        if user_input.lower() in {"exit", "quit"}:
            return True
        return False

    def _handle_request(self, user_input: str):
        if self._do_quit(user_input):
            self.quit()
            return
        self._stream_response(user_input)

    def _stream_response(self, user_input: str):
        print(f"{self.agent_name}: ", end="", flush=True)
        for message in self.workflow_manager.stream(user_input):
            if isinstance(message, AIMessage) and message.content:
                sys.stdout.write(message.content)
                sys.stdout.flush()
        print()

    def _run_app(self):
        self._stream_response("Send a friendly greeting to start the conversation.")
        while self.is_running:
            user_input = self.get_user_input()
            self._handle_request(user_input)
