-- src/db/schema.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tickets (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  assignee_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  status       TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','IN PROGRESS','CLOSED')),
  UNIQUE(title, assignee_id)
);
