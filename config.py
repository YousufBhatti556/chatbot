
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

def get_model(config: dict):
    model_name = config.get("configurable", {}).get("model", "llama-3.1-8b-instant")
    
    if "gpt" in model_name:
        return ChatOpenAI(model=model_name, temperature=0)
    elif "claude" in model_name:
        return ChatAnthropic(model=model_name, temperature=0)
    elif "gemini" in model_name:
        return ChatGoogleGenerativeAI(model=model_name, temperature=0)
    elif "llama" in model_name or "mixtral" in model_name:
        return ChatGroq(model=model_name, temperature=0)
    else:
        # Default to Groq Llama 3.1 8B if unknown (Fast & Free)
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Mock environment setup for demonstration if keys are missing
if not os.environ.get("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not set. Using mock/placeholder if needed.")

DEFAULT_SYSTEM_PROMPT = """You are a helpful customer support assistant for MakTek.
Use the retrieved context to answer the user's questions.
If you are unsure, ask for clarification or escalate to a human agent.
"""
