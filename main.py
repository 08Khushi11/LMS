import customtkinter as ctk
from database.db_connection import initialize_database
from controllers.navigation_controller import NavigationController

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1024x768")
        self.minsize(800, 600)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Library System", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")

        self.nav_controller = NavigationController(self)
        self.nav_buttons = {}

    def update_sidebar_active(self, view_name):
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

if __name__ == "__main__":
    initialize_database()
    app = MainApplication()
    app.mainloop()
