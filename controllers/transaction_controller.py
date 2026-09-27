from database.db_connection import execute_query
from datetime import datetime, timedelta

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

    @staticmethod
    def issue_book(book_id, member_id, days_to_due=14):
        cursor, conn = execute_query("SELECT * FROM members WHERE member_id = ?", (member_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError("Invalid Member ID.")
        conn.close()

        cursor, conn = execute_query("SELECT available_copies FROM books WHERE book_id = ?", (book_id,))
        book_row = cursor.fetchone()
        if not book_row:
            conn.close()
            raise ValueError("Invalid Book ID.")
        if book_row['available_copies'] <= 0:
            conn.close()
            raise ValueError("No available copies to issue.")
        conn.close()

        cursor, conn = execute_query("SELECT * FROM transactions WHERE book_id = ? AND member_id = ? AND status = 'Issued'", (book_id, member_id))
        if cursor.fetchone():
            conn.close()
            raise ValueError("Member already has a copy of this book issued.")
        conn.close()

        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=days_to_due)

        query = """
            INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
            VALUES (?, ?, ?, ?, 'Issued')
        """
        cursor, conn = execute_query(query, (book_id, member_id, issue_date.isoformat(), due_date.isoformat()))
        conn.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (book_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def return_book(transaction_id):
        cursor, conn = execute_query("SELECT book_id, status FROM transactions WHERE transaction_id = ?", (transaction_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("Transaction not found.")
        if row['status'] != 'Issued':
            conn.close()
            raise ValueError("Book is not currently issued on this transaction.")
        book_id = row['book_id']
        conn.close()
        return_date = datetime.now().isoformat()
        cursor, conn = execute_query("UPDATE transactions SET status = 'Returned', return_date = ? WHERE transaction_id = ?", (return_date, transaction_id))
        conn.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?", (book_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_active_transactions():
        query = """
            SELECT t.transaction_id, b.title, m.full_name, t.issue_date, t.due_date 
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            JOIN members m ON t.member_id = m.member_id
            WHERE t.status = 'Issued'
            ORDER BY t.issue_date DESC
        """
        cursor, conn = execute_query(query)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
