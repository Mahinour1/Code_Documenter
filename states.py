from typing_extensions import List, TypedDict
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
  messages: Annotated[list, add_messages]