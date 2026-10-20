import pytest
from database.db_connection import initialize_database, get_db
from controllers.book_controller import BookController
from controllers.member_controller import MemberController
from controllers.transaction_controller import TransactionController
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import database.db_connection

@pytest.fixture(autouse=True)
def setup_db():
    orig_db = database.db_connection.DB_PATH
    fd, temp_db = tempfile.mkstemp()
    os.close(fd)
    
    database.db_connection.DB_PATH = temp_db
    initialize_database()
    
    yield
    
    database.db_connection.DB_PATH = orig_db
    if os.path.exists(temp_db):
        try:
            os.remove(temp_db)
        except Exception:
            pass

def test_add_and_get_book():
    BookController.add_book("123", "Test Book", "Author", "Sci-Fi", "Pub", 5)
    books = BookController.get_all_books()
    assert len(books) == 1
    assert books[0]['title'] == "Test Book"
    assert books[0]['available_copies'] == 5

def test_add_book_validation():
    with pytest.raises(ValueError, match="ISBN is required"):
        BookController.add_book("", "Title", "Author", total_copies=1)

    with pytest.raises(ValueError, match="Book title is required"):
        BookController.add_book("123", "", "Author", total_copies=1)

    with pytest.raises(ValueError, match="Author is required"):
        BookController.add_book("123", "Title", "", total_copies=1)

    with pytest.raises(ValueError, match="cannot be negative"):
        BookController.add_book("123", "Title", "Author", total_copies=-2)

    BookController.add_book("DUP-1", "Book 1", "Author", total_copies=1)
    with pytest.raises(ValueError, match="already exists"):
        BookController.add_book("DUP-1", "Book 2", "Author", total_copies=1)

def test_update_book():
    BookController.add_book("100", "Original Title", "Author A", "Cat", "Pub", 5)
    books = BookController.get_all_books()
    book_id = books[0]['book_id']

    BookController.update_book(book_id, "100", "Updated Title", "Author B", "Fiction", "New Pub", 10)
    updated = BookController.get_all_books()
    assert updated[0]['title'] == "Updated Title"
    assert updated[0]['author'] == "Author B"
    assert updated[0]['total_copies'] == 10
    assert updated[0]['available_copies'] == 10

def test_search_and_delete_book():
    BookController.add_book("111", "Clean Code", "Robert Martin", "Tech", "Prentice", 3)
    BookController.add_book("222", "The Hobbit", "J.R.R. Tolkien", "Fantasy", "Allen", 2)

    results = BookController.search_books("Clean")
    assert len(results) == 1
    assert results[0]['isbn'] == "111"

    book_id = results[0]['book_id']
    BookController.delete_book(book_id)
    assert len(BookController.get_all_books()) == 1

def test_add_and_get_member():
    MemberController.add_member("John Doe", "john@test.com", "12345", "123 St")
    members = MemberController.get_all_members()
    assert len(members) == 1
    assert members[0]['full_name'] == "John Doe"

def test_member_validation_and_update():
    with pytest.raises(ValueError, match="Full name is required"):
        MemberController.add_member("", "valid@email.com")

    with pytest.raises(ValueError, match="Invalid email format"):
        MemberController.add_member("Jane", "bad-email")

    MemberController.add_member("Alice", "alice@example.com", "98765", "Park Ave")
    members = MemberController.get_all_members()
    member_id = members[0]['member_id']

    MemberController.update_member(member_id, "Alice Smith", "alice.smith@example.com", "99999", "5th Ave")
    updated = MemberController.get_all_members()
    assert updated[0]['full_name'] == "Alice Smith"
    assert updated[0]['phone'] == "99999"

def test_issue_and_return_book():
    BookController.add_book("123", "Test Book", "Author", "Sci-Fi", "Pub", 1)
    MemberController.add_member("John Doe", "john@test.com", "12345", "123 St")
    
    books = BookController.get_all_books()
    members = MemberController.get_all_members()
    
    book_id = books[0]['book_id']
    member_id = members[0]['member_id']
    
    # Issue
    TransactionController.issue_book(book_id, member_id)
    
    books_after_issue = BookController.get_all_books()
    assert books_after_issue[0]['available_copies'] == 0
    
    active_txns = TransactionController.get_active_transactions()
    assert len(active_txns) == 1
    txn_id = active_txns[0]['transaction_id']
    
    # Return
    TransactionController.return_book(txn_id)
    
    books_after_return = BookController.get_all_books()
    assert books_after_return[0]['available_copies'] == 1
    
    active_txns_after = TransactionController.get_active_transactions()
    assert len(active_txns_after) == 0

def test_overissue_prevents():
    BookController.add_book("123", "Test Book", "Author", "Sci-Fi", "Pub", 1)
    MemberController.add_member("John Doe", "john@test.com", "12345", "123 St")
    MemberController.add_member("Jane Doe", "jane@test.com", "54321", "124 St")
    
    books = BookController.get_all_books()
    members = MemberController.get_all_members()
    
    book_id = books[0]['book_id']
    member_id_1 = members[0]['member_id']
    member_id_2 = members[1]['member_id']
    
    TransactionController.issue_book(book_id, member_id_1)
    
    with pytest.raises(ValueError, match="No available copies to issue"):
        TransactionController.issue_book(book_id, member_id_2)

def test_cannot_delete_book_or_member_with_active_loans():
    BookController.add_book("999", "Locked Book", "Author", total_copies=2)
    MemberController.add_member("Borrower", "borrower@test.com")
    
    book = BookController.get_all_books()[0]
    member = MemberController.get_all_members()[0]
    
    TransactionController.issue_book(book['book_id'], member['member_id'])
    
    with pytest.raises(ValueError, match="Cannot delete book while copies are currently issued"):
        BookController.delete_book(book['book_id'])
        
    with pytest.raises(ValueError, match="Cannot delete member with currently issued or overdue books"):
        MemberController.delete_member(member['member_id'])

def test_overdue_and_dashboard_stats():
    BookController.add_book("888", "Due Book", "Author", total_copies=2)
    MemberController.add_member("Late Member", "late@test.com")
    
    book = BookController.get_all_books()[0]
    member = MemberController.get_all_members()[0]
    
    # Issue book with negative days_to_due to simulate overdue
    TransactionController.issue_book(book['book_id'], member['member_id'], days_to_due=-3)
    
    stats = TransactionController.get_dashboard_stats()
    assert stats['total_books'] == 1
    assert stats['total_members'] == 1
    assert stats['currently_issued'] == 1
    assert stats['overdue_books'] == 1

    active_txns = TransactionController.get_active_transactions()
    assert len(active_txns) == 1
    assert active_txns[0]['status'] == 'Overdue'

    # Ensure returning an overdue book works
    TransactionController.return_book(active_txns[0]['transaction_id'])
    stats_after = TransactionController.get_dashboard_stats()
    assert stats_after['currently_issued'] == 0
    assert stats_after['overdue_books'] == 0

