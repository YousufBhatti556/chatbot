
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import SystemMessage, RemoveMessage

from state import AgentState
from config import get_model
from agents.supervisor import supervisor
from agents.retriever import retrieve
from agents.generator import generate
from agents.escalator import escalate
from agents.intent import intent_detector

# Connect to a persistent SQLite DB for long-term memory mock (or actual InMemoryStore use)
# For this task, we use InMemoryStore as requested for "Long-Term" (though technically ephemeral without persistence)
# and MemorySaver for "Short-term".

def summarize_conversation(state: AgentState):
    """
    Middleware: Summarizes the conversation if it gets too long.
    Prunes old messages to save tokens.
    """
    messages = state["messages"]
    summary = state.get("summary", "")
    
    # Threshold for summarization
    if len(messages) > 6:
        config = state.get("config", {})
        model = get_model(config)
        
        # Create a summarization prompt
        # We need to act on the *current* state of messages
        
        prompt = (
            f"Previous summary: {summary}\n\n"
            "New lines of conversation:\n" + 
            "\n".join([m.content for m in messages if hasattr(m, 'content')]) + 
            "\n\nSummarize the conversation so far, retaining key details for customer support."
        )
        
        new_summary_msg = model.invoke([SystemMessage(content=prompt)])
        new_summary = new_summary_msg.content
        
        # Logic to remove old messages and keep only the last 2 + summary
        # We use RemoveMessage to delete from the graph state
        delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
        
        print(f" [SYSTEM] Summarization triggered. New Summary: {new_summary[:50]}...")
        
        return {
            "summary": new_summary,
            "messages": delete_messages
        }
    
    return {}

def build_graph():
    builder = StateGraph(AgentState)
    
    # 1. Add Nodes
    builder.add_node("supervisor", supervisor)
    builder.add_node("retriever", retrieve)
    builder.add_node("generator", generate)
    builder.add_node("escalator", escalate)
    builder.add_node("summarizer", summarize_conversation)
    builder.add_node("intent_detector", intent_detector)

    # 2. Add Edges
    # Start at Intent Detector
    builder.add_edge(START, "intent_detector")
    
    # Intent Detector -> Summarizer (if not end)
    # The Intent Detector uses Command to go to __end__ or summarizer
    # But we need to define the implicit edge for clarity/visualization if using conditional logic outside Command
    # With Command, we just ensure nodes exist.
    
    builder.add_edge("summarizer", "supervisor")
    
    # The Supervisor uses Command to go to other nodes, so we don't need explicit conditional_edges here
    # but we do need to register the possible destinations if using old style. 
    # With Command, we just need nodes to be added.
    
    # Implicit logic:
    # Supervisor -> Retriever or Escalator
    # Retriever -> Generator or Escalator
    # Generator -> END (or loop back)
    # Escalator -> END

    # 3. Setup Memory
    memory = MemorySaver()
    store = InMemoryStore() # Can be used to store user preferences
    
    return builder.compile(checkpointer=memory, store=store)

app = build_graph()
