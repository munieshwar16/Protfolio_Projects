# src/db/migrate.py
"""
Async migration runner for the Mini-Jira DB.

- Applies src/db/schema.sql (idempotent)
- Applies any .sql files under src/db/migrations/ exactly once (in filename order)
- Records applied migrations (filename + sha256(content)) in schema_migrations table

Usage:
  python -m src.db.migrate           # apply schema + pending migrations
  python -m src.db.migrate apply     # same as above
  python -m src.db.migrate status    # show which migrations are applied/pending
"""

import asyncio
import hashlib
import os
from pathlib import Path
from typing import List, Tuple

import aiosqlite

# Paths
ROOT = Path(__file__).resolve().parent  # src/db
SCHEMA_PATH = ROOT / "schema.sql"
MIGRATIONS_DIR = ROOT / "migrations"    # optional directory for extra .sql files
DB_PATH = os.environ.get("DB_PATH", "mini_jira.db")


async def _ensure_conn() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH, isolation_level=None)  # autocommit
    await db.execute("PRAGMA journal_mode=WAL;")
    await db.execute("PRAGMA synchronous=NORMAL;")
    await db.execute("PRAGMA foreign_keys=ON;")
    await db.execute("PRAGMA busy_timeout=3000;")
    return db


async def _ensure_migrations_table(db: aiosqlite.Connection) -> None:
    await db.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            sha256 TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def _applied_migrations(db: aiosqlite.Connection) -> List[Tuple[str, str]]:
    cur = await db.execute("SELECT filename, sha256 FROM schema_migrations ORDER BY filename")
    rows = await cur.fetchall()
    await cur.close()
    return [(r[0], r[1]) for r in rows]


def _list_migration_files() -> List[Path]:
    if not MIGRATIONS_DIR.exists():
        return []
    return sorted([p for p in MIGRATIONS_DIR.glob("*.sql") if p.is_file()], key=lambda p: p.name)


async def apply_schema(db: aiosqlite.Connection) -> None:
    if SCHEMA_PATH.exists():
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        await db.executescript(sql)


async def apply_migrations(db: aiosqlite.Connection) -> None:
    await _ensure_migrations_table(db)
    already = dict(await _applied_migrations(db))  # filename -> sha256

    for path in _list_migration_files():
        sql = path.read_text(encoding="utf-8")
        digest = _sha256(sql)

        # If filename already recorded with same digest, skip
        if path.name in already and already[path.name] == digest:
            continue

        # If filename recorded but digest changed, we disallow destructive re-run
        if path.name in already and already[path.name] != digest:
            raise RuntimeError(
                f"Migration '{path.name}' content changed after being applied. "
                "Create a new migration file instead."
            )

        # Apply migration
        await db.executescript(sql)
        # Record as applied
        await db.execute(
            "INSERT INTO schema_migrations(filename, sha256) VALUES (?, ?)",
            (path.name, digest),
        )


async def status(db: aiosqlite.Connection) -> str:
    await _ensure_migrations_table(db)
    applied = {fn for fn, _ in await _applied_migrations(db)}
    files = _list_migration_files()

    lines = []
    lines.append(f"Database: {DB_PATH}")
    lines.append(f"schema.sql: {'present' if SCHEMA_PATH.exists() else 'missing'}")
    lines.append("Migrations directory: " + (str(MIGRATIONS_DIR) if MIGRATIONS_DIR.exists() else "missing (no extra migrations)"))
    lines.append("")
    lines.append("Applied migrations:")
    if applied:
        for fn in sorted(applied):
            lines.append(f"  ✔ {fn}")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append("Pending migrations:")
    pending = [p.name for p in files if p.name not in applied]
    if pending:
        for fn in pending:
            lines.append(f"  • {fn}")
    else:
        lines.append("  (none)")

    return "\n".join(lines)


async def main(cmd: str = "apply") -> None:
    db = await _ensure_conn()
    try:
        if cmd == "status":
            print(await status(db))
            return

        # Default: apply schema + migrations
        await apply_schema(db)
        await apply_migrations(db)
        print("Schema and migrations applied successfully.")
    finally:
        await db.close()


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "apply"
    asyncio.run(main(cmd))
