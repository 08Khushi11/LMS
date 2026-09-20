import customtkinter as ctk

class BreadcrumbHeader(ctk.CTkFrame):
    def __init__(self, master, nav_controller, paths, **kwargs):
        """
        paths is a list of tuples: [("Home", "Dashboard"), ("Books", "Books"), ("Add Book", None)]
        If the view_name is None, it means it's the current page (unclickable text).
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        
        col = 0
        for i, (label_text, view_name) in enumerate(paths):
            if view_name:
                btn = ctk.CTkButton(
                    self, text=label_text, 
                    command=lambda v=view_name: self.nav_controller.navigate(v),
                    fg_color="transparent", text_color="#1f538d", hover_color=("gray70", "gray30"),
                    width=10
                )
                btn.grid(row=0, column=col, padx=0, pady=5)
            else:
                lbl = ctk.CTkLabel(self, text=label_text, text_color=("gray20", "gray80"), font=ctk.CTkFont(weight="bold"))
                lbl.grid(row=0, column=col, padx=5, pady=5)
            
            col += 1
            if i < len(paths) - 1:
                sep = ctk.CTkLabel(self, text=">", text_color="gray50")
                sep.grid(row=0, column=col, padx=2, pady=5)
                col += 1
