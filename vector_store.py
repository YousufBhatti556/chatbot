
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from datasets import load_dataset
import os

def build_vector_store():
    print("*************** BUILDING VECTOR STORE START ***************")
    # Load real dataset from Hugging Face
    try:
        print(" [SYSTEM] Loading dataset 'MakTek/Customer_support_faqs_dataset'...")
        dataset = load_dataset("MakTek/Customer_support_faqs_dataset")
        
        # Assuming the dataset has a 'train' split and 'question'/'answer' columns
        data = dataset['train']
        
        docs = []
        for item in data:
            # Flexible handling if keys differ, but user said 'question' and 'answer' exist
            q = item.get("question", "")
            a = item.get("answer", "")
            if q and a:
                docs.append(
                    Document(
                        page_content=f"Q: {q}\nA: {a}",
                        metadata={"source": "MakTek_HF_Dataset"}
                    )
                )
        
        print(f" [SYSTEM] Indexed {len(docs)} documents from dataset.")
    except Exception as e:
        print(f" [ERROR] Failed to load dataset: {e}")
        # Fallback to a tiny mock set just to prevent crash if internet/auth fails
        docs = [
           Document(page_content="Q: Support\nA: Contact us at support@maktek.com", metadata={"source": "fallback"}) 
        ]

    # Use HuggingFace Embeddings (Free, runs locally)
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        
        print(" [SYSTEM] Initializing HuggingFace Embeddings (PyTorch)...")
        # Explicitly suggest torch if possible, though handled by library
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print(" [SYSTEM] Embeddings initialized successfully.")
        vectorstats = FAISS.from_documents(docs, embeddings)
        print(" [SYSTEM] FAISS vector store created.")
        print("*************** BUILDING VECTOR STORE SUCCESS ***************")
        return vectorstats.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        print(f"*************** ERROR initializing FAISS: {e} ***************")
        return None

# Singleton-ish pattern for the retriever
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = build_vector_store()
    return _retriever
