"""
Summarizer Agent
----------------
Compresses older chat history into a concise summary
to prevent the conversation state from growing too large.
"""

from typing import Dict, Any
from src.graph.llm_client import llm_call

MAX_MESSAGES = 15  # keep last 15 messages verbatim


async def summarizer(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])

    if len(messages) <= MAX_MESSAGES:
        # Nothing to summarize
        return state

    # Separate older and recent messages
    old_messages = messages[:-MAX_MESSAGES]
    recent_messages = messages[-MAX_MESSAGES:]

    # Build summary prompt
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in old_messages)
    prompt = f"""
    Summarize the following conversation history in a concise way,
    keeping only important details (users, tickets, actions, statuses).

    Conversation:
    {history_text}

    Return the summary in plain text.
    """

    summary = await llm_call(prompt)

    # Replace older messages with a single summary note
    state["messages"] = [
        {"role": "system", "content": f"Summary of previous conversation: {summary.strip()}"}
    ] + recent_messages

    return state
