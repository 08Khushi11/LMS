import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.member_controller import MemberController
import tkinter.messagebox as messagebox

class MembersView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Members", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Members Management", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(header_frame, placeholder_text="Search Members... (Ctrl+F)", width=250)
        self.search_entry.pack(side="left", padx=(20, 10))
        self.search_entry.bind("<Return>", lambda e: self.load_members())
        
        ctk.CTkButton(header_frame, text="Search", width=80, command=self.load_members).pack(side="left")
        ctk.CTkButton(header_frame, text="Reset", width=70, fg_color="gray50", hover_color="gray40", command=self.reset_search).pack(side="left", padx=(5, 0))
        
        ctk.CTkButton(header_frame, text="+ Register Member (Ctrl+N)", command=self.show_add_member_dialog).pack(side="right")
        
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._setup_shortcuts()
        self.load_members()

    def _setup_shortcuts(self):
        def _focus_search(e=None):
            if self.winfo_exists() and hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
                self.search_entry.focus_set()
                return "break"

        def _open_add(e=None):
            if self.winfo_exists():
                self.show_add_member_dialog()
                return "break"

        self.bind_all("<Control-f>", _focus_search)
        self.bind_all("<Control-F>", _focus_search)
        self.bind_all("<Control-n>", _open_add)
        self.bind_all("<Control-N>", _open_add)

        def _on_destroy(event):
            if event.widget == self:
                try:
                    self.unbind_all("<Control-f>")
                    self.unbind_all("<Control-F>")
                    self.unbind_all("<Control-n>")
                    self.unbind_all("<Control-N>")
                except Exception:
                    pass

        self.bind("<Destroy>", _on_destroy)

    def reset_search(self):
        self.search_entry.delete(0, 'end')
        self.load_members()

    def load_members(self):
        if not self.winfo_exists() or not self.table_frame.winfo_exists():
            return

        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip()
        if search_query:
            members = MemberController.search_members(search_query)
        else:
            members = MemberController.get_all_members()
            
        headers = ["ID", "Full Name", "Email", "Phone", "Registration Date", "Actions"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=10, pady=5, sticky="w")
            
        if not members:
            ctk.CTkLabel(self.table_frame, text="No members found.", font=ctk.CTkFont(slant="italic")).grid(row=1, column=0, columnspan=6, pady=20)
            return

        for row, member in enumerate(members, start=1):
            ctk.CTkLabel(self.table_frame, text=str(member['member_id'])).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=member['full_name']).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=member['email'] or "-").grid(row=row, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=member['phone'] or "-").grid(row=row, column=3, padx=10, pady=5, sticky="w")
            reg_date = str(member['registration_date'])[:10] if member['registration_date'] else "-"
            ctk.CTkLabel(self.table_frame, text=reg_date).grid(row=row, column=4, padx=10, pady=5, sticky="w")
            
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=5, padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="Edit", width=55, fg_color="#1f538d", hover_color="#14375e", 
                          command=lambda m=member: self.show_edit_member_dialog(m)).pack(side="left", padx=(0, 5))
            ctk.CTkButton(btn_frame, text="Delete", width=55, fg_color="#c23b22", hover_color="#8b2512", 
                          command=lambda m=member: self.delete_member(m['member_id'])).pack(side="left")

    def show_add_member_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Register Member")
        dialog.geometry("420x480")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        entries = {}
        fields = [("Full Name *", "full_name"), ("Email", "email"), ("Phone", "phone"), ("Address", "address")]
        
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).pack(pady=(10, 0))
            entry = ctk.CTkEntry(dialog, width=320)
            entry.pack(pady=5)
            entries[key] = entry
            if i == 0:
                entry.focus_set()
                
        def save():
            try:
                MemberController.add_member(
                    entries["full_name"].get(),
                    entries["email"].get(),
                    entries["phone"].get(),
                    entries["address"].get()
                )
                dialog.destroy()
                self.load_members()
            except Exception as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
                
        ctk.CTkButton(dialog, text="Register", command=save, fg_color="#2fa572").pack(pady=20)

    def show_edit_member_dialog(self, member):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Member #{member['member_id']}")
        dialog.geometry("420x480")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        entries = {}
        fields = [
            ("Full Name *", "full_name", member.get('full_name', '')),
            ("Email", "email", member.get('email', '') or ''),
            ("Phone", "phone", member.get('phone', '') or ''),
            ("Address", "address", member.get('address', '') or '')
        ]

        for i, (label, key, val) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).pack(pady=(10, 0))
            entry = ctk.CTkEntry(dialog, width=320)
            entry.insert(0, val)
            entry.pack(pady=5)
            entries[key] = entry
            if i == 0:
                entry.focus_set()

        def save_changes():
            try:
                MemberController.update_member(
                    member['member_id'],
                    entries["full_name"].get(),
                    entries["email"].get(),
                    entries["phone"].get(),
                    entries["address"].get()
                )
                dialog.destroy()
                self.load_members()
            except Exception as e:
                messagebox.showerror("Update Error", str(e), parent=dialog)

        ctk.CTkButton(dialog, text="Update Member", command=save_changes, fg_color="#1f538d").pack(pady=20)

    def delete_member(self, member_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this member?"):
            try:
                MemberController.delete_member(member_id)
                self.load_members()
            except Exception as e:
                messagebox.showerror("Error", str(e))

