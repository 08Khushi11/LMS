import customtkinter as ctk

class BreadcrumbHeader(ctk.CTkFrame):
    def __init__(self, master, nav_controller, paths, **kwargs):
        """
        paths is a list of tuples: [("🏠 Home", "Dashboard"), ("Books", "Books"), ("Add Book", None)]
        If the view_name is None, it means it's the current page (unclickable highlighted text).
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        
        col = 0
        for i, (label_text, view_name) in enumerate(paths):
            if view_name:
                btn = ctk.CTkButton(
                    self, text=label_text, 
                    command=lambda v=view_name: self.nav_controller.navigate(v),
                    fg_color="transparent", 
                    text_color=("#1f538d", "#4da6ff"), 
                    hover_color=("gray80", "gray30"),
                    font=ctk.CTkFont(size=12, underline=True),
                    width=10, height=24
                )
                btn.grid(row=0, column=col, padx=0, pady=2)
            else:
                lbl = ctk.CTkLabel(
                    self, text=label_text, 
                    text_color=("gray15", "gray95"), 
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                lbl.grid(row=0, column=col, padx=4, pady=2)
            
            col += 1
            if i < len(paths) - 1:
                sep = ctk.CTkLabel(self, text="›", font=ctk.CTkFont(size=14), text_color="gray50")
                sep.grid(row=0, column=col, padx=3, pady=2)
                col += 1
