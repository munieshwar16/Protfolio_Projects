"""
Graph package
-------------
Exports the compiled LangGraph and key nodes/utilities.
"""

# Main compiled graph & state types
from .graph import compiled  # the compiled StateGraph ready to invoke

# Individual nodes/utilities commonly used elsewhere
from .router import router_logic

# If you put the LLM client here (per our plan):
try:
    from .llm_client import llm_call  # optional import for convenience
except Exception:
    # Keep imports safe if llm_client isn't configured yet
    llm_call = None  # type: ignore

__all__ = [
    "compiled",
    "router",
    "llm_call",
]
