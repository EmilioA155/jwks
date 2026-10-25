

import os
import sqlite3
import time
from contextlib import contextmanager


DB_FILE = os.environ.get("JWKS_DB", "totally_not_my_privateKeys.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS keys(
    kid INTEGER PRIMARY KEY AUTOINCREMENT,
    key BLOB NOT NULL,
    exp INTEGER NOT NULL
)
"""


@contextmanager
def get_connection(db_file=None):
    """Open (creating if needed) the DB, commit on success, always close."""
    conn = sqlite3.connect(db_file or DB_FILE)
    try:
        with conn:  # commits, or rolls back on error
            yield conn
    finally:
        conn.close()


def init_db(db_file=None):
    """Create the keys table if it does not exist yet."""
    with get_connection(db_file) as conn:
        conn.execute(SCHEMA)


def save_key(pem, exp, db_file=None):
    """Store a PEM-encoded private key with its expiry (Unix time).

    Returns the new row's kid.
    """
    with get_connection(db_file) as conn:
        cur = conn.execute(
            "INSERT INTO keys (key, exp) VALUES (?, ?)",
            (pem, int(exp)),
        )
        return cur.lastrowid


def get_key(expired=False, db_file=None):
    """Return one (kid, pem, exp) row, or None if there isn't one.

    expired=False -> a key that has not expired yet.
    expired=True  -> a key that has already expired.
    """
    now = int(time.time())
    if expired:
        query = "SELECT kid, key, exp FROM keys WHERE exp <= ? " \
                "ORDER BY kid LIMIT 1"
    else:
        query = "SELECT kid, key, exp FROM keys WHERE exp > ? " \
                "ORDER BY kid LIMIT 1"
    with get_connection(db_file) as conn:
        return conn.execute(query, (now,)).fetchone()


def get_valid_keys(db_file=None):
    """Return every (kid, pem, exp) row whose key has not expired."""
    now = int(time.time())
    with get_connection(db_file) as conn:
        return conn.execute(
            "SELECT kid, key, exp FROM keys WHERE exp > ?",
            (now,),
        ).fetchall()
        