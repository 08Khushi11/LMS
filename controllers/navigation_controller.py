import customtkinter as ctk

class NavigationController:
    """Centralized navigation controller to handle page transitions and shortcuts."""
    
    def __init__(self, root_window):
        self.root = root_window
        self.current_frame = None
        self.current_view_name = None
        self.views = {}  # Maps view name to the view class
        self._bind_shortcuts()

    def register_views(self, views_dict):
        """Register views to the controller."""
        self.views.update(views_dict)

    def navigate(self, view_name, **kwargs):
        """Navigate to a specific view safely, preventing any blank page on error."""
        if view_name not in self.views:
            print(f"Error: View '{view_name}' not found.")
            return

        view_class = self.views[view_name]
        try:
            # Instantiate new frame before destroying the previous one
            new_frame = view_class(self.root.main_content_frame, self, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            # If view initialization fails, display a recovery screen instead of leaving a blank page
            if self.current_frame is not None:
                self.current_frame.destroy()
            self.current_frame = ctk.CTkFrame(self.root.main_content_frame, fg_color="transparent")
            self.current_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(
                self.current_frame,
                text=f"⚠️ Unable to load '{view_name}' view",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#c23b22"
            ).pack(pady=(60, 10))
            ctk.CTkLabel(
                self.current_frame,
                text=str(e),
                font=ctk.CTkFont(size=13),
                text_color="gray70"
            ).pack(pady=(0, 20))
            ctk.CTkButton(
                self.current_frame,
                text="🏠 Return to Dashboard",
                command=self.navigate_home,
                height=38
            ).pack()
            return

        # Destroy the old frame now that new_frame succeeded
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = new_frame
        self.current_view_name = view_name
        self.current_frame.pack(fill="both", expand=True)
        
        # Update sidebar highlighting if sidebar exists
        if hasattr(self.root, 'update_sidebar_active'):
            self.root.update_sidebar_active(view_name)

    def navigate_home(self):
        """Shortcut to navigate to the dashboard."""
        self.navigate("Dashboard")

    def _bind_shortcuts(self):
        """Bind global keyboard shortcuts."""
        self.root.bind('<Control-d>', lambda e: self.navigate_home())
        self.root.bind('<Control-D>', lambda e: self.navigate_home())
        self.root.bind('<Control-b>', lambda e: self.navigate('Books'))
        self.root.bind('<Control-B>', lambda e: self.navigate('Books'))
        self.root.bind('<Control-m>', lambda e: self.navigate('Members'))
        self.root.bind('<Control-M>', lambda e: self.navigate('Members'))
        self.root.bind('<Control-i>', lambda e: self.navigate('IssueBook'))
        self.root.bind('<Control-I>', lambda e: self.navigate('IssueBook'))
        self.root.bind('<Control-r>', lambda e: self.navigate('ReturnBook'))
        self.root.bind('<Control-R>', lambda e: self.navigate('ReturnBook'))
        self.root.bind('<Control-p>', lambda e: self.navigate('Reports'))
        self.root.bind('<Control-P>', lambda e: self.navigate('Reports'))

        def _handle_search(e=None):
            if hasattr(self.current_frame, 'focus_search'):
                self.current_frame.focus_search()
                return "break"
            else:
                self.navigate('Books')
                if hasattr(self.current_frame, 'focus_search'):
                    self.current_frame.focus_search()
                return "break"

        def _handle_add(e=None):
            if hasattr(self.current_frame, 'open_add_dialog'):
                self.current_frame.open_add_dialog()
                return "break"
            else:
                self.navigate('Books', open_add=True)
                return "break"

        def _handle_escape(e=None):
            if self.current_view_name and self.current_view_name != "Dashboard":
                self.navigate_home()
                return "break"

        self.root.bind('<Control-f>', _handle_search)
        self.root.bind('<Control-F>', _handle_search)
        self.root.bind('<Control-n>', _handle_add)
        self.root.bind('<Control-N>', _handle_add)
        self.root.bind('<Escape>', _handle_escape)
