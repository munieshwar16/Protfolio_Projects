"""
Mini-Jira Bot
=============
Async Mini-Jira style chatbot using LangGraph + SQLite + Hugging Face LLM.

This package exposes high-level components:
- compiled graph workflow
- agents
- models
- db repositories
"""

# Expose the compiled graph (the orchestrated workflow)
from src.graph import compiled

# Expose agents for direct imports
from src.agents import (
    user_agent,
    ticket_agent,
    clarifier,
    fallback_agent,
    summarizer,
)

# Expose models (typed dictionaries for state and domain objects)
from src.models import (
    BotState,
    BotMessage,
    User,
    Ticket,
    Slots,
    Status,
)

# Expose repositories for DB access (if you want to call them directly in tests)
from src.db.repo import UserRepo, TicketRepo

__all__ = [
    "compiled",
    # Agents
    "user_agent",
    "ticket_agent",
    "clarifier",
    "fallback_agent",
    "summarizer",
    # Models
    "BotState",
    "BotMessage",
    "User",
    "Ticket",
    "Slots",
    "Status",
    # Repos
    "UserRepo",
    "TicketRepo",
]
