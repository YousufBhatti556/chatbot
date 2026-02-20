
from typing import Literal
from langgraph.types import Command
from langchain_core.messages import AIMessage
from state import AgentState

def intent_detector(state: AgentState) -> Command[Literal["summarizer", "__end__"]]:
    """
    Intent Detector Agent:
    Classifies the user's input into:
    - Greeting: Responds immediately.
    - Abusive: Responds with a warning/refusal.
    - Other: Passes through to the main flow (Summarizer -> Supervisor).
    """
    messages = state["messages"]
    if not messages:
        return Command(goto="__end__")
        
    last_msg = messages[-1]
    user_input = last_msg.content.lower().strip()
    
    # 1. Check for Abusive/Harsh Language
    abusive_keywords = [
        "stupid", "idiot", "dumb", "hate you", "shut up", "useless", "fuck", "shit", "bitch", "asshole"
    ]
    if any(word in user_input for word in abusive_keywords):
        fallback_response = (
            "I'm here to help you, but I expect respectful communication. "
            "Please refrain from using offensive language so we can solve your issue constructively."
        )
        return Command(
            update={"messages": [AIMessage(content=fallback_response)]},
            goto="__end__"
        )
        
    # 2. Check for Greetings
    greeting_keywords = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    # Exact match or starts with greeting (to avoid triggering on "hi there, my phone is broken")
    # But for "smarter" feel, we might want to catch just "hi" separately.
    # If the user says "Hi, I have a problem", we should probably handle the problem (Pass through).
    # If the user JUST says "Hi", we greet back.
    
    is_pure_greeting = user_input in greeting_keywords
    
    if is_pure_greeting:
        greeting_response = "Hello! How can I assist you with MakTek support today?"
        return Command(
            update={"messages": [AIMessage(content=greeting_response)]},
            goto="__end__"
        )
        
    # 3. Default: Pass to Main Flow
    # We go to 'summarizer' aimed at preserving the original entry point logic
    return Command(goto="summarizer")
