from typing import Any, List, Optional, Tuple
from langgraph.graph.state import CompiledStateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from agent import Agent


class WorkflowManager:
    _workflow: Optional[StateGraph] = None
    _memory: Optional[MemorySaver] = None
    _agent: Optional[Agent] = None
    _compiled_workflow: Optional[CompiledStateGraph] = None
    _trimmer = None
    _tool_node: ToolNode = None
    _first_message: bool = True

    def __init__(self, agent: Optional[Agent] = None, max_tokens: int = 2000):
        self._agent = agent or Agent()
        self._max_tokens = max_tokens
        self._token_counter = lambda msgs: count_tokens_approximately(msgs)

        self._define_nodes()

    @property
    def tool_node(self) -> ToolNode:
        if self._tool_node is None:
            self._tool_node = ToolNode(self._agent.tools)
        return self._tool_node

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
    def workflow(self) -> StateGraph:
        if self._workflow is None:
            self._workflow = StateGraph(state_schema=MessagesState)
        return self._workflow

    @property
    def compiled_workflow(self) -> CompiledStateGraph:
        if self._compiled_workflow is None:
            self._compiled_workflow = self.workflow.compile(checkpointer=self.memory)
        return self._compiled_workflow

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
        return self.compiled_workflow.invoke({"messages": input_messages}, self.config)

    def stream(self, user_input: str):
        input_messages = [HumanMessage(user_input)]

        for event in self.compiled_workflow.stream(
            {"messages": input_messages}, self.config, stream_mode="messages"
        ):
            message = event[0]
            if isinstance(message, AIMessage) and message.content:
                yield message

    def _define_nodes(self):
        self.workflow.add_node("model", self._call_model)
        self.workflow.add_node("tools", self.tool_node)
        self.workflow.add_edge(START, "model")
        self.workflow.add_conditional_edges(
            "model", self._should_continue, {"tools": "tools", "end": END}
        )
        self.workflow.add_edge("tools", "model")

    def _call_model(self, state: MessagesState):
        trimmed_messages = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(
            {"messages": trimmed_messages, "name": self._agent.name}
        )
        response = self._agent.invoke(prompt)
        return {"messages": [response]}

    def _should_continue(self, state: MessagesState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
