import customtkinter as ctk

class NavigationController:
    """Centralized navigation controller to handle page transitions and shortcuts."""
    
    def __init__(self, root_window):
        self.root = root_window
        self.current_frame = None
        self.views = {}  # Maps view name to the view class
        self._bind_shortcuts()

    def register_views(self, views_dict):
        """Register views to the controller."""
        self.views.update(views_dict)

    def navigate(self, view_name, **kwargs):
        """Navigate to a specific view."""
        if view_name not in self.views:
            print(f"Error: View '{view_name}' not found.")
            return

        if self.current_frame is not None:
            self.current_frame.destroy()

        view_class = self.views[view_name]
        self.current_frame = view_class(self.root.main_content_frame, self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)
        
        # Update sidebar highlighting if sidebar exists
        if hasattr(self.root, 'update_sidebar_active'):
            self.root.update_sidebar_active(view_name)

    def navigate_home(self):
        """Shortcut to navigate to the dashboard."""
        self.navigate("Dashboard")

    def _bind_shortcuts(self):
        """Bind global keyboard shortcuts."""
        # Make sure shortcuts work globally
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
