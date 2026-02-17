
from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.types import Command

from tools import create_support_ticket
from state import AgentState

def escalate(state: AgentState) -> Command[Literal["__end__"]]:
    """
    Escalator Agent:
    Creates a support ticket and informs the user.
    """
    messages = state["messages"]
    last_user_msg = messages[-1]
    user_id = state.get("user_info", {}).get("user_id", "guest")
    
    print(" [SYSTEM] Escalating to human agent...")
    
    # Invoke the tool
    ticket_result = create_support_ticket.invoke({"issue": last_user_msg.content, "user_id": user_id})
    
    response_text = (
        f"I'm sorry I couldn't help with that. {ticket_result}\n"
        "A human agent will contact you shortly."
    )
    
    return Command(
        update={"messages": [AIMessage(content=response_text)]},
        goto="__end__"
    )
