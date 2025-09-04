"""
Mini-Jira Chatbot Demo
----------------------
Run this file to interact with your Mini-Jira bot via the command line.
"""

import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from src.models import BotState, BotMessage
from src.graph import compiled

def get_role(m):
    """Extract role from different message types"""
    if isinstance(m, dict):
        return m.get("role")
    if hasattr(m, "role"):
        return m.role
    # Handle LangChain message types
    if isinstance(m, HumanMessage):
        return "user"
    if isinstance(m, AIMessage):
        return "assistant"
    return None

def get_content(m):
    """Extract content from different message types"""
    if isinstance(m, dict):
        return m.get("content", str(m))
    if hasattr(m, "content"):
        return m.content
    return str(m)

async def main():
    print("Welcome to Mini-Jira! Type your requests (type 'exit' to quit).\n")
    state: BotState = {"messages": [], "context": {}}

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue

        # Add user message as HumanMessage (LangChain format)
        user_message = HumanMessage(content=user_input)
        state["messages"].append(user_message)

        # Run the chatbot workflow
        state = await compiled.ainvoke(state, config={"recursion_limit": 50})

        # Debug: print all messages in state after ainvoke
        #print("[DEMO DEBUG] state['messages'] after ainvoke:")
    # for idx, m in enumerate(state["messages"]):
    #     print(f"  [{idx}] {type(m)}: content='{get_content(m)}' role='{get_role(m)}'")

        # Find the latest assistant message from this turn
        assistant_msgs = []
        for m in state["messages"]:
            role = get_role(m)
            if role == "assistant":
                assistant_msgs.append(m)

        if assistant_msgs:
            last_msg = assistant_msgs[-1]
            content = get_content(last_msg)
            print(f"Bot: {content}")
        else:
            print("Bot: (no response)")

        # After each turn, keep only the last user and last assistant message to prevent looping
        user_msgs = [m for m in state["messages"] if get_role(m) == "user"]
        assistant_msgs = [m for m in state["messages"] if get_role(m) == "assistant"]
        
        new_messages = []
        if user_msgs:
            new_messages.append(user_msgs[-1])
        if assistant_msgs:
            new_messages.append(assistant_msgs[-1])
        
        state["messages"] = new_messages
        
        # Reset context for next turn but preserve any persistent data
        state["context"] = {}

if __name__ == "__main__":
    asyncio.run(main())