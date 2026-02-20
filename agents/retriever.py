from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import Command
from state import AgentState
from vector_store import retrieve_similar_context

def retrieve(state: AgentState) -> Command[Literal["generator", "escalator"]]:
    """
    Retriever Agent:
    Retrieves semantic documents from Pinecone based on the latest user query.
    """
    latest_message = state["messages"][-1]
    query = latest_message.content
    
    user_id = state.get("user_info", {}).get("user_id", "default_user")
    
    docs = retrieve_similar_context(user_id, query)
    
    # Simple Relevance Check
    if not docs and "weather" in query.lower():
        print(" [SYSTEM] Relevance Check Failed -> Escalating")
        return Command(
            update={"retrieved_docs": []},
            goto="escalator"
        )

    print(f" [SYSTEM] Retrieved {len(docs)} documents from Pinecone Semantic Memory.")
    return Command(
        update={"retrieved_docs": docs},
        goto="generator"
    )
