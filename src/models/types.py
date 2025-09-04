"""
Typed models for the Mini-Jira bot.
Lightweight contracts shared across the router/agents/graph.
If you later want runtime validation, you can swap these for Pydantic models.
"""

from __future__ import annotations
from typing import TypedDict, List, Dict, Any, Optional, Literal
from typing_extensions import Annotated

# ----- Conversation state -----

class BotMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class BotState(TypedDict):
    # Rolling conversation log (older history may be summarized into a single system message)
    messages: Annotated[List[BotMessage], "multiple_values"]
    # Working memory for the current turn, set by the Router and used by agents.
    # Example:
    # {
    #   "pending_intent": "create_ticket",
    #   "slots": {"title": "Login bug", "assignee": "Alice", "ticket_id": None, "status": None}
    # }
    context: Dict[str, Any]

# ----- Domain models -----

class User(TypedDict):
    id: int
    name: str

Status = Literal["OPEN", "IN PROGRESS", "CLOSED"]

class Ticket(TypedDict):
    id: int
    title: str
    assignee_id: int
    status: Status

# ----- Slots container (helps typing router/clarifier state) -----

class Slots(TypedDict, total=False):
    name: Optional[str]
    title: Optional[str]
    assignee: Optional[str]
    ticket_id: Optional[int]
    status: Optional[Status]
