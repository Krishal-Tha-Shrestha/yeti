import os
import sqlite3
import datetime
from typing import List, Dict

# DB located at project root: yeti.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "yeti.db"))


def _get_conn():
    # Ensure parent directory exists
    parent = os.path.dirname(DB_PATH)
    if not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create chat_logs and user_profile tables if they don't exist."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profile (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_message(session_id: str, role: str, content: str):
    """Save one message to chat_logs."""
    ts = datetime.datetime.now().isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_logs (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, ts),
    )
    conn.commit()
    conn.close()


def get_recent_messages(limit: int = 20) -> List[Dict]:
    """Return the last `limit` messages ordered oldest->newest as list of {role, content} dicts.
    Useful for injecting into model context.
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM chat_logs ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    # rows are newest->oldest; reverse to oldest->newest
    results = []
    for r in reversed(rows):
        results.append({"role": r["role"], "content": r["content"]})
    return results


def save_profile_fact(key: str, value: str):
    """Insert or update a profile fact."""
    ts = datetime.datetime.now().isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_profile (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (key, value, ts),
    )
    conn.commit()
    conn.close()


def get_all_profile_facts() -> str:
    """Return all profile facts formatted as a readable string for the system prompt."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM user_profile ORDER BY key")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return "(no profile facts yet)"
    lines = []
    for r in rows:
        lines.append(f"{r['key']}: {r['value']}")
    return "\n".join(lines)


def get_profile_fact(key: str) -> str:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
