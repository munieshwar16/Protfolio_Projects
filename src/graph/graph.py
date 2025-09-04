"""
LangGraph Orchestration
-----------------------
This file wires together all the agents (router, user, ticket,
clarifier, fallback, summarizer) into one chatbot workflow.
"""

from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, START, add_messages

# Import agents
from src.graph.router import router_logic  # Add this import
from src.agents.user_agent import user_agent
from src.agents.ticket_agent import ticket_agent
from src.agents.clarifier import clarifier
from src.agents.fallback_agent import fallback_agent
from src.agents.summarizer import summarizer



class BotMessage(TypedDict):
    role: str
    content: str


def merge_context(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Merge context dictionaries, with right taking precedence"""
    result = {}
    if left:
        result.update(left)
    if right:
        result.update(right)
    return result


class BotState(TypedDict):
    messages: Annotated[List[BotMessage], add_messages]
    context: Annotated[Dict[str, Any], merge_context]  # Added reducer to handle concurrent updates
    next_node: str 


async def router_node(state: BotState) -> Dict[str, Any]:
    """
    Router node that processes the message and returns state updates.
    """
    #print("[GRAPH DEBUG] Entering router_node with state:", state)
    dict_state = {
        "messages": state["messages"],
        "context": state.get("context", {})
    }
    updates = await router_logic(dict_state)
    #print("[GRAPH DEBUG] router_logic returned updates:", updates)
    
    # Get the intent and map it to the next node
    pending_intent = updates["context"]["pending_intent"]
    intent_to_agent = {
        "add_user": "user_agent",
        "list_users": "user_agent",  # Added this mapping
        "create_ticket": "ticket_agent", 
        "view_ticket": "ticket_agent",
        "update_status": "ticket_agent",
        "list_tickets": "ticket_agent",
        "delete_tickets": "ticket_agent",  # Added this mapping
        "unsupported": "fallback_agent",  # Changed from "__end__" to "fallback_agent"
    }
    
    # Set the next node based on the intent
    updates["next_node"] = intent_to_agent.get(pending_intent, "fallback_agent")
    
    #print("[GRAPH DEBUG] router_node returning updates:", updates)
    return updates  




def route_based_on_next_node(state: BotState) -> str:
    """
    Conditional edge function that reads the next_node from state
    and returns the next node name.
    """
    
    next_node = state.get("next_node", "fallback_agent")  # Changed default from "__end__"

    
    return next_node

# -------------------------
# Build Graph
# -------------------------
graph = StateGraph(BotState)

# Register nodes
# Register nodes
# Register nodes
graph.add_node("router", router_node)
graph.add_node("user_agent", user_agent)
graph.add_node("ticket_agent", ticket_agent)
graph.add_node("clarifier", clarifier)
graph.add_node("fallback_agent", fallback_agent)
graph.add_node("summarizer", summarizer)

# Set entry point
graph.add_edge(START, "router")

# Add conditional edges from router to different agents
graph.add_conditional_edges(
    "router",
    route_based_on_next_node,
    {
        "user_agent": "user_agent",
        "ticket_agent": "ticket_agent", 
        "clarifier": "clarifier",
        "fallback_agent": "fallback_agent",
        "summarizer": "summarizer",
        "__end__": "__end__"
    }
)

# After each agent runs, check if we should end or continue
def should_continue(state: BotState) -> str:
    """
    Determine whether to continue processing or end the conversation.
    """
    # Check if the last message indicates the conversation should end
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1].get("content", "").lower() if isinstance(messages[-1], dict) else str(messages[-1]).lower()
        if any(exit_word in last_message for exit_word in ["exit", "quit", "goodbye", "bye", "done"]):
            return "__end__"
    
    # Check if the agent has indicated completion
    context = state.get("context", {})
    if context.get("completed", False):
        return "__end__"
    
    # Otherwise, continue to router
    return "router"

# Add conditional edges from agents
graph.add_conditional_edges("user_agent", should_continue)
graph.add_conditional_edges("ticket_agent", should_continue)
graph.add_conditional_edges("clarifier", should_continue)
graph.add_conditional_edges("fallback_agent", should_continue)
graph.add_conditional_edges("summarizer", should_continue)


compiled = graph.compile()