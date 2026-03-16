import sqlite3
import json
import time
import os

DB_PATH = os.getenv("DB_PATH", "app/cache/melodex.db")
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", 3600))


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_cache_table():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at REAL NOT NULL
            )
        """)
        c.commit()


def set_cache(key: str, value, ttl: int = DEFAULT_TTL):
    init_cache_table()
    expires_at = time.time() + ttl
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), expires_at),
        )
        c.commit()


def get_cache(key: str):
    init_cache_table()
    with _conn() as c:
        row = c.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
    if not row:
        return None
    if time.time() > row["expires_at"]:
        delete_cache(key)
        return None
    return json.loads(row["value"])


def delete_cache(key: str):
    init_cache_table()
    with _conn() as c:
        c.execute("DELETE FROM cache WHERE key = ?", (key,))
        c.commit()


def clear_all_cache():
    init_cache_table()
    with _conn() as c:
        c.execute("DELETE FROM cache")
        c.commit()


def get_cache_age(key: str):
    """Returns seconds since cache was last set, or None if not cached."""
    init_cache_table()
    with _conn() as c:
        row = c.execute(
            "SELECT expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
    if not row:
        return None
    remaining = row["expires_at"] - time.time()
    age = DEFAULT_TTL - remaining
    return max(0.0, age)
