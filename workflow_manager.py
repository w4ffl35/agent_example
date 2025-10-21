from typing import Any, List, Optional, Tuple
from langgraph.graph.state import CompiledStateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver


class WorkflowManager:
    _workflow: Optional[StateGraph] = None
    _memory: Optional[MemorySaver] = None
    _agent = None
    _compiled_workflow: Optional[CompiledStateGraph] = None
    _trimmer = None

    def __init__(self, agent, max_tokens: int = 2000):
        self._agent = agent
        self._max_tokens = max_tokens
        self._token_counter = lambda msgs: count_tokens_approximately(msgs)

    @property
    def trimmer(self):
        if self._trimmer is None:
            self._trimmer = trim_messages(
                max_tokens=self._max_tokens,
                strategy="last",
                token_counter=self._token_counter,
                include_system=True,
                allow_partial=False,
                start_on="human",
            )
        return self._trimmer

    @property
    def prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(self.messages)

    @property
    def memory(self) -> MemorySaver:
        if self._memory is None:
            self._memory = MemorySaver()
        return self._memory

    @property
    def messages(self) -> List[Tuple[str, str]]:
        return [
            ("system", self._agent.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]

    @property
    def config(self) -> dict[str, Any]:
        return {"configurable": {"thread_id": "1"}}

    def invoke(self, user_input: str) -> dict[str, Any]:
        input_messages = [HumanMessage(user_input)]
        return self._agent.invoke({"messages": input_messages}, self.config)

    def stream(self, user_input: str):
        input_messages = [HumanMessage(user_input)]
        for chunk in self._agent.stream(
            {"messages": input_messages}, self.config, stream_mode="messages"
        ):
            if isinstance(chunk, tuple) and len(chunk) >= 1:
                message = chunk[0]
                if isinstance(message, AIMessage) and message.content:
                    yield message
            elif isinstance(chunk, AIMessage) and chunk.content:
                yield chunk
