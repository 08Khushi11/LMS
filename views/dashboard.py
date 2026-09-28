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

    def create_stat_tile(self, parent, title, value, row, col, nav_target):
        frame = ctk.CTkFrame(parent, corner_radius=10, width=200, height=100)
        frame.grid(row=row, column=col, padx=10, pady=10)
        frame.grid_propagate(False)
        lbl_val = ctk.CTkLabel(frame, text=str(value), font=ctk.CTkFont(size=32, weight="bold"))
        lbl_val.place(relx=0.5, rely=0.4, anchor="center")
        lbl_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14))
        lbl_title.place(relx=0.5, rely=0.75, anchor="center")
