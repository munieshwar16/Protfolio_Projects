# Mini-Jira

A conversational, LLM-powered mini Jira-like ticketing system.  
You can add users, create and manage tickets, update statuses, list and delete tickets—all via natural language!

---

## Features

- **LLM-powered intent extraction:** Understands your requests in plain English.
- **User management:** Add/list users.
- **Ticket management:** Create, view, update, list, and delete tickets.
- **Status updates:** Supports statuses like OPEN, IN PROGRESS, CLOSED.
- **Batch operations:** Add multiple users or tickets in one command.
- **Summarizer:** (Optional) Summarizes long conversations.
- **Extensible:** Modular agents for routing, user, ticket, clarifier, fallback, and summarizer logic.

---

## Project Structure

```
mini_jira/
│
├── src/
│   ├── agents/
│   │   ├── user_agent.py      # Handles user-related actions
│   │   ├── ticket_agent.py    # Handles ticket-related actions
│   │   ├── clarifier.py       # (Optional) Clarifies ambiguous requests
│   │   ├── fallback_agent.py  # Handles unsupported/unknown requests
│   │   └── summarizer.py      # (Optional) Summarizes chat history
│   ├── db/
│   │   ├── repo.py            # Database access for users and tickets
│   │   └── conn.py            # Database connection logic
│   ├── graph/
│   │   ├── graph.py           # Orchestrates agent workflow (LangGraph)
│   │   └── router.py          # LLM-powered intent/slot extraction and routing
│   ├── models.py              # (Optional) Data models for state/messages
│   └── llm_client.py          # LLM API call logic
│
├── tests/
│   ├── test_users.py          # User-related tests
│   └── test_tickets.py        # Ticket-related tests
│
├── demo.py                    # CLI entry point
└── README.md                  # This file
```

---

## How It Works

1. **User Input:**  
   You type a request (e.g., "create a ticket named login bug and assign it to Alice").

2. **Router Agent:**  
   - Uses an LLM to extract the intent (e.g., `create_ticket`) and slots (e.g., title, assignee).
   - Maps the intent to the correct agent (user, ticket, etc.).

3. **Agent Execution:**  
   - The selected agent (e.g., `ticket_agent`) performs the action (e.g., creates a ticket in the DB).
   - Replies with a confirmation or result.

4. **Conversation Flow:**  
   - The system loops, handling each new user message.
   - Summarizer agent can compress old chat history if needed.

---

## Supported Commands (Examples)

- **Add users:**  
  `add users named anusha, bob, muni`
- **List users:**  
  `list all users`
- **Create tickets:**  
  `create tickets named bug1, bug2 and assign them to alice and bob respectively`
- **Update status:**  
  `set the status of ticket id 3 as closed`
- **List tickets:**  
  `list all tickets`  
  `get the open tickets`
- **Delete tickets:**  
  `delete ticket 5`  
  `delete all the tickets`

---

## Running the Project

1. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Set up the database:**  
   The database is created automatically on first run.

3. **Run the CLI:**
    ```sh
    python -m src.demo
    ```

4. **Type your requests!**  
   Type `exit` to quit.

---

## Running Tests

- **Install pytest and pytest-asyncio:**
    ```sh
    pip install pytest pytest-asyncio
    ```
- **Run tests:**
    ```sh
    pytest
    ```
  If you see `ModuleNotFoundError: No module named 'src'`, set your `PYTHONPATH`:
    - PowerShell: `$env:PYTHONPATH = "."`
    - cmd: `set PYTHONPATH=.`

---

## Customization & Extensibility

- **Agents:**  
  Add or modify agents in `src/agents/` to extend functionality.
- **LLM Prompt:**  
  Tune `EXTRACTION_INSTRUCTIONS` in `src/graph/router.py` for better intent extraction.
- **Database:**  
  Modify `src/db/repo.py` for custom user/ticket logic.

---

## Troubleshooting

- **"I can’t help with that."**  
  The LLM could not extract a supported intent. Try rephrasing or add more examples to the prompt.
- **Async test errors:**  
  Install `pytest-asyncio` and mark async tests with `@pytest.mark.asyncio`.
- **ModuleNotFoundError:**  
  Set your `PYTHONPATH` to the project root.

---

## Credits

- Built with [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain), and your favorite LLM!

---

Enjoy your conversational Mini-Jira