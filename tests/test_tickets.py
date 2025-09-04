import pytest
from src.db.repo import UserRepo, TicketRepo
from src.db.conn import get_db

@pytest.mark.asyncio
async def test_ticket_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    db = await get_db()
    await db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        assignee_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','IN PROGRESS','CLOSED')),
        UNIQUE(title, assignee_id)
    );
    """)

    # Add user
    uid = await UserRepo.add_user("Bob")
    assert uid is not None

    # Create ticket
    tid = await TicketRepo.create_ticket("Login bug", uid)
    ticket = await TicketRepo.get_ticket(tid)
    assert ticket[1] == "Login bug"
    assert ticket[3] == "OPEN"

    # Update status
    ok = await TicketRepo.set_status(tid, "CLOSED")
    assert ok

    updated = await TicketRepo.get_ticket(tid)
    assert updated[3] == "CLOSED"

    # List tickets
    tickets = await TicketRepo.list_by_status("CLOSED")
    assert any(t[0] == tid for t in tickets)
