from database.db_connection import execute_query

class BookController:
    @staticmethod
    def get_all_books():
        cursor, conn = execute_query("SELECT * FROM books ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def add_book(isbn, title, author, category, publisher, total_copies):
        total_copies = int(total_copies)
        if total_copies < 0:
            raise ValueError("Total copies cannot be negative.")
        query = """
            INSERT INTO books (isbn, title, author, category, publisher, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor, conn = execute_query(query, (isbn, title, author, category, publisher, total_copies, total_copies), commit=True)
        conn.close()
