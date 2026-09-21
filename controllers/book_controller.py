from database.db_connection import execute_query

class BookController:
    @staticmethod
    def get_all_books():
        cursor, conn = execute_query("SELECT * FROM books ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
