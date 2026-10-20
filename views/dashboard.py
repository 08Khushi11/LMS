import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller

        # Breadcrumb
        BreadcrumbHeader(self, nav_controller, [("🏠 Home", None)]).pack(anchor="w", padx=20, pady=(20, 10))

        lbl_title = ctk.CTkLabel(self, text="Library Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_title.pack(anchor="w", padx=20, pady=(0, 5))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self, text="Loading stats...",
            font=ctk.CTkFont(size=12), text_color="gray60"
        )
        self.subtitle_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Stats Grid frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=5)

        # Action Tiles frame
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=20)

        lbl_actions = ctk.CTkLabel(actions_frame, text="Quick Actions & Operations", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_actions.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        self.create_action_tile(actions_frame, "➕ Add New Book", "Books", 1, 0, open_add=True)
        self.create_action_tile(actions_frame, "👤 Register Member", "Members", 1, 1, open_add=True)
        self.create_action_tile(actions_frame, "📤 Issue Book", "IssueBook", 1, 2)
        self.create_action_tile(actions_frame, "📥 Return Book", "ReturnBook", 1, 3)
        self.create_action_tile(actions_frame, "📖 View All Books", "Books", 2, 0)
        self.create_action_tile(actions_frame, "📊 Reports & Analytics", "Reports", 2, 1)

        # Load stats
        self.refresh_stats()

    def refresh_stats(self):
        """Fetch latest stats and rebuild stat tiles."""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        try:
            stats = TransactionController.get_dashboard_stats()
        except Exception:
            stats = {'total_books': 0, 'total_members': 0, 'currently_issued': 0, 'overdue_books': 0}

        from datetime import datetime
        self.subtitle_label.configure(
            text=f"Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        )

        stat_items = [
            ("📚 Total Books", stats['total_books'], "Books", "#1f538d"),
            ("👥 Members", stats['total_members'], "Members", "#2fa572"),
            ("📤 Issued", stats['currently_issued'], "ReturnBook", "#d68a27"),
            ("⚠️ Overdue", stats['overdue_books'], "Reports", "#c23b22"),
        ]

        for col, (title, value, nav_target, color) in enumerate(stat_items):
            self.create_stat_tile(self.stats_frame, title, value, 0, col, nav_target, color)

    def create_stat_tile(self, parent, title, value, row, col, nav_target, color="#1f538d"):
        frame = ctk.CTkFrame(parent, corner_radius=12, width=220, height=110, fg_color=color)
        frame.grid(row=row, column=col, padx=10, pady=10)
        frame.grid_propagate(False)

        lbl_val = ctk.CTkLabel(
            frame, text=str(value),
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        lbl_val.place(relx=0.5, rely=0.38, anchor="center")

        lbl_title = ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=13),
            text_color="#dddddd"
        )
        lbl_title.place(relx=0.5, rely=0.75, anchor="center")

        # Make clickable
        for w in [frame, lbl_val, lbl_title]:
            w.bind("<Button-1>", lambda e, t=nav_target: self.nav_controller.navigate(t))
            w.configure(cursor="hand2")

    def create_action_tile(self, parent, title, nav_target, row, col, **nav_kwargs):
        btn = ctk.CTkButton(
            parent, text=title, height=80, width=200,
            font=ctk.CTkFont(size=15),
            command=lambda t=nav_target, k=nav_kwargs: self.nav_controller.navigate(t, **k)
        )
        btn.grid(row=row, column=col, padx=10, pady=10)
