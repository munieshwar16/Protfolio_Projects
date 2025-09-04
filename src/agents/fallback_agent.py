"""
Fallback Agent
--------------
Handles unsupported or unknown user requests.
"""

from typing import Dict, Any


async def fallback_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appends a polite fallback response when the request
    cannot be handled by other agents.
    """
    state.setdefault("messages", []).append({
        "role": "assistant",
        "content": "I can’t help with that."
    })
    # Set completed flag so the graph can stop
    if "context" not in state:
        state["context"] = {}
    state["context"]["completed"] = True
    return state
