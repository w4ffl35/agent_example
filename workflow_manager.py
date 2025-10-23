from typing import Any, Annotated, Optional, List
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode


class WorkflowState(TypedDict):
    """State schema for the workflow."""

    messages: Annotated[list[BaseMessage], add_messages]


class WorkflowManager:
    """
    Manages the LangGraph workflow for agent execution.
    """

    def __init__(
        self,
        system_prompt: str,
        model: Optional[ChatOllama],
        tools: Optional[List[callable]],
        max_tokens: int = 2000,
    ):
        self._system_prompt = system_prompt
        self._model = model
        self._tools = tools
        self._max_tokens = max_tokens
        self._token_counter = lambda msgs: count_tokens_approximately(msgs)
        self._memory = MemorySaver()
        self._thread_id = "default"

        # Build the graph
        self._workflow = self._build_graph()
        self._compiled_workflow = self._workflow.compile(checkpointer=self._memory)

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("model", self._call_model)
        if self._tools:
            workflow.add_node("tools", ToolNode(self._tools))

        # Add edges
        workflow.add_edge(START, "model")

        if self._tools:
            workflow.add_conditional_edges(
                "model",
                self._route_after_model,
                {
                    "tools": "tools",
                    "end": END,
                },
            )
            workflow.add_edge("tools", "model")
        else:
            workflow.add_edge("model", END)

        return workflow

    def _route_after_model(self, state: WorkflowState) -> str:
        """Route to tools if model made tool calls, otherwise end."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    def _call_model(self, state: WorkflowState) -> dict[str, Any]:
        """Call the model with trimmed message history."""
        # Trim messages to stay within token limit
        trimmed_messages = trim_messages(
            state["messages"],
            max_tokens=self._max_tokens,
            strategy="last",
            token_counter=self._token_counter,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

        # Build prompt with system message and conversation history
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        formatted_prompt = prompt.invoke({"messages": trimmed_messages})
        response = self._model.invoke(formatted_prompt)

        return {"messages": [response]}

    def clear_memory(self):
        """Clear the conversation memory/history."""
        self._memory = MemorySaver()
        self._compiled_workflow = self._workflow.compile(checkpointer=self._memory)

    def invoke(self, user_input: str) -> dict[str, Any]:
        """Invoke the workflow with user input."""
        input_messages = [HumanMessage(user_input)]
        config = {"configurable": {"thread_id": self._thread_id}}
        return self._compiled_workflow.invoke({"messages": input_messages}, config)

    def stream(self, user_input: str):
        """Stream the workflow execution with user input."""
        input_messages = [HumanMessage(user_input)]
        config = {"configurable": {"thread_id": self._thread_id}}

        for event in self._compiled_workflow.stream(
            {"messages": input_messages},
            config,
            stream_mode="messages",
        ):
            message = event[0]
            if isinstance(message, AIMessage) and message.content:
                yield message
