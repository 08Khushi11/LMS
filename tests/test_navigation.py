import pytest
import customtkinter as ctk
from controllers.navigation_controller import NavigationController

class DummyView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.nav_controller = nav_controller

class DummyRoot(ctk.CTk):
    def __init__(self):
        super().__init__()
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
        "Reports": DummyView
    })
    
    # Test navigation routing
    nav.navigate("Dashboard")
    assert root.active_sidebar == "Dashboard"
    assert isinstance(nav.current_frame, DummyView)
    
    # Test navigation Home
    nav.navigate_home()
    assert root.active_sidebar == "Dashboard"
    
    # Test different view
    nav.navigate("Books")
    assert root.active_sidebar == "Books"

    # Test Reports view
    nav.navigate("Reports")
    assert root.active_sidebar == "Reports"

    # Test navigating to unknown view does not crash
    nav.navigate("NonExistentView")
    assert root.active_sidebar == "Reports"  # remains unchanged
    
    # Cleanup
    root.destroy()

