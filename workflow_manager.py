from dataclasses import dataclass
import json
from typing import Any, List, Optional, Tuple
from langgraph.graph.state import CompiledStateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from agent import Agent


@dataclass
class User:
    username: str
    name: str
    role: str
    department: str


class WorkflowManager:
    _workflow: Optional[StateGraph] = None
    _memory: Optional[MemorySaver] = None
    _agent: Optional[Agent] = None
    _compiled_workflow: Optional[CompiledStateGraph] = None
    _trimmer = None
    _tool_node: ToolNode = None
    _first_message: bool = True
    _thread_id: str = "default"
    _is_logged_in: bool = False
    _user: Optional[User] = None

    def __init__(self, agent: Optional[Agent] = None, max_tokens: int = 2000):
        self._agent = agent or Agent()
        self._max_tokens = max_tokens
        self._token_counter = lambda msgs: count_tokens_approximately(msgs)
        self._is_new_user = True

        self._define_nodes()
        self._add_edges()

    @property
    def agent_has_tools(self) -> bool:
        return self._agent.tools is not None and len(self._agent.tools) > 0

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
        return {"configurable": {"thread_id": self._thread_id}}

    def clear_memory(self):
        """Clear the conversation memory/history."""
        self._memory = MemorySaver()
        self._compiled_workflow = None

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

        if self.agent_has_tools:
            self.workflow.add_node("tools", self.tool_node)
            self.workflow.add_node("login", self._login)
            self.workflow.add_node("onboarding", self._onboarding)

    def _add_edges(self):
        self.workflow.add_edge(START, "login")

        self.workflow.add_conditional_edges(
            "login",
            self._login_router,
            {
                "login": "login",
                "onboarding": "onboarding",
                "model": "model",
            },
        )

        # After onboarding, check if tools need to be called
        if self.agent_has_tools:
            self.workflow.add_conditional_edges(
                "onboarding",
                self._agent_router,
                {
                    "tools": "tools",
                    "end": "model",  # If no tools, go to model for greeting
                },
            )

            self.workflow.add_conditional_edges(
                "model",
                self._agent_router,
                {
                    "tools": "tools",
                    "end": END,
                },
            )
            # After tools execute, go back to model to process the result
            self.workflow.add_edge("tools", "model")
        else:
            self.workflow.add_edge("onboarding", "model")
            self.workflow.add_edge("model", END)

    def _call_model(self, state: MessagesState):
        trimmed_messages = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(
            {"messages": trimmed_messages, "name": self._agent.name}
        )
        response = self._agent.invoke(prompt)
        return {"messages": [response]}

    def _login(self, state: MessagesState):
        username = input("Enter username: ")
        password = input("Enter password: ")
        # Simulate login validation
        if username == "admin" and password == "password":
            self._is_logged_in = True
            with open("data/employee_db.json", "r") as f:
                try:
                    employee_db = json.load(f)
                except json.JSONDecodeError:
                    employee_db = {}
                for _name, data in employee_db.items():
                    if data.get("username") == username:
                        self._user = User(
                            username=username,
                            name=_name,
                            role=data.get("role"),
                            department=data.get("department"),
                        )
                        self._is_new_user = False
                        break
            if self._is_logged_in:
                print("Login successful!")
        else:
            print("Login failed. Please try again.")

    def _onboarding(self, state: MessagesState):
        print("Welcome to the system! Let's get you onboarded.")
        name = input("Enter your full name: ")
        role = input("Enter your role/title: ")
        department = input("Enter your department: ")
        username = "admin"  # Could prompt for this too

        self._user = User(
            username=username,
            name=name,
            role=role,
            department=department,
        )

        # Create a message that will trigger the create_employee_profile tool
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are helping onboard a new employee. You MUST use the create_employee_profile tool to save their information.",
                ),
                (
                    "user",
                    f"Create an employee profile with username '{username}', employee_name '{name}', role '{role}', and department '{department}'.",
                ),
            ]
        )

        response = self._agent.invoke(prompt.invoke({}))

        # Mark user as no longer new after onboarding
        self._is_new_user = False

        print(f"\n✓ Onboarding complete for {name}!")
        print("Saving profile and preparing your workspace...\n")

        # Add a follow-up message to prompt a proper welcome after tool execution
        # This will be processed after the tool runs
        welcome_request = HumanMessage(
            content=f"Onboarding complete! {name} (username: {username}, role: {role}, department: {department}) has just joined the team. Welcome them warmly and offer to help them get started with their development environment."
        )

        return {"messages": [response, welcome_request]}

    def _login_router(self, state: MessagesState) -> str:
        if not self._is_logged_in:
            return "login"
        if self._is_new_user:
            return "onboarding"
        return "model"

    def _agent_router(self, state: MessagesState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
