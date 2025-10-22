import threading
from typing import List, Optional
from controller import Controller


class App:
    _is_running: bool = False
    _run_thread: threading.Thread = None

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
        self.controller = Controller(
            agent_folder=agent_folder,
            agent_name=agent_name,
            tools=tools,
            provider_name=provider_name,
            model_name=model_name,
            base_path=base_path,
            extra_files=extra_files,
        )
        self._run_thread = threading.Thread(target=self._run_app)

    @property
    def is_running(self) -> bool:
        return self._is_running

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
        self.controller.stream(user_input)

    def _run_app(self):
        # Send initial greeting
        self.controller.stream(
            "Hello! Please introduce yourself and tell me how you can help."
        )

        # Start the main conversation loop
        while self.is_running:
            user_input = self.get_user_input()
            self._handle_request(user_input)
