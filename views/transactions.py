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
        form_frame = ctk.CTkFrame(self, width=420)
        form_frame.pack(padx=20, pady=10, fill="y")
        ctk.CTkLabel(form_frame, text="Book ID *:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.book_entry = ctk.CTkEntry(form_frame, width=280, placeholder_text="Enter Book ID")
        self.book_entry.pack(pady=5)
        ctk.CTkLabel(form_frame, text="Member ID *:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        self.member_entry = ctk.CTkEntry(form_frame, width=280, placeholder_text="Enter Member ID")
        self.member_entry.pack(pady=5)
        ctk.CTkLabel(form_frame, text="Loan Duration (Days):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        self.days_entry = ctk.CTkEntry(form_frame, width=280)
        self.days_entry.insert(0, "14")
        self.days_entry.pack(pady=5)
        ctk.CTkButton(form_frame, text="Issue Book", command=self.issue_book, fg_color="#2fa572", hover_color="#238158", height=38).pack(pady=25)

    def issue_book(self):
        book_id_text = self.book_entry.get().strip()
        member_id_text = self.member_entry.get().strip()
        days_text = self.days_entry.get().strip()
        if not book_id_text or not member_id_text:
            messagebox.showerror("Validation Error", "Please provide both Book ID and Member ID.")
            return
        try:
            book_id = int(book_id_text)
            member_id = int(member_id_text)
            days = int(days_text) if days_text else 14
        except ValueError:
            messagebox.showerror("Validation Error", "Book ID, Member ID, and Loan Duration must be valid integers.")
            return
        try:
            TransactionController.issue_book(book_id, member_id, days_to_due=days)
            messagebox.showinfo("Success", f"Book #{book_id} issued successfully to Member #{member_id}!")
            self.book_entry.delete(0, 'end')
            self.member_entry.delete(0, 'end')
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", str(e))

class ReturnBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Transactions", None), ("Return Book", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(self, text="Return Book", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(0, 20))
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(form_frame, text="Transaction ID:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)
        self.txn_entry = ctk.CTkEntry(form_frame, width=160, placeholder_text="e.g. 1")
        self.txn_entry.pack(side="left", padx=10, pady=10)
        self.txn_entry.bind("<Return>", lambda e: self.return_book())
        ctk.CTkButton(form_frame, text="Return Book", command=self.return_book, fg_color="#1f538d").pack(side="left", padx=15, pady=10)
        ctk.CTkButton(form_frame, text="Refresh", command=self.load_active_transactions, fg_color="gray50").pack(side="right", padx=15, pady=10)
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_active_transactions()

    def return_book(self):
        txn_id_text = self.txn_entry.get().strip()
        if not txn_id_text:
            messagebox.showerror("Validation Error", "Please enter a Transaction ID.")
            return
        try:
            txn_id = int(txn_id_text)
        except ValueError:
            messagebox.showerror("Validation Error", "Transaction ID must be a valid integer.")
            return
        try:
            TransactionController.return_book(txn_id)
            messagebox.showinfo("Success", f"Transaction #{txn_id} marked as returned successfully!")
            self.txn_entry.delete(0, 'end')
            self.load_active_transactions()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", str(e))

    def load_active_transactions(self):
        if not self.winfo_exists() or not self.table_frame.winfo_exists():
            return
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        txns = TransactionController.get_active_transactions()
        headers = ["Txn ID", "Book Title", "Member Name", "Issue Date", "Due Date", "Status", "Action"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=10, pady=5, sticky="w")
        if not txns:
            ctk.CTkLabel(self.table_frame, text="No active issues or overdue books found.", font=ctk.CTkFont(slant="italic")).grid(row=1, column=0, columnspan=7, pady=20)
            return
        for row, txn in enumerate(txns, start=1):
            is_overdue = txn.get('status') == 'Overdue'
            status_color = "#c23b22" if is_overdue else "#2fa572"
            ctk.CTkLabel(self.table_frame, text=str(txn['transaction_id'])).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=txn['title']).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=txn['full_name']).grid(row=row, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(txn['issue_date'])[:10]).grid(row=row, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(txn['due_date'])[:10]).grid(row=row, column=4, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=txn['status'], text_color=status_color, font=ctk.CTkFont(weight="bold")).grid(row=row, column=5, padx=10, pady=5, sticky="w")
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=6, padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="Return", width=65, fg_color="#1f538d", hover_color="#14375e", command=lambda t=txn['transaction_id']: self.auto_return(t)).pack(side="left")

    def auto_return(self, txn_id):
        self.txn_entry.delete(0, 'end')
        self.txn_entry.insert(0, str(txn_id))
        self.return_book()
