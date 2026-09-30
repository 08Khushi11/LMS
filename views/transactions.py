import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController
import tkinter.messagebox as messagebox

class IssueBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Transactions", None), ("Issue Book", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(self, text="Issue Book", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(0, 20))
        form_frame = ctk.CTkFrame(self, width=400)
        form_frame.pack(padx=20, pady=10, fill="y")
        ctk.CTkLabel(form_frame, text="Book ID:").pack(pady=(20, 5))
        self.book_entry = ctk.CTkEntry(form_frame, width=250)
        self.book_entry.pack(pady=5)
        ctk.CTkLabel(form_frame, text="Member ID:").pack(pady=(10, 5))
        self.member_entry = ctk.CTkEntry(form_frame, width=250)
        self.member_entry.pack(pady=5)
        ctk.CTkButton(form_frame, text="Issue Book", command=self.issue_book).pack(pady=30)

    def issue_book(self):
        try:
            book_id = int(self.book_entry.get())
            member_id = int(self.member_entry.get())
            TransactionController.issue_book(book_id, member_id)
            messagebox.showinfo("Success", "Book issued successfully!")
            self.book_entry.delete(0, 'end')
            self.member_entry.delete(0, 'end')
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", str(e))
