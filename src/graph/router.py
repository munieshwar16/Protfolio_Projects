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
    "delete_tickets",  # Added this intent
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
  "intent": "add_user | list_users | create_ticket | view_ticket | update_status | list_tickets | delete_tickets | unsupported",
  "slots": {
    "names": [string]|string|null,        // user names if present (for add_user)
    "titles": [string]|string|null,       // ticket titles if present (for create_ticket)
    "assignees": [string]|string|null,    // assignee names if present (for create_ticket)
    "name": string|null,                  // single user name if present
    "title": string|null,                 // single ticket title if present
    "assignee": string|null,              // single assignee if present
    "ticket_id": number|null,             // integer ticket id if present
    "status": string|null                 // one of: OPEN, IN PROGRESS, CLOSED (or null)
  }
}

Rules:
- For "create_ticket", if multiple titles or assignees are present, extract all as lists in "titles" and "assignees".
- If only one, use a single-item list.
- Pair titles and assignees by order; if counts differ, assign all titles to all assignees.
- For "add_user", support multiple names as a list in "names".
- ticket_id must be a number if present (no text).
- status must be EXACTLY one of: OPEN, IN PROGRESS, CLOSED (upper-case, spaces as shown), else null.
- If a required piece of information is missing, set its value to null.
- If the request is outside capabilities, set "intent": "unsupported".
- Respond with VALID JSON ONLY. Do NOT include any explanation.

Examples:
User: create a ticket named ui_glitch and tag jira and abhi
{"intent": "create_ticket", "slots": {"titles": ["ui_glitch"], "assignees": ["jira", "abhi"]}}

User: create a ticket called backend bug and tag alice, john, and joseph
{"intent": "create_ticket", "slots": {"titles": ["backend bug"], "assignees": ["alice", "john", "joseph"]}}

User: create tickets named bug1, bug2 and assign them to alice and john respectively
{"intent": "create_ticket", "slots": {"titles": ["bug1", "bug2"], "assignees": ["alice", "john"]}}
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

    # TEMPORARY DEBUG: Manual override for delete commands
    if "delete" in last_user.lower() and "ticket" in last_user.lower():
        #print("[ROUTER DEBUG] Manual delete override triggered")
        # Try to extract ticket ID
        import re
        ticket_match = re.search(r'(\d+)', last_user)
        ticket_id = int(ticket_match.group(1)) if ticket_match else None
        return {
            "context": {
                "pending_intent": "delete_tickets",
                "slots": {
                    "name": None,
                    "title": None,
                    "assignee": None,
                    "ticket_id": ticket_id,
                    "status": None,
                },
            }
        }

    prompt = f"{EXTRACTION_INSTRUCTIONS}\n\nUser input:\n{last_user}"
    raw = await llm_call(prompt=prompt, system=JSON_SYSTEM_HINT)
    parsed = _safe_json_loads(raw) or {"intent": "unsupported", "slots": {}}

    # Pull fields safely
    intent = str(parsed.get("intent", "unsupported")).strip().lower().replace(" ", "_")
    # bring back to canonical form used in SUPPORTED_INTENTS
    intent_map = {
        "add_user": "add_user",
        "list_users": "list_users",  # Added this mapping
        "create_ticket": "create_ticket",
        "view_ticket": "view_ticket",
        "update_status": "update_status",
        "list_tickets": "list_tickets",
        "unsupported": "unsupported",
    }
    intent = intent_map.get(intent, "unsupported")

    slots = parsed.get("slots", {}) or {}
    names = slots.get("names") or slots.get("name")
    titles = slots.get("titles") or slots.get("title")
    assignees = slots.get("assignees") or slots.get("assignee")
    ticket_id = _normalize_ticket_id(slots.get("ticket_id"))
    status = _normalize_status(slots.get("status"))

    # Validate final status
    if status and status not in VALID_STATUSES:
        status = None

    # If intent looks like an action that implies listing, gently coerce
    # (LLMs sometimes pick "view_ticket" with no id; that's really "list_tickets")
    if intent == "view_ticket" and ticket_id is None:
        # If the user said "show open tickets" etc., convert to list_tickets
        if status or any(k in (titles or "").lower() for k in ("all", "open", "closed", "in progress")):
            intent = "list_tickets"

    # Return context update for downstream agents
    return {
        "context": {
            "pending_intent": intent if intent in SUPPORTED_INTENTS else "unsupported",
            "slots": {
                "names": names,
                "titles": titles,
                "assignees": assignees,
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
        "list_users": "user_agent",  # Added this mapping
        "create_ticket": "ticket_agent", 
        "view_ticket": "ticket_agent",
        "update_status": "ticket_agent",
        "list_tickets": "ticket_agent",
        "delete_tickets": "ticket_agent",  # Added this mapping
        "unsupported": "__end__",
    }
    # If unsupported or no actionable input, end the conversation
    state["next_node"] = intent_to_agent.get(pending_intent, "__end__")
    return state