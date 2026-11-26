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
        TransactionController.check_overdue_transactions()
        try:
            book_id = int(book_id)
            member_id = int(member_id)
            days_to_due = int(days_to_due)
        except (ValueError, TypeError):
            raise ValueError("Book ID, Member ID, and Loan Duration must be valid integers.")

        # Validate member
        member = fetch_one("SELECT * FROM members WHERE member_id = ?", (member_id,))
        if not member:
            raise ValueError(f"Invalid Member ID ({member_id}): Member does not exist in database.")

        # Check book availability
        book = fetch_one("SELECT * FROM books WHERE book_id = ?", (book_id,))
        if not book:
            raise ValueError(f"Invalid Book ID ({book_id}): Book does not exist in database.")
        if book['available_copies'] <= 0:
            raise ValueError(
                f"No available copies to issue: Cannot issue '{book['title']}' (0 of {book['total_copies']} available in stock)."
            )

        # Check if member already has this book issued or overdue
        existing = fetch_one(
            "SELECT * FROM transactions WHERE book_id = ? AND member_id = ? AND status IN ('Issued', 'Overdue')",
            (book_id, member_id)
        )
        if existing:
            raise ValueError(f"Member '{member['full_name']}' already has an active copy of '{book['title']}' on loan.")

        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=days_to_due)
        issue_str = issue_date.strftime("%Y-%m-%d %H:%M:%S")
        due_str = due_date.strftime("%Y-%m-%d %H:%M:%S")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
                VALUES (?, ?, ?, ?, 'Issued')
                """,
                (book_id, member_id, issue_str, due_str)
            )
            txn_id = cursor.lastrowid
            cursor.execute(
                "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?",
                (book_id,)
            )
            conn.commit()

        return {
            "transaction_id": txn_id,
            "book_id": book_id,
            "book_title": book['title'],
            "member_id": member_id,
            "member_name": member['full_name'],
            "issue_date": issue_str,
            "due_date": due_str,
            "remaining_available": book['available_copies'] - 1
        }

    @staticmethod
    def return_book(transaction_id):
        TransactionController.check_overdue_transactions()
        try:
            transaction_id = int(transaction_id)
        except (ValueError, TypeError):
            raise ValueError("Transaction ID must be a valid integer.")

        row = fetch_one(
            """
            SELECT t.*, b.title as book_title, m.full_name as member_name 
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            JOIN members m ON t.member_id = m.member_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        )
        if not row:
            raise ValueError(f"Transaction ID #{transaction_id} not found in database.")
        if row['status'] not in ('Issued', 'Overdue'):
            raise ValueError(f"Transaction #{transaction_id} is already marked as '{row['status']}'.")

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

        return {
            "transaction_id": transaction_id,
            "book_title": row['book_title'],
            "member_name": row['member_name'],
            "return_date": return_date
        }

    @staticmethod
    def get_active_transactions(search_query=""):
        TransactionController.check_overdue_transactions()
        clean = str(search_query).strip()
        if not clean:
            query = """
                SELECT t.transaction_id, b.book_id, b.title, b.isbn, m.member_id, m.full_name, 
                       t.issue_date, t.due_date, t.status 
                FROM transactions t
                JOIN books b ON t.book_id = b.book_id
                JOIN members m ON t.member_id = m.member_id
                WHERE t.status IN ('Issued', 'Overdue')
                ORDER BY t.due_date ASC
            """
            return fetch_all(query)
        else:
            like = f"%{clean}%"
            try:
                tid = int(clean)
            except ValueError:
                tid = -1
            query = """
                SELECT t.transaction_id, b.book_id, b.title, b.isbn, m.member_id, m.full_name, 
                       t.issue_date, t.due_date, t.status 
                FROM transactions t
                JOIN books b ON t.book_id = b.book_id
                JOIN members m ON t.member_id = m.member_id
                WHERE t.status IN ('Issued', 'Overdue')
                  AND (m.full_name LIKE ? OR b.title LIKE ? OR b.isbn LIKE ? OR t.transaction_id = ? OR m.member_id = ?)
                ORDER BY t.due_date ASC
            """
            return fetch_all(query, (like, like, like, tid, tid))

    @staticmethod
    def get_member_active_loans(member_id):
        """Retrieves all currently issued or overdue books for a specific member."""
        TransactionController.check_overdue_transactions()
        try:
            mid = int(member_id)
        except (ValueError, TypeError):
            return []

        query = """
            SELECT t.transaction_id, b.book_id, b.title, b.author, b.isbn,
                   t.issue_date, t.due_date, t.status
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            WHERE t.member_id = ? AND t.status IN ('Issued', 'Overdue')
            ORDER BY t.due_date ASC
        """
        return fetch_all(query, (mid,))

    @staticmethod
    def get_member_loan_history(member_id, limit=30):
        """Retrieves complete loan history (issued, returned, overdue) for a member."""
        try:
            mid = int(member_id)
        except (ValueError, TypeError):
            return []

        query = """
            SELECT t.transaction_id, b.title, b.author, 
                   t.issue_date, t.due_date, t.return_date, t.status
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            WHERE t.member_id = ?
            ORDER BY t.issue_date DESC
            LIMIT ?
        """
        return fetch_all(query, (mid, limit))

    @staticmethod
    def get_overdue_transactions():
        """Returns all overdue loans with calculated overdue days."""
        TransactionController.check_overdue_transactions()
        query = """
            SELECT t.transaction_id, b.book_id, b.title, m.member_id, m.full_name, m.phone,
                   t.issue_date, t.due_date, t.status
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            JOIN members m ON t.member_id = m.member_id
            WHERE t.status = 'Overdue'
            ORDER BY t.due_date ASC
        """
        return fetch_all(query)
