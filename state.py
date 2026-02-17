
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: str
    retrieved_docs: List[str]
    config: Dict[str, Any]
    user_info: Dict[str, Any] # Store user preferences here
