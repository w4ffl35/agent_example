import threading


class App:
    _is_running: bool = False
    _run_thread: threading.Thread

    def __init__(self):
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

    def _run_app(self):
        while self.is_running:
            user_input = self.get_user_input()
            if user_input.lower() in {"exit", "quit"}:
                self.quit()
