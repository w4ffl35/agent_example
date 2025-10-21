from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.prompt_values import PromptValue


class Agent:
    _model = None
    _name: str = ""

    def __init__(
        self,
        system_prompt: str = "You are a helpful AI assistant.",
        model_name: str = "gemma3",
        model_provider: str = "ollama",
        name: str = "Bot",
    ):
        self._system_prompt = system_prompt
        self._model_name = model_name
        self._model_provider = model_provider
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def model(self):
        if self._model is None:
            self._model = init_chat_model(
                self._model_name, model_provider=self._model_provider
            )
        return self._model

    def invoke(self, prompt: PromptValue) -> AIMessage:
        return self.model.invoke(prompt)

    def stream(self, prompt: PromptValue):
        return self.model.stream(prompt)
