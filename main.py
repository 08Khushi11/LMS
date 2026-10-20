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

APP_WIDTH = 1100
APP_HEIGHT = 750

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Library Management System — Q14: Improve Navigation")
        self.resizable(True, True)
        self.minsize(900, 650)

        # Center window on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(10, (screen_w - APP_WIDTH) // 2)
        y = max(10, (screen_h - APP_HEIGHT) // 2)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")

        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar (Top/Sidebar Navigation Bar)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)  # Push version label to bottom

        # Sidebar logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="📚 Library\nSystem",
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="center"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 15))

        # Separator line under logo
        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=("gray70", "gray30")).grid(
            row=1, column=0, sticky="ew", padx=15, pady=(0, 5)
        )

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

        # Shortcuts / Help button
        btn_help = ctk.CTkButton(
            self.sidebar_frame, text="⌨️  Shortcuts & Help",
            command=self.show_shortcuts_help,
            fg_color="transparent", text_color=("gray30", "gray70"),
            hover_color=("gray70", "gray30"),
            anchor="w", font=ctk.CTkFont(size=12)
        )
        btn_help.grid(row=8, column=0, padx=10, pady=(15, 5), sticky="ew")

        # Version label at bottom of sidebar
        ctk.CTkLabel(
            self.sidebar_frame,
            text="v1.0  |  SQLite  |  TQM Q14",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        ).grid(row=10, column=0, padx=10, pady=(0, 10))

        # Start at Home/Dashboard
        self.nav_controller.navigate_home()

    def _create_sidebar_buttons(self):
        buttons = [
            ("🏠  Dashboard", "Dashboard"),
            ("📖  Books", "Books"),
            ("👥  Members", "Members"),
            ("➕  Issue Book", "IssueBook"),
            ("↩️  Return Book", "ReturnBook"),
            ("📊  Reports", "Reports")
        ]

        for i, (text, view_name) in enumerate(buttons):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=text,
                command=lambda v=view_name: self.nav_controller.navigate(v),
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w", font=ctk.CTkFont(size=13)
            )
            btn.grid(row=i + 2, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[view_name] = btn

    def update_sidebar_active(self, view_name):
        """Highlights the active navigation button."""
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("gray75", "gray25"), font=ctk.CTkFont(size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", font=ctk.CTkFont(size=13))

    def show_shortcuts_help(self):
        """Displays keyboard shortcut help modal dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Keyboard Shortcuts & Help (TQM Q14)")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        dialog.transient(self)

        dialog.update_idletasks()
        try:
            pw = self.winfo_x()
            py = self.winfo_y()
            pw2 = self.winfo_width()
            py2 = self.winfo_height()
            dialog.geometry(f"450x420+{max(10, pw + (pw2 - 450) // 2)}+{max(10, py + (py2 - 420) // 2)}")
        except Exception:
            pass

        def _safe_grab():
            try:
                if dialog.winfo_exists():
                    dialog.grab_set()
            except Exception:
                pass
        dialog.after(150, _safe_grab)
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        ctk.CTkLabel(
            dialog, text="⌨️  Q14 Navigation Shortcuts",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        shortcuts = [
            ("Ctrl + D", "Open Dashboard (Home)"),
            ("Ctrl + B", "Open Books Management"),
            ("Ctrl + M", "Open Members Management"),
            ("Ctrl + I", "Open Issue Book"),
            ("Ctrl + R", "Open Return Book"),
            ("Ctrl + P", "Open Reports & Analytics"),
            ("Ctrl + F", "Focus Search Bar (Books / Members)"),
            ("Ctrl + N", "Open Add Form (Book / Member)"),
            ("Esc", "Close Dialog / Return to Dashboard"),
        ]

        frame = ctk.CTkFrame(dialog, fg_color=("gray90", "gray20"), corner_radius=8)
        frame.pack(fill="both", expand=True, padx=25, pady=10)

        for row, (key, desc) in enumerate(shortcuts):
            ctk.CTkLabel(
                frame, text=key, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1f538d", "#4da6ff")
            ).grid(row=row, column=0, padx=15, pady=4, sticky="w")

            ctk.CTkLabel(
                frame, text=desc, font=ctk.CTkFont(size=12),
                text_color=("gray20", "gray80")
            ).grid(row=row, column=1, padx=10, pady=4, sticky="w")

        ctk.CTkButton(
            dialog, text="Close", command=dialog.destroy, width=120, height=32
        ).pack(pady=(5, 15))

if __name__ == "__main__":
    initialize_database(seed_sample=True)
    app = MainApplication()
    app.mainloop()
