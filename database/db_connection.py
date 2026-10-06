import sqlite3
import os
import contextlib

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'library.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_connection():
    """Returns a SQLite connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextlib.contextmanager
def get_db():
    """Context manager for SQLite connections that ensures proper closing."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def initialize_database():
    """Initializes the database schema if it doesn't exist."""
    with get_db() as conn:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_script = f.read()
        conn.executescript(schema_script)
        conn.commit()

def fetch_all(query, params=()):
    """Executes a SELECT query and returns all rows as list of dicts, safely closing connection."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=()):
    """Executes a SELECT query and returns a single row as dict (or None), safely closing connection."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def execute_write(query, params=()):
    """Executes an INSERT/UPDATE/DELETE statement, commits and safely closes connection."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

def execute_query(query, params=(), commit=False):
    """Executes a query and optionally commits the transaction. Returns the cursor and conn."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor, conn
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
