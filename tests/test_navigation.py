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
    nav.register_views({"Dashboard": DummyView, "Books": DummyView})
    nav.navigate("Dashboard")
    assert root.active_sidebar == "Dashboard"
    nav.navigate_home()
    assert root.active_sidebar == "Dashboard"
    nav.navigate("Books")
    assert root.active_sidebar == "Books"
    root.destroy()
