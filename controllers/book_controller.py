import sqlite3
from database.db_connection import fetch_all, fetch_one, execute_write, get_db

class BookController:
    @staticmethod
    def get_all_books():
        books = fetch_all("SELECT * FROM books ORDER BY created_at DESC")
        for b in books:
            b['issued_copies'] = max(0, b['total_copies'] - b['available_copies'])
        return books

    @staticmethod
    def get_book_by_id(book_id):
        try:
            bid = int(book_id)
        except (ValueError, TypeError):
            return None
        book = fetch_one("SELECT * FROM books WHERE book_id = ?", (bid,))
        if book:
            book['issued_copies'] = max(0, book['total_copies'] - book['available_copies'])
        return book

    @staticmethod
    def get_book_by_title(title):
        clean = str(title).strip()
        if not clean:
            return None
        book = fetch_one("SELECT * FROM books WHERE LOWER(title) = LOWER(?) LIMIT 1", (clean,))
        if not book:
            # Try fuzzy/partial match
            book = fetch_one("SELECT * FROM books WHERE title LIKE ? LIMIT 1", (f"%{clean}%",))
        if book:
            book['issued_copies'] = max(0, book['total_copies'] - book['available_copies'])
        return book

    @staticmethod
    def search_books_autocomplete(query_text, limit=15):
        clean = str(query_text).strip()
        if not clean:
            books = fetch_all("SELECT * FROM books ORDER BY title ASC LIMIT ?", (limit,))
        else:
            like = f"%{clean}%"
            # Allow searching by title, author, isbn, or book_id
            try:
                bid = int(clean)
            except ValueError:
                bid = -1
            query = """
                SELECT * FROM books 
                WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ? OR book_id = ?
                ORDER BY 
                    CASE WHEN LOWER(title) LIKE LOWER(?) THEN 1 ELSE 2 END,
                    title ASC
                LIMIT ?
            """
            books = fetch_all(query, (like, like, like, like, bid, f"{clean}%", limit))

        for b in books:
            b['issued_copies'] = max(0, b['total_copies'] - b['available_copies'])
        return books

    @staticmethod
    def add_book(isbn, title, author, category="", publisher="", total_copies=1):
        isbn = str(isbn).strip() if isbn else ""
        title = str(title).strip() if title else ""
        author = str(author).strip() if author else ""
        category = str(category).strip() if category else ""
        publisher = str(publisher).strip() if publisher else ""

        if not isbn:
            raise ValueError("ISBN is required.")
        if not title:
            raise ValueError("Book title is required.")
        if not author:
            raise ValueError("Author is required.")

        try:
            total_copies = int(total_copies)
        except (ValueError, TypeError):
            raise ValueError("Total copies must be a valid integer.")

        if total_copies < 0:
            raise ValueError("Total copies cannot be negative.")

        existing = fetch_one("SELECT book_id FROM books WHERE isbn = ?", (isbn,))
        if existing:
            raise ValueError(f"A book with ISBN '{isbn}' already exists.")

        query = """
            INSERT INTO books (isbn, title, author, category, publisher, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return execute_write(query, (isbn, title, author, category, publisher, total_copies, total_copies))

    @staticmethod
    def update_book(book_id, isbn, title, author, category="", publisher="", total_copies=1):
        isbn = str(isbn).strip() if isbn else ""
        title = str(title).strip() if title else ""
        author = str(author).strip() if author else ""
        category = str(category).strip() if category else ""
        publisher = str(publisher).strip() if publisher else ""

        if not isbn:
            raise ValueError("ISBN is required.")
        if not title:
            raise ValueError("Book title is required.")
        if not author:
            raise ValueError("Author is required.")

        try:
            total_copies = int(total_copies)
        except (ValueError, TypeError):
            raise ValueError("Total copies must be a valid integer.")

        if total_copies < 0:
            raise ValueError("Total copies cannot be negative.")

        row = fetch_one("SELECT total_copies, available_copies FROM books WHERE book_id = ?", (book_id,))
        if not row:
            raise ValueError("Book not found.")

        # Check for duplicate ISBN on another book
        dup = fetch_one("SELECT book_id FROM books WHERE isbn = ? AND book_id != ?", (isbn, book_id))
        if dup:
            raise ValueError(f"Another book with ISBN '{isbn}' already exists.")

        old_total, available = row['total_copies'], row['available_copies']
        issued = old_total - available
        new_available = total_copies - issued

        if new_available < 0:
            raise ValueError(f"Cannot reduce total copies below currently issued copies ({issued}).")

        query = """
            UPDATE books SET
            isbn = ?, title = ?, author = ?, category = ?, publisher = ?, total_copies = ?, available_copies = ?
            WHERE book_id = ?
        """
        execute_write(query, (isbn, title, author, category, publisher, total_copies, new_available, book_id))

    @staticmethod
    def search_books(query_text):
        query = """
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?
            ORDER BY created_at DESC
        """
        like_text = f"%{str(query_text).strip()}%"
        books = fetch_all(query, (like_text, like_text, like_text, like_text))
        for b in books:
            b['issued_copies'] = max(0, b['total_copies'] - b['available_copies'])
        return books

    @staticmethod
    def delete_book(book_id):
        row = fetch_one("SELECT total_copies, available_copies FROM books WHERE book_id = ?", (book_id,))
        if not row:
            raise ValueError("Book not found.")
        if row['total_copies'] != row['available_copies']:
            raise ValueError("Cannot delete book while copies are currently issued.")

        execute_write("DELETE FROM books WHERE book_id = ?", (book_id,))
