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
        ctk.CTkButton(header_frame, text="Search", width=80, command=self.load_members).pack(side="left")
        ctk.CTkButton(header_frame, text="+ Register Member (Ctrl+N)", command=self.show_add_member_dialog).pack(side="right")
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.load_members()

    def load_members(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        search_query = self.search_entry.get().strip()
        members = MemberController.search_members(search_query) if search_query else MemberController.get_all_members()
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
            ctk.CTkButton(btn_frame, text="Delete", width=60, fg_color="red", hover_color="darkred", command=lambda m=member: self.delete_member(m['member_id'])).pack(side="left")

    def show_add_member_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Register Member")
        dialog.geometry("400x450")
        entries = {}
        fields = [("Full Name *", "full_name"), ("Email", "email"), ("Phone", "phone"), ("Address", "address")]
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).pack(pady=(10, 0))
            entry = ctk.CTkEntry(dialog, width=300)
            entry.pack(pady=5)
            entries[key] = entry
        def save():
            try:
                MemberController.add_member(entries["full_name"].get(), entries["email"].get(), entries["phone"].get(), entries["address"].get())
                dialog.destroy()
                self.load_members()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ctk.CTkButton(dialog, text="Register", command=save).pack(pady=20)

    def delete_member(self, member_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this member?"):
            try:
                MemberController.delete_member(member_id)
                self.load_members()
            except Exception as e:
                messagebox.showerror("Error", str(e))
