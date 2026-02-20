from typing import Literal
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command

from config import get_model
from state import AgentState
from db import load_recent_messages

def generate(state: AgentState) -> Command[Literal["__end__", "generator"]]:
    """
    Generator Agent:
    Synthesizes an answer combining:
    1. Short-term memory (LangGraph state)
    2. Long-term persistent memory (PostgreSQL)
    3. Semantic Memory (Pinecone retrieved docs)
    """
    messages = state["messages"]
    docs = state.get("retrieved_docs", [])
    config = state.get("config", {})
    user_id = state.get("user_info", {}).get("user_id", "default_user")
    thread_id = config.get("configurable", {}).get("thread_id", "default_thread")
    
    # Load past history from Postgres
    past_history = load_recent_messages(user_id, thread_id, limit=5)
    history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in past_history])
    if not history_str:
        history_str = "No recent history."
    
    # 1. Generate Answer
    model = get_model(config)
    
    context_str = "\n\n".join(docs) if docs else "No relevant semantic context found."
    
    system_prompt = (
        "You are a MakTek support agent. Use the provided context to answer the user's question.\n"
        f"--- Semantic Context (from Pinecone) ---\n{context_str}\n\n"
        f"--- Recent Persistent History (from PostgreSQL) ---\n{history_str}\n\n"
        "If the answer is not in the context, say 'I don't know' or ask to escalate."
    )
    
    # We construct a temporary message list for generation that includes the system prompt + current graph messages
    generation_messages = [("system", system_prompt)] + messages
    
    response = model.invoke(generation_messages)
    answer = response.content
    
    # 2. Hallucination/Consistency Check
    if len(answer.strip()) < 5:
        print(" [SYSTEM] Hallucination Check Failed (Too short) -> Retrying Generator")
        return Command(
            goto="generator",
        )

    return Command(
        update={"messages": [AIMessage(content=answer)]},
        goto="__end__"
    )
