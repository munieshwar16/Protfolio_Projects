"""
Router Agent
------------
LLM-powered intent/slot extraction for the Mini-Jira bot.

It:
- Reads the latest user message
- Asks the local HF model (via llm_client.llm_call) to return STRICT JSON
- Parses/normalizes the JSON (status synonyms, ints)
- Stores intent + slots in state["context"] for downstream agents
- Returns the name of the next agent to execute
"""

from __future__ import annotations
from pyexpat.errors import messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import Dict, Any, Optional
import json
import re

from src.graph.llm_client import llm_call

SUPPORTED_INTENTS = {
    "add_user",
    "list_users",  # Added this intent
    "create_ticket",
    "view_ticket",
    "update_status",
    "list_tickets",
    "delete_tickets",  # <-- add this
    "unsupported",
}

VALID_STATUSES = {"OPEN", "IN PROGRESS", "CLOSED"}

JSON_SYSTEM_HINT = (
    "You are a strict JSON function. "
    "Return ONLY valid JSON, no prose, no markdown, no code fences."
)

EXTRACTION_INSTRUCTIONS = """
You are routing a natural-language request for a tiny Jira-like system.

Return a SINGLE JSON object (no markdown, no commentary) with this exact schema and keys:
{
  "intent": "add_user | create_ticket | ...",
  "slots": {
    "titles": [string]|string|null,      // list of ticket titles or single title
    "assignees": [string]|string|null,   // list of assignees or single assignee
    ... // other slots unchanged
  }
}

Rules:
- For "create_ticket", if multiple titles or assignees are present, extract all as lists.
- If only one, use a single-item list.
- Pair titles and assignees by order; if counts differ, assign all titles to all assignees.

Examples:
User: create tickets named frontend bug, hallucination, authentication and assign it to muni, zaid and joseph
{"intent": "create_ticket", "slots": {"titles": ["frontend bug", "hallucination", "authentication"], "assignees": ["muni", "zaid", "joseph"]}}

User: create a ticket for login bug and assign it to Alice
{"intent": "create_ticket", "slots": {"titles": ["login bug"], "assignees": ["Alice"]}}

User: delete all the tickets
{"intent": "delete_tickets", "slots": {}}

User: remove all tickets
{"intent": "delete_tickets", "slots": {}}

User: delete ticket 5
{"intent": "delete_tickets", "slots": {"ticket_id": 5}}
"""

