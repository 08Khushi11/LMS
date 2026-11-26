import pytest
from database.db_connection import initialize_database
import database.db_connection
from controllers.book_controller import BookController
from controllers.member_controller import MemberController
from controllers.transaction_controller import TransactionController
import os
import tempfile

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

def test_member_autocomplete_and_search_by_name():
    MemberController.add_member("Kamlesh Tewari", "kamlesh@test.com", "9876543210")
    MemberController.add_member("Aarav Sharma", "aarav@test.com", "9812345678")
    
    # Search by exact name
    m = MemberController.get_member_by_name("Kamlesh Tewari")
    assert m is not None
    assert m['full_name'] == "Kamlesh Tewari"
    
    # Search by partial name
    m_part = MemberController.get_member_by_name("Kamlesh")
    assert m_part is not None
    assert m_part['full_name'] == "Kamlesh Tewari"
    
    # Autocomplete list
    results = MemberController.search_members_autocomplete("Aar")
    assert len(results) == 1
    assert results[0]['full_name'] == "Aarav Sharma"

def test_book_autocomplete_and_search_by_title():
    BookController.add_book("ISBN-1", "Clean Code", "Robert Martin", "CS", "Prentice", 5)
    BookController.add_book("ISBN-2", "The Hobbit", "J.R.R. Tolkien", "Fantasy", "Allen", 3)
    
    # Search by title
    b = BookController.get_book_by_title("Clean Code")
    assert b is not None
    assert b['title'] == "Clean Code"
    assert b['total_copies'] == 5
    assert b['available_copies'] == 5
    assert b['issued_copies'] == 0
    
    # Search partial
    b_part = BookController.get_book_by_title("Hobbit")
    assert b_part is not None
    assert b_part['title'] == "The Hobbit"
    
    # Autocomplete
    results = BookController.search_books_autocomplete("Clean")
    assert len(results) == 1
    assert results[0]['title'] == "Clean Code"

def test_book_availability_updates_on_issue_and_return():
    BookController.add_book("ISBN-10", "Python Crash Course", "Eric Matthes", "Programming", "No Starch", 3)
    MemberController.add_member("Priya Patel", "priya@test.com", "9998887776")
    
    books = BookController.get_all_books()
    members = MemberController.get_all_members()
    bid = books[0]['book_id']
    mid = members[0]['member_id']
    
    # Initial state
    b_init = BookController.get_book_by_id(bid)
    assert b_init['total_copies'] == 3
    assert b_init['available_copies'] == 3
    assert b_init['issued_copies'] == 0
    
    # Issue book
    txn = TransactionController.issue_book(bid, mid, days_to_due=14)
    assert txn['book_title'] == "Python Crash Course"
    assert txn['remaining_available'] == 2
    
    # Check updated book stats
    b_after_issue = BookController.get_book_by_id(bid)
    assert b_after_issue['total_copies'] == 3
    assert b_after_issue['available_copies'] == 2
    assert b_after_issue['issued_copies'] == 1
    
    # Return book
    ret = TransactionController.return_book(txn['transaction_id'])
    assert ret['book_title'] == "Python Crash Course"
    
    # Check restored book stats
    b_after_return = BookController.get_book_by_id(bid)
    assert b_after_return['total_copies'] == 3
    assert b_after_return['available_copies'] == 3
    assert b_after_return['issued_copies'] == 0

def test_prevent_issue_when_out_of_stock():
    BookController.add_book("ISBN-STOCK", "Single Copy Rare Book", "Author", "Rare", "Publisher", 1)
    MemberController.add_member("User 1", "u1@test.com")
    MemberController.add_member("User 2", "u2@test.com")
    
    books = BookController.get_all_books()
    members = MemberController.get_all_members()
    bid = books[0]['book_id']
    mid1 = members[0]['member_id']
    mid2 = members[1]['member_id']
    
    # First issue succeeds
    TransactionController.issue_book(bid, mid1)
    
    # Second issue must fail due to 0 available copies
    with pytest.raises(ValueError, match="No available copies to issue"):
        TransactionController.issue_book(bid, mid2)

def test_prevent_duplicate_issue_to_same_member():
    BookController.add_book("ISBN-MULTI", "Popular Book", "Author", "Fiction", "Publisher", 5)
    MemberController.add_member("Single User", "single@test.com")
    
    books = BookController.get_all_books()
    members = MemberController.get_all_members()
    bid = books[0]['book_id']
    mid = members[0]['member_id']
    
    # First issue succeeds
    TransactionController.issue_book(bid, mid)
    
    # Second issue to same member must fail
    with pytest.raises(ValueError, match="already has an active copy"):
        TransactionController.issue_book(bid, mid)

def test_member_active_loans_and_filter():
    BookController.add_book("B1", "Algorithms 1", "Cormen", "CS", "MIT", 2)
    BookController.add_book("B2", "Algorithms 2", "Cormen", "CS", "MIT", 2)
    MemberController.add_member("Rohan Verma", "rohan@test.com")
    
    books = BookController.get_all_books()
    member = MemberController.get_all_members()[0]
    mid = member['member_id']
    
    TransactionController.issue_book(books[0]['book_id'], mid)
    TransactionController.issue_book(books[1]['book_id'], mid)
    
    active_loans = TransactionController.get_member_active_loans(mid)
    assert len(active_loans) == 2
    assert any(a['title'] == "Algorithms 1" for a in active_loans)
    assert any(a['title'] == "Algorithms 2" for a in active_loans)
    
    # Test searching active transactions by member name
    found_by_name = TransactionController.get_active_transactions("Rohan")
    assert len(found_by_name) == 2
    
    # Test searching active transactions by book title
    found_by_title = TransactionController.get_active_transactions("Algorithms 1")
    assert len(found_by_title) == 1
    assert found_by_title[0]['title'] == "Algorithms 1"

def test_invalid_member_or_book_raises():
    with pytest.raises(ValueError, match="Invalid Member ID"):
        TransactionController.issue_book(1, 99999)
        
    MemberController.add_member("Valid Member", "valid@test.com")
    m = MemberController.get_all_members()[0]
    with pytest.raises(ValueError, match="Invalid Book ID"):
        TransactionController.issue_book(99999, m['member_id'])
