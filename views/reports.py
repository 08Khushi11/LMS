import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend to prevent memory leaks


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        self.figure_canvas = None  # Track matplotlib canvas widget for cleanup

        BreadcrumbHeader(
            self, nav_controller, [("🏠 Home", "Dashboard"), ("Reports", None)]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            self, text="Reports & Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=20, pady=(0, 5))

        ctk.CTkLabel(
            self, text="Real-time quality overview of library operations (TQM Quality Evaluation)",
            font=ctk.CTkFont(size=12), text_color="gray60"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Refresh button
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(anchor="e", padx=20, pady=(0, 10))
        ctk.CTkButton(
            btn_frame, text="🔄 Refresh Chart", command=self.refresh_chart,
            width=140, fg_color="gray40", hover_color="gray30"
        ).pack()

        # Chart container
        self.chart_frame = ctk.CTkFrame(self, corner_radius=12)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.generate_chart()

        # Cleanup on destroy to prevent memory leaks
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, event):
        if event.widget == self:
            self._clear_canvas()

    def _clear_canvas(self):
        """Properly remove matplotlib canvas widget."""
        if self.figure_canvas is not None:
            try:
                self.figure_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.figure_canvas = None

    def refresh_chart(self):
        """Refresh the chart with latest data."""
        self._clear_canvas()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.generate_chart()

    def generate_chart(self):
        try:
            stats = TransactionController.get_dashboard_stats()
        except Exception:
            stats = {'total_books': 0, 'total_members': 0, 'currently_issued': 0, 'overdue_books': 0}

        labels = ['Total\nBooks', 'Registered\nMembers', 'Currently\nIssued', 'Overdue\nBooks']
        values = [
            stats['total_books'],
            stats['total_members'],
            stats['currently_issued'],
            stats['overdue_books']
        ]
        colors = ['#1f538d', '#2fa572', '#d68a27', '#c23b22']

        fig = Figure(figsize=(8, 4.5), dpi=100)
        ax = fig.add_subplot(111)

        # Dark theme
        bg_color = '#1e1e2e'
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor('#2b2b3b')

        if all(v == 0 for v in values):
            ax.text(
                0.5, 0.5, 'No data yet.\nAdd books and members to see stats.',
                transform=ax.transAxes, ha='center', va='center',
                color='gray', fontsize=14
            )
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            bars = ax.bar(labels, values, color=colors, width=0.5, zorder=3)
            ax.set_ylim(0, max(values) * 1.3 if max(values) > 0 else 5)

            # Value labels on top of bars
            for bar, val in zip(bars, values):
                height = bar.get_height()
                if height >= 0:
                    ax.annotate(
                        f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        color='white', fontsize=12, fontweight='bold'
                    )

            ax.grid(axis='y', color='#444455', linestyle='--', linewidth=0.7, zorder=0)
            ax.tick_params(colors='#cccccc', labelsize=10)

        for spine in ax.spines.values():
            spine.set_edgecolor('#444455')

        ax.set_title('Library System Overview', color='white', fontsize=15, pad=15, fontweight='bold')
        fig.tight_layout(pad=1.5)

        self.figure_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
