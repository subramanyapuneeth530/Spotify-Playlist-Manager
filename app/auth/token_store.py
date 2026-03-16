import sqlite3
import json
import time
import os

DB_PATH = os.getenv("DB_PATH", "app/cache/melodex.db")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_token_table():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        c.commit()


def save_tokens(access_token: str, refresh_token: str, expires_in: int):
    init_token_table()
    expires_at = time.time() + expires_in
    data = json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    })
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO tokens (key, value, updated_at) VALUES (?, ?, ?)",
            ("spotify_tokens", data, time.time()),
        )
        c.commit()


def load_tokens() -> dict:
    init_token_table()
    with _conn() as c:
        row = c.execute(
            "SELECT value FROM tokens WHERE key = ?", ("spotify_tokens",)
        ).fetchone()
    if not row:
        return None
    return json.loads(row["value"])


def is_token_expired() -> bool:
    tokens = load_tokens()
    if not tokens:
        return True
    return time.time() >= tokens.get("expires_at", 0) - 60


def clear_tokens():
    init_token_table()
    with _conn() as c:
        c.execute("DELETE FROM tokens WHERE key = ?", ("spotify_tokens",))
        c.commit()
