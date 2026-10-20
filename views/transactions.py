import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController
from controllers.book_controller import BookController
from controllers.member_controller import MemberController
import tkinter.messagebox as messagebox


class IssueBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller

        BreadcrumbHeader(
            self, nav_controller,
            [("🏠 Home", "Dashboard"), ("Issue Book", None)]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(self, text="Issue Book", font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=20, pady=(0, 10)
        )

        # ── Main layout: form on left, lookup tables on right ──
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # ── LEFT: Issue form ──
        form_frame = ctk.CTkFrame(main_frame, width=300)
        form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 15), pady=0)
        form_frame.grid_propagate(False)

        ctk.CTkLabel(form_frame, text="Book ID *:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 4))
        self.book_entry = ctk.CTkEntry(form_frame, width=240, placeholder_text="Enter Book ID")
        self.book_entry.pack(pady=4)

        ctk.CTkLabel(form_frame, text="Member ID *:", font=ctk.CTkFont(weight="bold")).pack(pady=(12, 4))
        self.member_entry = ctk.CTkEntry(form_frame, width=240, placeholder_text="Enter Member ID")
        self.member_entry.pack(pady=4)

        ctk.CTkLabel(form_frame, text="Loan Duration (Days):", font=ctk.CTkFont(weight="bold")).pack(pady=(12, 4))
        self.days_entry = ctk.CTkEntry(form_frame, width=240)
        self.days_entry.insert(0, "14")
        self.days_entry.pack(pady=4)

        ctk.CTkButton(
            form_frame, text="✅  Issue Book", command=self.issue_book,
            fg_color="#2fa572", hover_color="#238158", height=42, width=240,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=25)

        ctk.CTkLabel(
            form_frame,
            text="💡 Click a row in the tables\nto auto-fill the IDs.",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            justify="center"
        ).pack(pady=(0, 10))

        # ── RIGHT: Available books & members tables ──
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Books with available copies
        ctk.CTkLabel(right_frame, text="📖 Available Books", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="nw", padx=5, pady=(0, 3)
        )
        self.books_frame = ctk.CTkScrollableFrame(right_frame, height=200)
        self.books_frame.grid(row=0, column=0, sticky="new", padx=5, pady=(20, 5))

        # Members list
        ctk.CTkLabel(right_frame, text="👥 Registered Members", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=(10, 3)
        )
        self.members_frame = ctk.CTkScrollableFrame(right_frame, height=180)
        self.members_frame.grid(row=1, column=0, sticky="new", padx=5, pady=(20, 5))

        self.load_lookup_tables()

    def load_lookup_tables(self):
        """Populate the book and member lookup tables."""
        # Clear
        for w in self.books_frame.winfo_children():
            w.destroy()
        for w in self.members_frame.winfo_children():
            w.destroy()

        # Books headers
        book_headers = ["ID", "ISBN", "Title", "Author", "Available"]
        for col, h in enumerate(book_headers):
            ctk.CTkLabel(self.books_frame, text=h, font=ctk.CTkFont(weight="bold", size=11)).grid(
                row=0, column=col, padx=8, pady=3, sticky="w"
            )

        books = [b for b in BookController.get_all_books() if b['available_copies'] > 0]
        if not books:
            ctk.CTkLabel(self.books_frame, text="No books with available copies.",
                         font=ctk.CTkFont(slant="italic"), text_color="gray60").grid(
                row=1, column=0, columnspan=5, pady=10
            )
        for row, b in enumerate(books, start=1):
            row_data = [
                str(b['book_id']), b['isbn'], b['title'][:30], b['author'][:20],
                str(b['available_copies'])
            ]
            for col, val in enumerate(row_data):
                lbl = ctk.CTkLabel(self.books_frame, text=val, font=ctk.CTkFont(size=11))
                lbl.grid(row=row, column=col, padx=8, pady=2, sticky="w")
                lbl.bind("<Button-1>", lambda e, bid=b['book_id']: self._fill_book_id(bid))
                lbl.configure(cursor="hand2")

        # Members headers
        mem_headers = ["ID", "Name", "Email", "Phone"]
        for col, h in enumerate(mem_headers):
            ctk.CTkLabel(self.members_frame, text=h, font=ctk.CTkFont(weight="bold", size=11)).grid(
                row=0, column=col, padx=8, pady=3, sticky="w"
            )

        members = MemberController.get_all_members()
        if not members:
            ctk.CTkLabel(self.members_frame, text="No registered members.",
                         font=ctk.CTkFont(slant="italic"), text_color="gray60").grid(
                row=1, column=0, columnspan=4, pady=10
            )
        for row, m in enumerate(members, start=1):
            row_data = [
                str(m['member_id']), m['full_name'][:25],
                (m['email'] or '-')[:25], (m['phone'] or '-')
            ]
            for col, val in enumerate(row_data):
                lbl = ctk.CTkLabel(self.members_frame, text=val, font=ctk.CTkFont(size=11))
                lbl.grid(row=row, column=col, padx=8, pady=2, sticky="w")
                lbl.bind("<Button-1>", lambda e, mid=m['member_id']: self._fill_member_id(mid))
                lbl.configure(cursor="hand2")

    def _fill_book_id(self, book_id):
        self.book_entry.delete(0, 'end')
        self.book_entry.insert(0, str(book_id))

    def _fill_member_id(self, member_id):
        self.member_entry.delete(0, 'end')
        self.member_entry.insert(0, str(member_id))

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
            self.load_lookup_tables()  # Refresh available books
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", str(e))


class ReturnBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller

        BreadcrumbHeader(
            self, nav_controller,
            [("🏠 Home", "Dashboard"), ("Return Book", None)]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(self, text="Return Book", font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=20, pady=(0, 15)
        )

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(padx=20, pady=(0, 10), fill="x")

        ctk.CTkLabel(form_frame, text="Transaction ID:", font=ctk.CTkFont(weight="bold")).pack(
            side="left", padx=15, pady=10
        )
        self.txn_entry = ctk.CTkEntry(form_frame, width=160, placeholder_text="e.g. 1")
        self.txn_entry.pack(side="left", padx=10, pady=10)
        self.txn_entry.bind("<Return>", lambda e: self.return_book())

        ctk.CTkButton(
            form_frame, text="↩️  Return Book", command=self.return_book,
            fg_color="#1f538d", hover_color="#14375e",
            font=ctk.CTkFont(size=13, weight="bold"), height=36
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            form_frame, text="🔄 Refresh", command=self.load_active_transactions,
            fg_color="gray50", hover_color="gray40", height=36
        ).pack(side="right", padx=15, pady=10)

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
            ctk.CTkLabel(
                self.table_frame,
                text="✅ No active issues or overdue books found.",
                font=ctk.CTkFont(slant="italic"), text_color="gray60"
            ).grid(row=1, column=0, columnspan=7, pady=20)
            return

        for row, txn in enumerate(txns, start=1):
            is_overdue = txn.get('status') == 'Overdue'
            status_color = "#c23b22" if is_overdue else "#2fa572"

            ctk.CTkLabel(self.table_frame, text=str(txn['transaction_id'])).grid(
                row=row, column=0, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(self.table_frame, text=txn['title'][:30]).grid(
                row=row, column=1, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(self.table_frame, text=txn['full_name'][:20]).grid(
                row=row, column=2, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(self.table_frame, text=str(txn['issue_date'])[:10]).grid(
                row=row, column=3, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(self.table_frame, text=str(txn['due_date'])[:10]).grid(
                row=row, column=4, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(
                self.table_frame, text=txn['status'],
                text_color=status_color, font=ctk.CTkFont(weight="bold")
            ).grid(row=row, column=5, padx=10, pady=4, sticky="w")

            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=6, padx=10, pady=4)
            ctk.CTkButton(
                btn_frame, text="Return", width=70,
                fg_color="#1f538d", hover_color="#14375e",
                command=lambda t=txn['transaction_id']: self.auto_return(t)
            ).pack(side="left")

    def auto_return(self, txn_id):
        self.txn_entry.delete(0, 'end')
        self.txn_entry.insert(0, str(txn_id))
        self.return_book()
