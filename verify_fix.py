
import os
# Ensure the environment variable is set if needed, though usually not required if tf-keras is present and transformers detects it, 
# but sometimes explicit setting helps.
# os.environ["TF_USE_LEGACY_KERAS"] = "1" 

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("Successfully imported HuggingFaceEmbeddings")
    
    print("Initializing embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Successfully initialized HuggingFaceEmbeddings")
except Exception as e:
    print(f"Failed to initialize: {e}")
