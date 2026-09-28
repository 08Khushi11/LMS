import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        BreadcrumbHeader(self, nav_controller, [("Home", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        lbl_title = ctk.CTkLabel(self, text="Library Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_title.pack(anchor="w", padx=20, pady=(0, 20))
        stats = TransactionController.get_dashboard_stats()
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        self.create_stat_tile(stats_frame, "Total Books", stats['total_books'], 0, 0, "Books")
        self.create_stat_tile(stats_frame, "Registered Members", stats['total_members'], 0, 1, "Members")
        self.create_stat_tile(stats_frame, "Books Issued", stats['currently_issued'], 0, 2, "Reports")
        self.create_stat_tile(stats_frame, "Overdue Books", stats['overdue_books'], 0, 3, "Reports")

        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=20)
        lbl_actions = ctk.CTkLabel(actions_frame, text="Quick Actions", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_actions.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        self.create_action_tile(actions_frame, "Add New Book", "Books", 1, 0)
        self.create_action_tile(actions_frame, "Register Member", "Members", 1, 1)
        self.create_action_tile(actions_frame, "Issue Book", "IssueBook", 1, 2)
        self.create_action_tile(actions_frame, "Return Book", "ReturnBook", 1, 3)

    def create_stat_tile(self, parent, title, value, row, col, nav_target):
        frame = ctk.CTkFrame(parent, corner_radius=10, width=200, height=100)
        frame.grid(row=row, column=col, padx=10, pady=10)
        frame.grid_propagate(False)
        lbl_val = ctk.CTkLabel(frame, text=str(value), font=ctk.CTkFont(size=32, weight="bold"))
        lbl_val.place(relx=0.5, rely=0.4, anchor="center")
        lbl_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14))
        lbl_title.place(relx=0.5, rely=0.75, anchor="center")
        for w in [frame, lbl_val, lbl_title]:
            w.bind("<Button-1>", lambda e, t=nav_target: self.nav_controller.navigate(t))

    def create_action_tile(self, parent, title, nav_target, row, col):
        btn = ctk.CTkButton(
            parent, text=title, height=80, width=180,
            font=ctk.CTkFont(size=16),
            command=lambda t=nav_target: self.nav_controller.navigate(t)
        )
        btn.grid(row=row, column=col, padx=10, pady=10)
