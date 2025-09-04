"""
Clarifier Agent (LLM-powered)
-----------------------------
Uses an LLM to ask natural clarifying questions when user input
is missing required details for an action.
"""

from typing import Dict, Any
from src.graph.llm_client import llm_call


async def clarifier(state: Dict[str, Any]) -> Dict[str, Any]:
    context = state.get("context", {})
    pending_intent = context.get("pending_intent")
    slots = context.get("slots", {})

    # Find missing fields
    missing = [k for k, v in slots.items() if v in (None, "")]
    if not missing:
        # Nothing missing → skip clarifier
        return state

    missing_slot = missing[0]

    # Build a prompt for the LLM
    prompt = f"""
    You are a helpful Jira admin assistant.
    The user wants to perform action: {pending_intent}.
    Currently, I have the following details: {slots}.
    The missing detail is: {missing_slot}.
    
    Ask the user a short, natural clarifying question to get that detail.
    Do not explain; just ask the question.
    """

    question = await llm_call(prompt)

    # Append assistant's clarifying question
    state.setdefault("messages", []).append({
        "role": "assistant",
        "content": question.strip()
    })
    return state
