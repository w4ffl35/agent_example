import os
import sys
from typing import List, Optional, Callable
from langchain_core.messages import AIMessage
from tool_manager import ToolManager
from agent import Agent
from workflow_manager import WorkflowManager


class Controller:
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
        temperature: float = 0.7,
    ):
        # Construct paths based on agent_folder
        self.agent_folder = agent_folder
        self.base_path = base_path
        self.agent_path = os.path.join(base_path, agent_folder)
        self.system_prompt_path = os.path.join(self.agent_path, "system_prompt.md")
        self.knowledge_directory = os.path.join(self.agent_path, "knowledge")
        self.extra_files = extra_files or []
        self.temperature = temperature

        self.tool_manager = ToolManager(
            rag_directory=self.knowledge_directory,
            provider_name=provider_name,
            model_name=model_name,
            extra_files=self.extra_files,
        )
        self._tools = tools
        self._default_system_prompt = "You are a helpful assistant."
        self.agent_name = agent_name
        self._provider_name = provider_name
        self._model_name = model_name

    @property
    def tools(self) -> List[Callable]:
        """
        Defaults to RAG tool
        """
        return (
            self._tools
            if self._tools
            else [
                self.tool_manager.retrieve_context_tool(),
                self.tool_manager.employee_lookup_tool(),
                self.tool_manager.create_employee_profile_tool(),
            ]
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
                temperature=self.temperature,
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

    def stream(self, user_input: str):
        has_output = False
        for message in self.workflow_manager.stream(user_input):
            if isinstance(message, AIMessage) and message.content:
                if not has_output:
                    print(f"{self.agent_name}: ", end="", flush=True)
                    has_output = True
                sys.stdout.write(message.content)
                sys.stdout.flush()
        if has_output:
            print()

    def invoke(self, user_input: str) -> dict:
        return self.workflow_manager.invoke(user_input)