def _safe_json_loads(s: str) -> Optional[dict]:
    """
    Try strict JSON parse; if it fails (model added junk), attempt to salvage by
    extracting the first {...} block. Return None on failure.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Try to find a JSON object substring
        m = re.search(r"\{.*\}", s, flags=re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None

def _normalize_status(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    v = val.strip().upper().replace("-", " ").replace("_", " ")
    # simple synonyms
    if v in {"INPROGRESS", "IN  PROGRESS"}:
        v = "IN PROGRESS"
    if v in {"OPEN", "CLOSED", "IN PROGRESS"}:
        return v
    # map common variants
    mapping = {
        "OPENED": "OPEN",
        "CLOSE": "CLOSED",
        "CLOSEd": "CLOSED",
        "DONE": "CLOSED",
        "RESOLVED": "CLOSED",
        "START": "IN PROGRESS",
        "STARTED": "IN PROGRESS",
        "WORKING": "IN PROGRESS",
        "INPROG": "IN PROGRESS",
        "PENDING": "IN PROGRESS",
    }
    return mapping.get(v, None)

def _normalize_ticket_id(val: Any) -> Optional[int]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        try:
            iv = int(val)
            return iv if iv >= 0 else None
        except Exception:
            return None
    # try to pull an integer from a string like "#12" or "ticket 12"
    if isinstance(val, str):
        m = re.search(r"\d+", val)
        if m:
            return int(m.group(0))
    return None

def _trim(s: Optional[str]) -> Optional[str]:
    return s.strip() if isinstance(s, str) and s.strip() else None

async def router_logic(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core router logic that processes the message and updates context.
    Supports both dicts and HumanMessage objects for user messages.
    """
    messages = state.get("messages", [])
    from langchain_core.messages import HumanMessage
    def extract_user_content(m):
        if isinstance(m, dict) and m.get("role") == "user":
            return m.get("content")
        if isinstance(m, HumanMessage):
            return m.content
        if hasattr(m, "role") and getattr(m, "role", None) in ("user", "human"):
            return getattr(m, "content", None)
        return None
    last_user = next((extract_user_content(m) for m in reversed(messages) if extract_user_content(m)), None)
    if not last_user:
        return {
            "context": {"pending_intent": "unsupported", "slots": {}}
        }

    prompt = f"{EXTRACTION_INSTRUCTIONS}\n\nUser input:\n{last_user}"
    raw = await llm_call(prompt=prompt, system=JSON_SYSTEM_HINT)
    parsed = _safe_json_loads(raw) or {"intent": "unsupported", "slots": {}}

    # --- DEBUG PRINTS ---
    print("LLM RAW OUTPUT:", raw)
    print("PARSED:", parsed)
    # --- END DEBUG PRINTS ---

    # Pull fields safely
    intent = str(parsed.get("intent", "unsupported")).strip().lower().replace(" ", "_")
    print("EXTRACTED INTENT:", intent)  # <--- Add this line

    # bring back to canonical form used in SUPPORTED_INTENTS
    intent_map = {
        "add_user": "add_user",
        "list_users": "list_users",  # Added this mapping
        "create_ticket": "create_ticket",
        "view_ticket": "view_ticket",
        "update_status": "update_status",
        "list_tickets": "list_tickets",
        "unsupported": "unsupported",
        "delete_tickets": "delete_tickets",
        "remove_tickets": "delete_tickets",
        "delete_ticket": "delete_tickets",
        "remove_ticket": "delete_tickets",
    }
    intent = intent_map.get(intent, "unsupported")

    slots = parsed.get("slots", {}) or {}

    # --- PATCH START ---
    # Extract titles and assignees as lists if present
    titles = slots.get("titles")
    if titles is None:
        # fallback: try singular
        titles = slots.get("title")
    if isinstance(titles, str):
        titles = [titles]
    elif titles is None:
        titles = []
    assignees = slots.get("assignees")
    if assignees is None:
        assignees = slots.get("assignee")
    if isinstance(assignees, str):
        assignees = [assignees]
    elif assignees is None:
        assignees = []
    # --- PATCH END ---

    names = slots.get("names") or []
    # Normalize names: trim whitespace, remove duplicates
    if isinstance(names, list):
        names = list({_trim(n) for n in names if _trim(n)})
    if len(names) == 1:
        names = names[:1]
    elif len(names) > 5:
        names = names[:5]
    name = names

    ticket_id = _normalize_ticket_id(slots.get("ticket_id"))
    status = _normalize_status(slots.get("status"))

    # Validate final status
    if status and status not in VALID_STATUSES:
        status = None

    # If intent looks like an action that implies listing, gently coerce
    if intent == "view_ticket" and ticket_id is None:
        if status or any(k in (titles[0] if titles else "").lower() for k in ("all", "open", "closed", "in progress")):
            intent = "list_tickets"

    # Return context update for downstream agents
    return {
        "context": {
            "pending_intent": intent if intent in SUPPORTED_INTENTS else "unsupported",
            "slots": {
                "names": name,
                "titles": titles,
                "assignees": assignees,
                "title": titles[0] if titles else None,
                "assignee": assignees[0] if assignees else None,
                "ticket_id": ticket_id,
                "status": status,
            },
        }
    }

async def router(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Router node for LangGraph conditional edges.
    Processes the message, updates context, and sets the next node name in state.
    """
    updates = await router_logic(state)
    state.update(updates)
    pending_intent = updates["context"]["pending_intent"]
    intent_to_agent = {
        "add_user": "user_agent",
        "list_users": "user_agent",
        "create_ticket": "ticket_agent", 
        "view_ticket": "ticket_agent",
        "update_status": "ticket_agent",
        "list_tickets": "ticket_agent",
        "delete_tickets": "ticket_agent",   
        "remove_tickets": "ticket_agent",
        "unsupported": "__end__",
    }
    # If unsupported or no actionable input, end the conversation
    state["next_node"] = intent_to_agent.get(pending_intent, "__end__")
    return state