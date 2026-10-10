import customtkinter as ctk
from database.db_connection import initialize_database
from controllers.navigation_controller import NavigationController

# Import views
from views.dashboard import DashboardView
from views.books import BooksView
from views.members import MembersView
from views.transactions import IssueBookView, ReturnBookView
from views.reports import ReportsView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Library Management System")
        self.geometry("1024x768")
        self.minsize(800, 600)

        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar (Top/Side Navigation Bar)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Library System", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Setup navigation controller
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        
        self.nav_controller = NavigationController(self)
        
        # Register views
        self.nav_controller.register_views({
            "Dashboard": DashboardView,
            "Books": BooksView,
            "Members": MembersView,
            "IssueBook": IssueBookView,
            "ReturnBook": ReturnBookView,
            "Reports": ReportsView
        })

        self.nav_buttons = {}
        self._create_sidebar_buttons()

        # Start at Home/Dashboard
        self.nav_controller.navigate_home()

    def _create_sidebar_buttons(self):
        buttons = [
            ("Dashboard", "Dashboard"),
            ("Books", "Books"),
            ("Members", "Members"),
            ("Issue Book", "IssueBook"),
            ("Return Book", "ReturnBook"),
            ("Reports", "Reports")
        ]
        
        for i, (text, view_name) in enumerate(buttons):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=text,
                command=lambda v=view_name: self.nav_controller.navigate(v),
                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                anchor="w"
            )
            btn.grid(row=i+1, column=0, padx=20, pady=10, sticky="ew")
            self.nav_buttons[view_name] = btn

    def update_sidebar_active(self, view_name):
        """Highlights the active navigation button."""
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

if __name__ == "__main__":
    initialize_database()
    app = MainApplication()
    app.mainloop()
