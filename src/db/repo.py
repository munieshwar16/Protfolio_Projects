# src/db/repo.py
from typing import Optional, List, Tuple, Dict, Any
import aiosqlite
from .conn import get_db

# ---------- USERS ----------

class UserRepo:
    @staticmethod
    async def add_user(name: str) -> int:
        """
        Creates a user if not exists; returns user id.
        Idempotent: if user already exists, returns existing id.
        """
        name = (name or "").strip()
        if not name:
            raise ValueError("User name cannot be empty.")

        db = await get_db()
        try:
            cur = await db.execute("INSERT INTO users(name) VALUES (?)", (name,))
            await db.commit()
            return cur.lastrowid
        except aiosqlite.IntegrityError:
            row = await db.execute_fetchone("SELECT id FROM users WHERE name=?", (name,))
            if not row:
                raise
            return int(row[0])

    @staticmethod
    async def get_user_id(name: str) -> Optional[int]:
        db = await get_db()
        # Case-insensitive lookup
        row = await db.execute_fetchone("SELECT id FROM users WHERE lower(name)=lower(?)", (name,))
        return int(row[0]) if row else None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        db = await get_db()
        row = await db.execute_fetchone("SELECT id, name FROM users WHERE id=?", (user_id,))
        if not row:
            return None
        return {"id": int(row[0]), "name": row[1]}


# ---------- TICKETS ----------

class TicketRepo:
    @staticmethod
    async def create_ticket(title: str, assignee_id: int) -> int:
        """
        Creates a ticket (title, assignee_id). Unique(title, assignee_id).
        If duplicate exists, return existing id (idempotent).
        """
        title = (title or "").strip()
        if not title:
            raise ValueError("Ticket title cannot be empty.")

        db = await get_db()
        try:
            cur = await db.execute(
                "INSERT INTO tickets(title, assignee_id) VALUES (?, ?)",
                (title, assignee_id),
            )
            await db.commit()
            return cur.lastrowid
        except aiosqlite.IntegrityError:
            row = await db.execute_fetchone(
                "SELECT id FROM tickets WHERE title=? AND assignee_id=?",
                (title, assignee_id),
            )
            if not row:
                raise
            return int(row[0])

    @staticmethod
    async def get_ticket(ticket_id: int) -> Optional[Tuple[int, str, int, str]]:
        """
        Returns (id, title, assignee_id, status) or None.
        """
        db = await get_db()
        row = await db.execute_fetchone(
            "SELECT id, title, assignee_id, status FROM tickets WHERE id=?",
            (ticket_id,),
        )
        if not row:
            return None
        # Ensure correct types
        return (int(row[0]), row[1], int(row[2]), row[3])

    @staticmethod
    async def set_status(ticket_id: int, status: str) -> bool:
        """
        Updates ticket status. Returns True if a row was updated.
        """
        db = await get_db()
        cur = await db.execute(
            "UPDATE tickets SET status=? WHERE id=?",
            (status, ticket_id),
        )
        await db.commit()
        return cur.rowcount == 1

    @staticmethod
    async def list_by_status(status: Optional[str]):
        """
        Returns list of (ticket_id, title, assignee_name, status),
        filtered by status if provided, else all tickets.
        """
        db = await get_db()
        if status:
            sql = """
                SELECT t.id, t.title, u.name, t.status
                FROM tickets t
                JOIN users u ON u.id = t.assignee_id
                WHERE t.status=?
                ORDER BY t.id
            """
            rows = await db.execute_fetchall(sql, (status,))
        else:
            sql = """
                SELECT t.id, t.title, u.name, t.status
                FROM tickets t
                JOIN users u ON u.id = t.assignee_id
                ORDER BY t.id
            """
            rows = await db.execute_fetchall(sql)
        return [(int(r[0]), r[1], r[2], r[3]) for r in rows]

    @staticmethod
    async def update_all_tickets_status(status: str) -> int:
        db = await get_db()
        result = await db.execute("UPDATE tickets SET status = ? WHERE 1=1", (status,))
        await db.commit()
        return result.rowcount

    @staticmethod
    async def delete_ticket(ticket_id: int) -> int:
        db = await get_db()
        result = await db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        await db.commit()
        return result.rowcount

    @staticmethod
    async def delete_all_tickets() -> int:
        db = await get_db()
        result = await db.execute("DELETE FROM tickets")
        await db.commit()
        return result.rowcount
