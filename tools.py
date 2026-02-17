
from langchain_core.tools import tool

@tool
def create_support_ticket(issue: str, user_id: str):
    """Creates a tracking ticket for a customer issue."""
    # In a real app, this would call an API (Jira, Zendesk, etc.)
    ticket_id = f"TICKET-{hash(issue) % 10000}"
    print(f" [SYSTEM] Ticket created: {ticket_id} for User {user_id} regarding: {issue}")
    return f"Support ticket #{ticket_id} has been created for your issue."
