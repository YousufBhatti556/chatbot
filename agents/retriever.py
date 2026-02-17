
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import Command
from state import AgentState
from vector_store import get_retriever

def retrieve(state: AgentState) -> Command[Literal["generator", "escalator"]]:
    """
    Retriever Agent:
    Retrieves documents based on the latest user query.
    Performs a self-check on relevance.
    """
    latest_message = state["messages"][-1]
    query = latest_message.content
    
    retriever = get_retriever()
    if not retriever:
        # Fallback if vector store fails
        return Command(
            update={"retrieved_docs": []},
            goto="escalator"
        )
        
    docs = retriever.invoke(query)
    
    # Simple Relevance Check (Self-Correction Loop)
    # in a real system, you might use an LLM or cross-encoder to score relevance.
    # Here, we'll check if we got any docs and if the query is strictly out of domain.
    # For demo purposes, let's say queries about "weather" are irrelevant to MakTek.
    if not docs or "weather" in query.lower():
        print(" [SYSTEM] Relevance Check Failed -> Escalating")
        return Command(
            update={"retrieved_docs": []},
            goto="escalator"
        )

    print(f" [SYSTEM] Retrieved {len(docs)} documents.")
    return Command(
        update={"retrieved_docs": [d.page_content for d in docs]},
        goto="generator"
    )
