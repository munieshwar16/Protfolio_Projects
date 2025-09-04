import pytest
import asyncio
from src.graph.router import router

@pytest.mark.asyncio
async def test_router_add_user_intent():
    state = {"messages": [{"role": "user", "content": "Add Alice as a user"}]}
    state = await router(state)
    ctx = state["context"]
    assert ctx["pending_intent"] == "add_user"
    assert ctx["slots"]["name"] in {"Alice", "alice"}
