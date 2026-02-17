
import os

# Suppress TensorFlow oneDNN custom operations warning
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import uuid
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from graph import app

# Ensure API key is set for testing
if not os.environ.get("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not set in .env. Please set it for Groq to work.")

def run_chat_loop():
    print("Initializing MakTek Support System...")
    
    # Simulate a user session
    thread_id = str(uuid.uuid4())
    user_id = "user_123"
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "model": "llama-3.1-8b-instant"
        }
    }
    
    print(f"Session started for User {user_id} (Thread: {thread_id})")
    print("Type 'quit' to exit.")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # Invoke the graph
        # We pass the user input as a new message
        # And user_info in the state
        inputs = {
            "messages": [HumanMessage(content=user_input)],
            "user_info": {"user_id": user_id},
            "config": config  # Pass config into state so nodes can access it
        }
        
        # Stream events or just get final state
        # For simplicity, we'll just print the final response from the assistant
        
        # We can use .stream() to see the steps
        print(" [Assistant is thinking...]")
        
        final_answer = ""
        for event in app.stream(inputs, config=config):
            for key, value in event.items():
                # Value is the state update
                # print(f"DEBUG: Node '{key}' finished.")
                if value and "messages" in value and value["messages"]:
                     # Check if it's an AI Message (generation)
                     last_msg = value["messages"][-1]
                     if hasattr(last_msg, "content") and last_msg.type == "ai":
                         final_answer = last_msg.content
        
        if final_answer:
            print(f"MakTek: {final_answer}")
        else:
             # Fallback if no final answer generated (e.g. escalation only or partial validation)
             # Logic needs to be robust to pull from state if stream didn't catch it
             # snapshot = app.get_state(config)
             pass

if __name__ == "__main__":
    run_chat_loop()
