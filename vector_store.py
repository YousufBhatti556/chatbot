import os
import uuid
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings

# Globals
pc = None
index = None
embeddings = None

def init_pinecone():
    """Initializes Pinecone client and creates the index if it doesn't exist."""
    global pc, index, embeddings
    
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print(" [WARNING] PINECONE_API_KEY not set. Semantic memory will be disabled.")
        return
        
    index_name = os.getenv("PINECONE_INDEX_NAME", "chatbot-memory")
    
    try:
        print(" [SYSTEM] Initializing Pinecone...")
        pc = Pinecone(api_key=api_key)
        
        # HuggingFace Embeddings (all-MiniLM-L6-v2) outputs 384 dimensions
        dimension = 384 
        
        if index_name not in pc.list_indexes().names():
            print(f" [SYSTEM] Creating Pinecone index '{index_name}'...")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        index = pc.Index(index_name)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print(" [SYSTEM] Pinecone initialized successfully.")
    except Exception as e:
        print(f" [ERROR] Error initializing Pinecone: {e}")

def store_embedding(user_id, message_id, content, role):
    """Generates and stores an embedding for a message in Pinecone."""
    if not index or not embeddings:
        return
        
    try:
        # Generate embedding
        vector = embeddings.embed_query(content)
        
        # Prepare metadata
        metadata = {
            "user_id": user_id,
            "message_id": message_id,
            "role": role,
            "content": content,
            "timestamp": str(datetime.now())
        }
        
        # Upsert to Pinecone
        index.upsert(
            vectors=[{
                "id": message_id,
                "values": vector,
                "metadata": metadata
            }],
            namespace=user_id  # Use namespace to isolate user data
        )
    except Exception as e:
        print(f" [ERROR] Error storing embedding in Pinecone: {e}")

def retrieve_similar_context(user_id, query, top_k=3):
    """Retrieves semantically similar past messages for a user based on a query."""
    if not index or not embeddings:
        return []
        
    try:
        # Generate embedding for the query
        query_vector = embeddings.embed_query(query)
        
        # Search Pinecone in the user's namespace
        results = index.query(
            namespace=user_id,
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract the content from the matches
        context_docs = []
        for match in results.get("matches", []):
            if "metadata" in match and "content" in match["metadata"]:
                # Optionally prepend role (User/Assistant) to context
                role_str = str(match["metadata"].get("role", "unknown")).capitalize()
                content_str = match["metadata"]["content"]
                # E.g., User (past): ... or MakTek (past): ...
                context_docs.append(f"{role_str} (past): {content_str}")
                
        return context_docs
    except Exception as e:
        print(f" [ERROR] Error retrieving from Pinecone: {e}")
        return []

# Legacy wrapper so Retriever node doesn't completely break if it calls get_retriever()
# However, we will modify the Retriever node to use the new functions directly.
def get_retriever():
    return None
