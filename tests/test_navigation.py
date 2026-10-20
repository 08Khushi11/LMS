import pytest
import customtkinter as ctk
from controllers.navigation_controller import NavigationController
from views.books import BooksView
from views.members import MembersView
from views.dashboard import DashboardView
from views.transactions import IssueBookView, ReturnBookView

class DummyView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.nav_controller = nav_controller

class DummyRoot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Do not render on screen during tests
        self.main_content_frame = ctk.CTkFrame(self)
        self.active_sidebar = None
        
    def update_sidebar_active(self, view_name):
        self.active_sidebar = view_name

def test_navigation_controller():
    root = DummyRoot()
    nav = NavigationController(root)
    
    nav.register_views({
        "Dashboard": DummyView,
        "Books": DummyView,
        "Members": DummyView
    })
    
    # Test navigation routing
    nav.navigate("Dashboard")
    assert root.active_sidebar == "Dashboard"
    assert isinstance(nav.current_frame, DummyView)
    assert nav.current_view_name == "Dashboard"
    
    # Test navigation Home
    nav.navigate_home()
    assert root.active_sidebar == "Dashboard"
    
    # Test different view
    nav.navigate("Books")
    assert root.active_sidebar == "Books"
    assert nav.current_view_name == "Books"

    # Test Members view
    nav.navigate("Members")
    assert root.active_sidebar == "Members"

    # Test navigating to unknown view does not crash
    nav.navigate("NonExistentView")
    assert root.active_sidebar == "Members"  # remains unchanged
    
    root.destroy()

def test_real_views_instantiation_no_blank_screen():
    root = DummyRoot()
    nav = NavigationController(root)
    nav.register_views({
        "Dashboard": DashboardView,
        "Books": BooksView,
        "Members": MembersView,
        "IssueBook": IssueBookView,
        "ReturnBook": ReturnBookView
    })

    views = ["Dashboard", "Books", "Members", "IssueBook", "ReturnBook"]
    for v in views:
        nav.navigate(v)
        root.update()
        assert nav.current_frame is not None, f"View {v} resulted in empty frame"
        assert nav.current_view_name == v

    # Verify BooksView methods
    nav.navigate("Books")
    root.update()
    assert isinstance(nav.current_frame, BooksView)
    assert hasattr(nav.current_frame, 'focus_search')
    assert hasattr(nav.current_frame, 'open_add_dialog')
    nav.current_frame.focus_search()

    # Verify MembersView methods
    nav.navigate("Members")
    root.update()
    assert isinstance(nav.current_frame, MembersView)
    assert hasattr(nav.current_frame, 'focus_search')
    assert hasattr(nav.current_frame, 'open_add_dialog')
    nav.current_frame.focus_search()

    root.destroy()
