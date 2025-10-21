import os
import threading
from typing import Optional, Dict
from workflow_manager import WorkflowManager
from agent import Agent


class App:
    _is_running: bool = False
    _run_thread: threading.Thread = None
    _workflow_manager: Optional[WorkflowManager] = None
    _agent: Optional[Agent] = None

    def __init__(
        self, system_prompt_path: str = "docs/system_prompt.md", agent_name: str = "Bot"
    ):
        self._default_system_prompt = "You are a helpful assistant."
        self.system_prompt_path = system_prompt_path
        self.agent_name = agent_name
        self._run_thread = threading.Thread(target=self._run_app)

    @property
    def system_prompt(self) -> str:
        if not os.path.exists(self.system_prompt_path):
            return self._default_system_prompt
        with open(self.system_prompt_path, "r") as f:
            return f.read()

    @property
    def agent(self) -> Agent:
        if self._agent is None:
            self._agent = Agent(name=self.agent_name, system_prompt=self.system_prompt)
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

    def _handle_request(self, user_input: str) -> Optional[Dict]:
        if user_input.lower() in {"exit", "quit"}:
            self.quit()
            return None
        return self.workflow_manager.invoke(user_input)

    def _handle_response(self, response: Optional[Dict]) -> Optional[str]:
        if response is None:
            return None
        messages = response["messages"]
        message = messages[-1]
        return message.content

    def _display_response(self, content: str):
        print(f"{self.agent_name}: {content}")

    def _run_app(self):
        while self.is_running:
            user_input = self.get_user_input()
            response = self._handle_request(user_input)
            content = self._handle_response(response)
            if content is not None:
                self._display_response(content)
