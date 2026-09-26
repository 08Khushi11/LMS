from database.db_connection import execute_query

class TransactionController:
    @staticmethod
    def get_dashboard_stats():
        cursor, conn1 = execute_query("SELECT COUNT(*) as count FROM books")
        total_books = cursor.fetchone()['count']
        conn1.close()

        cursor, conn2 = execute_query("SELECT COUNT(*) as count FROM members")
        total_members = cursor.fetchone()['count']
        conn2.close()

        cursor, conn3 = execute_query("SELECT COUNT(*) as count FROM transactions WHERE status = 'Issued'")
        currently_issued = cursor.fetchone()['count']
        conn3.close()

        cursor, conn4 = execute_query("SELECT COUNT(*) as count FROM transactions WHERE status = 'Issued' AND due_date < datetime('now')")
        overdue_books = cursor.fetchone()['count']
        conn4.close()

        return {
            "total_books": total_books,
            "total_members": total_members,
            "currently_issued": currently_issued,
            "overdue_books": overdue_books
        }
