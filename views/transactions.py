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

class ReturnBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Transactions", None), ("Return Book", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(self, text="Return Book", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(0, 20))
        form_frame = ctk.CTkFrame(self, width=400)
        form_frame.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(form_frame, text="Transaction ID:").pack(side="left", padx=20)
        self.txn_entry = ctk.CTkEntry(form_frame, width=150)
        self.txn_entry.pack(side="left", padx=10)
        ctk.CTkButton(form_frame, text="Return", command=self.return_book).pack(side="left", padx=20)
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.load_active_transactions()

    def return_book(self):
        try:
            txn_id = int(self.txn_entry.get())
            TransactionController.return_book(txn_id)
            messagebox.showinfo("Success", "Book returned successfully!")
            self.txn_entry.delete(0, 'end')
            self.load_active_transactions()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", str(e))

    def load_active_transactions(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        txns = TransactionController.get_active_transactions()
        headers = ["Txn ID", "Book Title", "Member Name", "Issue Date", "Due Date", "Action"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=10, pady=5, sticky="w")
        if not txns:
            ctk.CTkLabel(self.table_frame, text="No active issues found.").grid(row=1, column=0, columnspan=6, pady=20)
            return
        for row, txn in enumerate(txns, start=1):
            ctk.CTkLabel(self.table_frame, text=str(txn['transaction_id'])).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=txn['title']).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=txn['full_name']).grid(row=row, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(txn['issue_date'])[:10]).grid(row=row, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(txn['due_date'])[:10]).grid(row=row, column=4, padx=10, pady=5, sticky="w")
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=5, padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="Return", width=60, command=lambda t=txn['transaction_id']: self.auto_return(t)).pack(side="left")

    def auto_return(self, txn_id):
        self.txn_entry.delete(0, 'end')
        self.txn_entry.insert(0, str(txn_id))
        self.return_book()
