
from typing import Literal
from langgraph.types import Command
from state import AgentState

def supervisor(state: AgentState) -> Command[Literal["retriever", "escalator", "generator"]]:
    """
    Supervisor Agent:
    Orchestrates the flow. It decides whether to call the Retriever, Generator, or Escalator.
    It considers user intent based on the latest message.
    """
    messages = state["messages"]
    if not messages:
        return Command(goto="__end__")
        
    last_msg = messages[-1]
    user_input = last_msg.content.lower()
    
    # 1. Intent Classification
    # Check for direct escalation requests
    escalation_keywords = ["human", "agent", "support ticket", "escalate"]
    if any(keyword in user_input for keyword in escalation_keywords):
        return Command(goto="escalator")

    # Check for greetings (skip retrieval, go straight to generator or handle directly?)
    # For a RAG system seeking to be helpful, let's just retrieve anyway in case "Hi" is followed by a question in the same turn,
    # or just let the generator handle it if retrieval yields nothing.
    # However, to be robust, we'll try retrieval first for everything else.
    
    return Command(goto="retriever")
