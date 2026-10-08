import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportsView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Reports", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self, text="Library Reports & Analytics", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(0, 20))
        
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.generate_chart()

    def generate_chart(self):
        stats = TransactionController.get_dashboard_stats()
        
        labels = ['Total Books', 'Registered Members', 'Currently Issued', 'Overdue']
        values = [stats['total_books'], stats['total_members'], stats['currently_issued'], stats['overdue_books']]
        
        # Use Figure directly to avoid pyplot memory leaks
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        
        bars = ax.bar(labels, values, color=['#2fa572', '#1f538d', '#d68a27', '#c23b22'])
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
        
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
            
        ax.set_title('Library System Overview', color='white', fontsize=14, pad=15)
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

