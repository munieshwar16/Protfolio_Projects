# src/db/conn.py
import aiosqlite
from typing import Optional

_DB: Optional[aiosqlite.Connection] = None
_DB_PATH = "mini_jira.db"  # override via .env if you like

async def get_db() -> aiosqlite.Connection:
    """
    Returns a singleton async SQLite connection configured for
    lightweight concurrency (WAL) and safe FK behavior.
    """
    global _DB
    if _DB is None:
        _DB = await aiosqlite.connect(_DB_PATH, isolation_level=None)  # autocommit
        await _DB.execute("PRAGMA journal_mode=WAL;")
        await _DB.execute("PRAGMA synchronous=NORMAL;")
        await _DB.execute("PRAGMA foreign_keys=ON;")
        await _DB.execute("PRAGMA busy_timeout=3000;")  # ms
        # convenience helpers (available in recent aiosqlite versions)
        if not hasattr(_DB, "execute_fetchone"):
            # polyfill for older aiosqlite
            async def _fetchone(sql: str, params=()):
                cur = await _DB.execute(sql, params)
                row = await cur.fetchone()
                await cur.close()
                return row
            async def _fetchall(sql: str, params=()):
                cur = await _DB.execute(sql, params)
                rows = await cur.fetchall()
                await cur.close()
                return rows
            _DB.execute_fetchone = _fetchone  # type: ignore[attr-defined]
            _DB.execute_fetchall = _fetchall  # type: ignore[attr-defined]
    return _DB
