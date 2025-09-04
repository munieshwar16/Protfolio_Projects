import pytest
import asyncio
from src.db.repo import UserRepo
from src.db.conn import get_db

@pytest.mark.asyncio
async def test_add_and_get_user(tmp_path, monkeypatch):
    # Override DB_PATH for test isolation
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))

    db = await get_db()
    await db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    uid = await UserRepo.add_user("Alice")
    assert isinstance(uid, int)

    uid2 = await UserRepo.get_user_id("Alice")
    assert uid == uid2

    user = await UserRepo.get_user_by_id(uid)
    assert user["name"] == "Alice"
