import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'library.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    conn = get_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_script = f.read()
    conn.executescript(schema_script)
    conn.commit()
    conn.close()

def execute_query(query, params=(), commit=False):
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
