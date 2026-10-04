import pytest
from database.db_connection import initialize_database
from controllers.book_controller import BookController
from controllers.member_controller import MemberController
from controllers.transaction_controller import TransactionController
import os
import tempfile
import database.db_connection

@pytest.fixture(autouse=True)
def setup_db():
    fd, temp_db = tempfile.mkstemp()
    os.close(fd)
    database.db_connection.DB_PATH = temp_db
    initialize_database()
    yield
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

def test_add_and_get_member():
    MemberController.add_member("John Doe", "john@test.com", "12345", "123 St")
    members = MemberController.get_all_members()
    assert len(members) == 1
    assert members[0]['full_name'] == "John Doe"
