import sqlite3
import os
import contextlib
from datetime import datetime, timedelta

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

def initialize_database(seed_sample=False):
    """Initializes the database schema if it doesn't exist, and optionally seeds sample data."""
    with get_db() as conn:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_script = f.read()
        conn.executescript(schema_script)
        conn.commit()
    if seed_sample:
        seed_sample_data_if_empty()

def seed_sample_data_if_empty():
    """Seeds realistic sample books, members, and transactions if tables are empty."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] > 0:
            return  # Already has data

        # Sample books: (isbn, title, author, category, publisher, total_copies, available_copies)
        sample_books = [
            ("978-0132350884", "Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Computer Science", "Prentice Hall", 5, 4),
            ("978-0262033848", "Introduction to Algorithms (4th Edition)", "Thomas H. Cormen", "Algorithms", "MIT Press", 4, 3),
            ("978-1593279288", "Python Crash Course: Hands-on Project-Based", "Eric Matthes", "Programming", "No Starch Press", 6, 6),
            ("978-0446310789", "To Kill a Mockingbird", "Harper Lee", "Classic Literature", "J.B. Lippincott & Co.", 3, 3),
            ("978-0451524935", "1984: A Dystopian Novel", "George Orwell", "Classic Literature", "Secker & Warburg", 4, 4),
            ("978-0134685991", "Effective Java (3rd Edition)", "Joshua Bloch", "Software Engineering", "Addison-Wesley", 3, 3),
            ("978-0141439518", "Pride and Prejudice", "Jane Austen", "Classic Literature", "T. Egerton", 3, 3)
        ]
        cursor.executemany(
            """
            INSERT INTO books (isbn, title, author, category, publisher, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            sample_books
        )

        # Sample members: (full_name, email, phone, address)
        sample_members = [
            ("Kamlesh Tewari", "kamlesh.tewari@example.com", "+91 9876543210", "Civil Lines, Prayagraj"),
            ("Aarav Sharma", "aarav.sharma@example.com", "+91 9812345678", "Sector 62, Noida"),
            ("Priya Patel", "priya.patel@example.com", "+91 9723456789", "Navrangpura, Ahmedabad"),
            ("Rohan Verma", "rohan.verma@example.com", "+91 9934567890", "Indiranagar, Bengaluru"),
            ("Ananya Sen", "ananya.sen@example.com", "+91 9845678901", "Salt Lake, Kolkata")
        ]
        cursor.executemany(
            """
            INSERT INTO members (full_name, email, phone, address)
            VALUES (?, ?, ?, ?)
            """,
            sample_members
        )

        now = datetime.now()
        issue_1 = (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
        due_1 = (now + timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S")

        issue_2 = (now - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")
        due_2 = (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")

        issue_3 = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        due_3 = (now - timedelta(days=16)).strftime("%Y-%m-%d %H:%M:%S")
        return_3 = (now - timedelta(days=18)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
            VALUES (1, 1, ?, ?, 'Issued')
            """,
            (issue_1, due_1)
        )
        cursor.execute(
            """
            INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
            VALUES (2, 2, ?, ?, 'Overdue')
            """,
            (issue_2, due_2)
        )
        cursor.execute(
            """
            INSERT INTO transactions (book_id, member_id, issue_date, due_date, return_date, status)
            VALUES (5, 3, ?, ?, ?, 'Returned')
            """,
            (issue_3, due_3, return_3)
        )
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

@contextlib.contextmanager
def execute_query(query, params=(), commit=False):
    """Context manager that executes a query, optionally commits, and always closes the connection."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
        yield cursor, conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
