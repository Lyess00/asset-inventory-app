import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "/app/data/assets.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            asset_type  TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'active',
            expiry_date TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    logger.info('{"event": "database_initialized", "path": "%s"}', DB_PATH)