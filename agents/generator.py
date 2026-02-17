
from typing import Literal
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command

from config import get_model
from state import AgentState

def generate(state: AgentState) -> Command[Literal["__end__", "generator"]]:
    """
    Generator Agent:
    Synthesizes an answer using retrieved docs.
    Performs a hallucination check.
    """
    messages = state["messages"]
    docs = state.get("retrieved_docs", [])
    config = state.get("config", {})
    
    # 1. Generate Answer
    model = get_model(config)
    
    context_str = "\n\n".join(docs)
    system_prompt = (
        "You are a MakTek support agent. Use the following context to answer the user's question.\n"
        f"Context:\n{context_str}\n"
        "If the answer is not in the context, say 'I don't know' or ask to escalate."
    )
    
    # We construct a temporary message list for generation that includes the system prompt + context
    generation_messages = [("system", system_prompt)] + messages
    
    response = model.invoke(generation_messages)
    answer = response.content
    
    # 2. Hallucination/Consistency Check (Self-Correction Loop)
    # Check if the answer relies on info not in docs.
    # Again, a real implementation would use a grader LLM.
    # Here, a simple heuristic: if the model says "I don't know" despite having docs, 
    # we might want to try again with a different prompt, or just accept it.
    # Let's simulate a check: if the answer is completely empty or too short, retry.
    
    if len(answer.strip()) < 5:
        print(" [SYSTEM] Hallucination Check Failed (Too short) -> Retrying Generator")
        return Command(
            goto="generator",
            # internal counter could be added to state to prevent infinite loops
        )

    return Command(
        update={"messages": [AIMessage(content=answer)]},
        goto="__end__"
    )
