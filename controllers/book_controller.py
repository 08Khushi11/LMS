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

    @staticmethod
    def update_book(book_id, isbn, title, author, category, publisher, total_copies):
        total_copies = int(total_copies)
        cursor, conn = execute_query("SELECT total_copies, available_copies FROM books WHERE book_id = ?", (book_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("Book not found")
        old_total, available = row['total_copies'], row['available_copies']
        conn.close()
        issued = old_total - available
        new_available = total_copies - issued
        if new_available < 0:
            raise ValueError("Cannot reduce total copies below currently issued copies.")
        query = """
            UPDATE books SET
            isbn = ?, title = ?, author = ?, category = ?, publisher = ?, total_copies = ?, available_copies = ?
            WHERE book_id = ?
        """
        cursor, conn = execute_query(query, (isbn, title, author, category, publisher, total_copies, new_available, book_id), commit=True)
        conn.close()

    @staticmethod
    def delete_book(book_id):
        cursor, conn = execute_query("SELECT total_copies, available_copies FROM books WHERE book_id = ?", (book_id,))
        row = cursor.fetchone()
        if row and row['total_copies'] != row['available_copies']:
            conn.close()
            raise ValueError("Cannot delete book while copies are issued.")
        conn.close()
        cursor, conn = execute_query("DELETE FROM books WHERE book_id = ?", (book_id,), commit=True)
        conn.close()
