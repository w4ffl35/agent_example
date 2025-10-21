from typing import List, Callable
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from langchain_core.prompt_values import PromptValue


class Agent:
    _model = None
    _name: str = ""

    def __init__(
        self,
        system_prompt: str = "You are a helpful AI assistant.",
        model_name: str = "llama3.2",
        model_provider: str = "ollama",
        name: str = "Bot",
        tools: List[Callable] = None,
        temperature: float = 0.7,
    ):
        self._system_prompt = system_prompt
        self._model_name = model_name
        self._model_provider = model_provider
        self._name = name
        self._tools = tools or []
        self._temperature = temperature

    @property
    def tools(self) -> List[Callable]:
        return self._tools

    @property
    def name(self) -> str:
        return self._name

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def model(self):
        if self._model is None:
            base_model = ChatOllama(
                model=self._model_name, temperature=self._temperature
            )
            # Bind tools if provided
            if self._tools:
                self._model = base_model.bind_tools(self._tools)
            else:
                self._model = base_model
        return self._model

    def invoke(self, prompt: PromptValue) -> AIMessage:
        return self.model.invoke(prompt)

    def stream(self, prompt: PromptValue):
        return self.model.stream(prompt)
