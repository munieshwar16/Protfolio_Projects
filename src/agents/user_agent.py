"""
User Agent
----------
Handles user management actions such as adding new users.
"""

from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.db.repo import UserRepo


async def user_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles user management actions: create_user and list_users.
    """
    context = state.get("context", {})
    slots = context.get("slots", {})
    intent = context.get("pending_intent")

    #print(f"[USER_AGENT DEBUG] Called with state: {state}")
    #print(f"[USER_AGENT DEBUG] intent: {intent}, slots: {slots}")

    try:
        if intent == "list_users":
            # List all users
            users = []
            try:
                db = await UserRepo.get_db() if hasattr(UserRepo, 'get_db') else None
                if db is None:
                    from src.db.conn import get_db
                    db = await get_db()
                rows = await db.execute_fetchall("SELECT id, name FROM users ORDER BY id")
                users = [(int(r[0]), r[1]) for r in rows]
            except Exception as e:
                #print(f"[USER_AGENT DEBUG] Error fetching users: {e}")
                users = []
            
            if not users:
                reply = "No users found."
            else:
                reply = "Users:\n" + "\n".join([f"- {u[1]} (id={u[0]})" for u in users])
            
            #print(f"[USER_AGENT DEBUG] Generating reply: {reply}")

        elif intent == "add_user":
            # Create/add user
            names = slots.get("names") or []
            if not names:
                reply = "I need a user name to add. Please provide a username."
            else:
                added = []
                for name in names:
                    try:
                        user_id = await UserRepo.add_user(name)
                        added.append(f"{name} (id={user_id})")
                    except Exception as e:
                        added.append(f"{name} (error: {e})")
                reply = "Added users:\n" + "\n".join(added)
                
                #print(f"[USER_AGENT DEBUG] Generating reply: {reply}")

        else:
            reply = f"I don't know how to handle the intent '{intent}' for user operations."
            #print(f"[USER_AGENT DEBUG] Unknown intent: {intent}")

        # Get current messages and add the AI response
        messages = state.get("messages", [])
        
        # Add the AI response as an AIMessage object
        ai_message = AIMessage(content=reply)
        updated_messages = messages + [ai_message]
        
        # Update state with new messages and mark as completed
        updated_state = {
            **state,
            "messages": updated_messages,
            "context": {**context, "completed": True}
        }
        
        #print(f"[USER_AGENT DEBUG] Returning updated state with message count: {len(updated_messages)}")
        return updated_state

    except Exception as e:
        print(f"[USER_AGENT ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error message
        messages = state.get("messages", [])
        error_message = AIMessage(content=f"An error occurred while processing your request: {str(e)}")
        updated_messages = messages + [error_message]
        
        return {
            **state,
            "messages": updated_messages,
            "context": {**context, "completed": True}
        }