import customtkinter as ctk
from database.db_connection import initialize_database

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1024x768")
        self.minsize(800, 600)

if __name__ == "__main__":
    initialize_database()
    app = MainApplication()
    app.mainloop()
