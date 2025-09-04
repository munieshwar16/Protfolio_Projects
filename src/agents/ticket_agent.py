"""
Ticket Agent
------------
Handles ticket operations:
- Create new ticket
- View ticket by ID
- Update ticket status
- List tickets by status
"""

from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.db.repo import UserRepo, TicketRepo


async def ticket_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    #print("[TICKET_AGENT DEBUG] Called with state:", state)
    context = state.get("context", {})
    intent = context.get("pending_intent")
    slots = context.get("slots", {})

    #print(f"[TICKET_AGENT DEBUG] intent: {intent}, slots: {slots}")

    reply = ""

    # ---- CREATE TICKET ----
    if intent == "create_ticket":
        titles = slots.get("titles") or slots.get("title")
        assignees = slots.get("assignees") or slots.get("assignee")
        # Normalize to lists
        if isinstance(titles, str):
            titles = [titles]
        if isinstance(assignees, str):
            assignees = [assignees]
        if not titles or not assignees:
            reply = "I need both a title and an assignee to create a ticket."
        else:
            results = []
            # Pair by order: first title to first assignee, etc.
            for title, assignee in zip(titles, assignees):
                user_id = await UserRepo.get_user_id(assignee)
                if not user_id:
                    results.append(f"User {assignee} does not exist.")
                    continue
                ticket_id = await TicketRepo.create_ticket(title, user_id)
                results.append(f"Ticket '{title}' assigned to {assignee} (id={ticket_id})")
            reply = "\n".join(results)

    # ---- VIEW TICKET ----
    elif intent == "view_ticket":
        ticket_id = slots.get("ticket_id")
        if not ticket_id:
            reply = "Please provide a ticket ID to view."
        else:
            ticket = await TicketRepo.get_ticket(int(ticket_id))
            if not ticket:
                reply = f"No ticket found with id={ticket_id}."
            else:
                t_id, title, assignee_id, status = ticket
                assignee_name = (await UserRepo.get_user_by_id(assignee_id))["name"]
                reply = f"Ticket {t_id}: '{title}' (status: {status}, assignee: {assignee_name})."

    # ---- UPDATE STATUS ----
    elif intent == "update_status":
        ticket_id = slots.get("ticket_id")
        status = slots.get("status")
        if ticket_id is None and status:
            # Update all tickets
            updated_count = await TicketRepo.update_all_tickets_status(status)
            reply = f"Updated {updated_count} tickets to {status}."
        elif ticket_id and status:
            # Update single ticket
            valid = {"OPEN", "IN PROGRESS", "CLOSED"}
            if status not in valid:
                reply = f"Invalid status '{status}'. Must be one of {valid}."
            else:
                success = await TicketRepo.set_status(int(ticket_id), status)
                reply = f"Ticket {ticket_id} updated to {status}." if success else f"No ticket found with id={ticket_id}."
        else:
            reply = "Please provide both ticket ID and new status."

    # ---- LIST TICKETS ----
    elif intent == "list_tickets":
        tickets = await TicketRepo.list_by_status(slots.get("status"))
        if not tickets:
            reply = "No tickets found."
        else:
            reply = "ID   Title                 Assignee     Status\n"
            for tid, title, assignee, status in tickets:
                reply += f"{tid:<4} {title:<20} {assignee:<12} {status}\n"

    elif intent == "delete_tickets":
        ticket_id = slots.get("ticket_id")
        if ticket_id:
            deleted = await TicketRepo.delete_ticket(ticket_id)
            if deleted:
                reply = f"Deleted ticket {ticket_id}."
            else:
                reply = f"Ticket {ticket_id} not found."
        else:
            deleted_count = await TicketRepo.delete_all_tickets()
            reply = f"Deleted {deleted_count} tickets."

    else:
        reply = "Sorry, I can't handle that ticket request."

    # Create proper LangChain message object
    #print(f"[TICKET_AGENT DEBUG] Generating reply: {reply}")
    ai_message = AIMessage(content=reply)
    
    # Return updated state with new message
    updated_state = {
        "messages": state.get("messages", []) + [ai_message],
        "context": {
            **context,
            "completed": True  # Mark as completed to end conversation
        }
    }
    
    #print("[TICKET_AGENT DEBUG] Returning updated state with message count:", len(updated_state["messages"]))
    return updated_state