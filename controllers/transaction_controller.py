from datetime import datetime, timedelta
from database.db_connection import fetch_all, fetch_one, execute_write, get_db

class TransactionController:
    @staticmethod
    def check_overdue_transactions():
        """Updates active issued transactions that passed their due date to Overdue status."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_db() as conn:
            conn.execute(
                "UPDATE transactions SET status = 'Overdue' WHERE status = 'Issued' AND due_date < ?",
                (now_str,)
            )
            conn.commit()

    @staticmethod
    def get_dashboard_stats():
        TransactionController.check_overdue_transactions()

        total_books_row = fetch_one("SELECT COUNT(*) as count FROM books")
        total_members_row = fetch_one("SELECT COUNT(*) as count FROM members")
        issued_row = fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status IN ('Issued', 'Overdue')")
        overdue_row = fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'Overdue'")

        return {
            "total_books": total_books_row['count'] if total_books_row else 0,
            "total_members": total_members_row['count'] if total_members_row else 0,
            "currently_issued": issued_row['count'] if issued_row else 0,
            "overdue_books": overdue_row['count'] if overdue_row else 0
        }

    @staticmethod
    def issue_book(book_id, member_id, days_to_due=14):
        try:
            book_id = int(book_id)
            member_id = int(member_id)
            days_to_due = int(days_to_due)
        except (ValueError, TypeError):
            raise ValueError("Book ID and Member ID must be valid integers.")

        # Validate member
        member = fetch_one("SELECT * FROM members WHERE member_id = ?", (member_id,))
        if not member:
            raise ValueError("Invalid Member ID: Member not found.")

        # Check book availability
        book = fetch_one("SELECT available_copies FROM books WHERE book_id = ?", (book_id,))
        if not book:
            raise ValueError("Invalid Book ID: Book not found.")
        if book['available_copies'] <= 0:
            raise ValueError("No available copies to issue.")

        # Check if member already has this book issued or overdue
        existing = fetch_one(
            "SELECT * FROM transactions WHERE book_id = ? AND member_id = ? AND status IN ('Issued', 'Overdue')",
            (book_id, member_id)
        )
        if existing:
            raise ValueError("Member already has a copy of this book issued.")

        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=days_to_due)

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
                VALUES (?, ?, ?, ?, 'Issued')
                """,
                (book_id, member_id, issue_date.strftime("%Y-%m-%d %H:%M:%S"), due_date.strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.execute(
                "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?",
                (book_id,)
            )
            conn.commit()

    @staticmethod
    def return_book(transaction_id):
        try:
            transaction_id = int(transaction_id)
        except (ValueError, TypeError):
            raise ValueError("Transaction ID must be a valid integer.")

        row = fetch_one(
            "SELECT book_id, status FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        )
        if not row:
            raise ValueError("Transaction not found.")
        if row['status'] not in ('Issued', 'Overdue'):
            raise ValueError("Book is not currently issued on this transaction.")

        book_id = row['book_id']
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with get_db() as conn:
            conn.execute(
                "UPDATE transactions SET status = 'Returned', return_date = ? WHERE transaction_id = ?",
                (return_date, transaction_id)
            )
            conn.execute(
                "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?",
                (book_id,)
            )
            conn.commit()

    @staticmethod
    def get_active_transactions():
        TransactionController.check_overdue_transactions()
        query = """
            SELECT t.transaction_id, b.title, m.full_name, t.issue_date, t.due_date, t.status 
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            JOIN members m ON t.member_id = m.member_id
            WHERE t.status IN ('Issued', 'Overdue')
            ORDER BY t.due_date ASC
        """
        return fetch_all(query)

