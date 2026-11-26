import customtkinter as ctk
from datetime import datetime, timedelta
from views.components import BreadcrumbHeader
from controllers.transaction_controller import TransactionController
from controllers.book_controller import BookController
from controllers.member_controller import MemberController
import tkinter.messagebox as messagebox


class IssueBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller

        # State tracking
        self.selected_member = None
        self.selected_book = None
        self._member_suggestion_widgets = []
        self._book_suggestion_widgets = []

        # ── Breadcrumb ──
        BreadcrumbHeader(
            self, nav_controller,
            [("🏠 Home", "Dashboard"), ("Issue Book", None)]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        # ── Header Title & Subtitle ──
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            header_frame, text="Book Issue Management",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="Search by Name/Title or ID  •  Real-Time Availability  •  Poka-Yoke Error Prevention",
            font=ctk.CTkFont(size=12), text_color="gray60"
        ).pack(side="right", padx=(0, 10))

        # ── Main 2-Column Split Layout ──
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        main_layout.grid_columnconfigure(0, weight=4, minsize=420)  # Left: Smart Issue Console
        main_layout.grid_columnconfigure(1, weight=5, minsize=520)  # Right: Explorer Tabs
        main_layout.grid_rowconfigure(0, weight=1)

        # ══════════════════════════════════════════════════════════════
        # LEFT COLUMN: Smart Issue Console (Scrollable)
        # ══════════════════════════════════════════════════════════════
        self.left_scroll = ctk.CTkScrollableFrame(main_layout, fg_color=("gray95", "gray17"), corner_radius=10)
        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        self.left_scroll.grid_columnconfigure(0, weight=1)

        # ── Section 1: Member Selection ──
        ctk.CTkLabel(
            self.left_scroll, text="1. Select Library Member",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1f538d", "#4da6ff")
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            self.left_scroll, text="Type member name, email, phone, or ID to search:",
            font=ctk.CTkFont(size=11), text_color="gray60"
        ).pack(anchor="w", padx=15, pady=(0, 4))

        # Member search entry & clear
        m_search_row = ctk.CTkFrame(self.left_scroll, fg_color="transparent")
        m_search_row.pack(fill="x", padx=15, pady=(0, 2))

        self.member_search_var = ctk.StringVar()
        self.member_search_entry = ctk.CTkEntry(
            m_search_row, textvariable=self.member_search_var,
            placeholder_text="🔍 Type Member Name (e.g. Kamlesh)...",
            height=34
        )
        self.member_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.member_search_entry.bind("<KeyRelease>", self._on_member_search_type)

        ctk.CTkButton(
            m_search_row, text="Clear", width=55, height=34,
            fg_color="gray45", hover_color="gray35",
            command=self.clear_selected_member
        ).pack(side="left")

        # Container for live member autocomplete suggestions
        self.member_suggestions_box = ctk.CTkFrame(self.left_scroll, fg_color=("gray85", "gray22"), corner_radius=6)

        # Selected Member Information Card
        self.member_card = ctk.CTkFrame(self.left_scroll, fg_color=("gray88", "gray20"), corner_radius=8)
        self.member_card.pack(fill="x", padx=15, pady=(6, 12))
        self._build_empty_member_card()

        # ── Section 2: Book Selection & Availability ──
        ctk.CTkLabel(
            self.left_scroll, text="2. Select Book & Inspect Availability",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1f538d", "#4da6ff")
        ).pack(anchor="w", padx=15, pady=(6, 4))

        ctk.CTkLabel(
            self.left_scroll, text="Type book title, author, ISBN, or Book ID to search:",
            font=ctk.CTkFont(size=11), text_color="gray60"
        ).pack(anchor="w", padx=15, pady=(0, 4))

        # Book search entry & clear
        b_search_row = ctk.CTkFrame(self.left_scroll, fg_color="transparent")
        b_search_row.pack(fill="x", padx=15, pady=(0, 2))

        self.book_search_var = ctk.StringVar()
        self.book_search_entry = ctk.CTkEntry(
            b_search_row, textvariable=self.book_search_var,
            placeholder_text="🔍 Type Book Name (e.g. Clean Code)...",
            height=34
        )
        self.book_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.book_search_entry.bind("<KeyRelease>", self._on_book_search_type)

        ctk.CTkButton(
            b_search_row, text="Clear", width=55, height=34,
            fg_color="gray45", hover_color="gray35",
            command=self.clear_selected_book
        ).pack(side="left")

        # Container for live book autocomplete suggestions
        self.book_suggestions_box = ctk.CTkFrame(self.left_scroll, fg_color=("gray85", "gray22"), corner_radius=6)

        # Selected Book & Availability Card
        self.book_card = ctk.CTkFrame(self.left_scroll, fg_color=("gray88", "gray20"), corner_radius=8)
        self.book_card.pack(fill="x", padx=15, pady=(6, 12))
        self._build_empty_book_card()

        # ── Section 3: Issue Settings & Due Date ──
        ctk.CTkLabel(
            self.left_scroll, text="3. Loan Duration & Dates",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1f538d", "#4da6ff")
        ).pack(anchor="w", padx=15, pady=(6, 4))

        loan_box = ctk.CTkFrame(self.left_scroll, fg_color=("gray88", "gray20"), corner_radius=8)
        loan_box.pack(fill="x", padx=15, pady=(4, 15))

        # Quick duration presets
        btn_row = ctk.CTkFrame(loan_box, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(btn_row, text="Loan Days:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))

        self.days_entry = ctk.CTkEntry(btn_row, width=65, height=30)
        self.days_entry.insert(0, "14")
        self.days_entry.pack(side="left", padx=(0, 10))
        self.days_entry.bind("<KeyRelease>", lambda e: self._update_due_date_preview())

        for days in [7, 14, 21, 30]:
            ctk.CTkButton(
                btn_row, text=f"{days}d", width=42, height=28,
                fg_color="gray40", hover_color="gray30",
                font=ctk.CTkFont(size=11),
                command=lambda d=days: self._set_loan_days(d)
            ).pack(side="left", padx=2)

        # Dates Display Row
        dates_row = ctk.CTkFrame(loan_box, fg_color="transparent")
        dates_row.pack(fill="x", padx=12, pady=(4, 10))

        today_str = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(
            dates_row, text=f"📅 Issue Date: {today_str}",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 20))

        self.due_date_label = ctk.CTkLabel(
            dates_row, text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1f538d", "#4da6ff")
        )
        self.due_date_label.pack(side="left")
        self._update_due_date_preview()

        # ── Final Action: Issue Book Button ──
        self.issue_btn = ctk.CTkButton(
            self.left_scroll, text="✅  Confirm & Issue Book",
            command=self.issue_book,
            fg_color="#2fa572", hover_color="#238158",
            height=44, font=ctk.CTkFont(size=15, weight="bold")
        )
        self.issue_btn.pack(fill="x", padx=15, pady=(5, 20))

        # ══════════════════════════════════════════════════════════════
        # RIGHT COLUMN: Multi-Tab Explorer & Member Loans Inspector
        # ══════════════════════════════════════════════════════════════
        self.tabview = ctk.CTkTabview(main_layout, fg_color=("gray95", "gray17"))
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        # Tabs
        self.tab_books = self.tabview.add("📚 Book Catalog & Stock")
        self.tab_members = self.tabview.add("👥 Member Directory")
        self.tab_loans = self.tabview.add("📋 Member's Active Loans")
        self.tab_overdue = self.tabview.add("⚠️ Overdue Loans")

        self._build_books_catalog_tab()
        self._build_members_directory_tab()
        self._build_member_loans_tab()
        self._build_overdue_tab()

        # Initial load
        self.refresh_all_data()

    # ──────────────────────────────────────────────────────────────────
    # Left Card Builders (Empty & Populated)
    # ──────────────────────────────────────────────────────────────────
    def _build_empty_member_card(self):
        for w in self.member_card.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.member_card,
            text="⚠️ No member selected yet.\nType a name above or click 'Select' in the Member Directory tab.",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60", justify="center"
        ).pack(pady=14)

    def _update_selected_member_card(self, member):
        for w in self.member_card.winfo_children():
            w.destroy()

        top_row = ctk.CTkFrame(self.member_card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            top_row, text=f"👤  {member['full_name']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        # Member ID Badge
        id_badge = ctk.CTkFrame(top_row, fg_color=("#1f538d", "#14375e"), corner_radius=6)
        id_badge.pack(side="right")
        ctk.CTkLabel(
            id_badge, text=f"ID: #{member['member_id']}",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="white"
        ).pack(padx=8, pady=2)

        # Details row
        details_row = ctk.CTkFrame(self.member_card, fg_color="transparent")
        details_row.pack(fill="x", padx=12, pady=(0, 10))

        contact_text = f"✉️ {member.get('email') or 'No email'}   📞 {member.get('phone') or 'No phone'}"
        ctk.CTkLabel(
            details_row, text=contact_text,
            font=ctk.CTkFont(size=11), text_color="gray60"
        ).pack(side="left")

        # Active loans pill
        active_loans = member.get('active_loans', 0)
        pill_color = "#c23b22" if active_loans >= 3 else ("#1f538d" if active_loans > 0 else "#2fa572")
        pill = ctk.CTkFrame(details_row, fg_color=pill_color, corner_radius=6)
        pill.pack(side="right")
        ctk.CTkLabel(
            pill, text=f"Loans: {active_loans}",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="white"
        ).pack(padx=6, pady=2)

    def _build_empty_book_card(self):
        for w in self.book_card.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.book_card,
            text="⚠️ No book selected yet.\nType a book title above or click 'Select' in the Book Catalog tab.",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray60", justify="center"
        ).pack(pady=14)

    def _update_selected_book_card(self, book):
        for w in self.book_card.winfo_children():
            w.destroy()

        top_row = ctk.CTkFrame(self.book_card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            top_row, text=f"📖  {book['title']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=300, justify="left"
        ).pack(side="left")

        # Book ID Badge
        id_badge = ctk.CTkFrame(top_row, fg_color=("#1f538d", "#14375e"), corner_radius=6)
        id_badge.pack(side="right")
        ctk.CTkLabel(
            id_badge, text=f"Book ID: #{book['book_id']}",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="white"
        ).pack(padx=8, pady=2)

        # Author / Category / ISBN Row
        sub_row = ctk.CTkFrame(self.book_card, fg_color="transparent")
        sub_row.pack(fill="x", padx=12, pady=(2, 8))

        sub_text = f"✍️ {book.get('author') or 'Unknown'}   •   🏷️ {book.get('category') or 'General'}   •   ISBN: {book.get('isbn') or '-'}"
        ctk.CTkLabel(
            sub_row, text=sub_text,
            font=ctk.CTkFont(size=11), text_color="gray60"
        ).pack(side="left")

        # ── 3-Metric Availability Pill Row ──
        stats_row = ctk.CTkFrame(self.book_card, fg_color=("gray80", "gray25"), corner_radius=6)
        stats_row.pack(fill="x", padx=12, pady=(0, 8))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1)

        total = book.get('total_copies', 0)
        available = book.get('available_copies', 0)
        issued = book.get('issued_copies', max(0, total - available))

        # Total copies
        c1 = ctk.CTkFrame(stats_row, fg_color="transparent")
        c1.grid(row=0, column=0, pady=6)
        ctk.CTkLabel(c1, text=str(total), font=ctk.CTkFont(size=16, weight="bold")).pack()
        ctk.CTkLabel(c1, text="Total Copies", font=ctk.CTkFont(size=10), text_color="gray60").pack()

        # Available copies
        c2 = ctk.CTkFrame(stats_row, fg_color="transparent")
        c2.grid(row=0, column=1, pady=6)
        avail_color = "#2fa572" if available > 0 else "#c23b22"
        ctk.CTkLabel(c2, text=str(available), font=ctk.CTkFont(size=16, weight="bold"), text_color=avail_color).pack()
        ctk.CTkLabel(c2, text="Available to Issue", font=ctk.CTkFont(size=10), text_color="gray60").pack()

        # Issued copies
        c3 = ctk.CTkFrame(stats_row, fg_color="transparent")
        c3.grid(row=0, column=2, pady=6)
        ctk.CTkLabel(c3, text=str(issued), font=ctk.CTkFont(size=16, weight="bold"), text_color="#d68a27").pack()
        ctk.CTkLabel(c3, text="Currently Issued", font=ctk.CTkFont(size=10), text_color="gray60").pack()

        # ── Status Banner (In Stock vs Out of Stock) ──
        if available > 0:
            status_frame = ctk.CTkFrame(self.book_card, fg_color=("#e6f4ea", "#1e392a"), corner_radius=6)
            status_frame.pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkLabel(
                status_frame,
                text=f"🟢 In Stock — {available} copies ready for immediate loan",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#137333", "#81c995")
            ).pack(pady=6)
            self.issue_btn.configure(state="normal", text="✅  Confirm & Issue Book", fg_color="#2fa572")
        else:
            status_frame = ctk.CTkFrame(self.book_card, fg_color=("#fce8e6", "#3c2121"), corner_radius=6)
            status_frame.pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkLabel(
                status_frame,
                text="🔴 Out of Stock — All copies are currently loaned out. Cannot issue.",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#c5221f", "#f28b82")
            ).pack(pady=6)
            self.issue_btn.configure(state="disabled", text="❌  Book Currently Unavailable", fg_color="gray45")

    # ──────────────────────────────────────────────────────────────────
    # Autocomplete Handlers
    # ──────────────────────────────────────────────────────────────────
    def _on_member_search_type(self, event=None):
        query = self.member_search_var.get().strip()
        if not query:
            self._hide_member_suggestions()
            return

        matches = MemberController.search_members_autocomplete(query, limit=5)
        if not matches:
            self._hide_member_suggestions()
            return

        # Show suggestion box
        self.member_suggestions_box.pack(fill="x", padx=15, pady=(0, 6))
        for w in self.member_suggestions_box.winfo_children():
            w.destroy()

        for m in matches:
            btn_text = f"👤 #{m['member_id']} - {m['full_name']} ({m.get('email') or m.get('phone') or 'No contact'})"
            btn = ctk.CTkButton(
                self.member_suggestions_box, text=btn_text, anchor="w",
                fg_color="transparent", hover_color=("gray75", "gray30"),
                text_color=("gray10", "gray90"), height=28,
                command=lambda mem=m: self.select_member(mem)
            )
            btn.pack(fill="x", padx=4, pady=2)

    def _hide_member_suggestions(self):
        for w in self.member_suggestions_box.winfo_children():
            w.destroy()
        self.member_suggestions_box.pack_forget()

    def _on_book_search_type(self, event=None):
        query = self.book_search_var.get().strip()
        if not query:
            self._hide_book_suggestions()
            return

        matches = BookController.search_books_autocomplete(query, limit=5)
        if not matches:
            self._hide_book_suggestions()
            return

        self.book_suggestions_box.pack(fill="x", padx=15, pady=(0, 6))
        for w in self.book_suggestions_box.winfo_children():
            w.destroy()

        for b in matches:
            avail_tag = "🟢 Available" if b['available_copies'] > 0 else "🔴 Out of Stock"
            btn_text = f"📖 #{b['book_id']} - {b['title'][:32]} | Avail: {b['available_copies']}/{b['total_copies']} ({avail_tag})"
            btn = ctk.CTkButton(
                self.book_suggestions_box, text=btn_text, anchor="w",
                fg_color="transparent", hover_color=("gray75", "gray30"),
                text_color=("gray10", "gray90"), height=28,
                command=lambda bk=b: self.select_book(bk)
            )
            btn.pack(fill="x", padx=4, pady=2)

    def _hide_book_suggestions(self):
        for w in self.book_suggestions_box.winfo_children():
            w.destroy()
        self.book_suggestions_box.pack_forget()

    def select_member(self, member):
        """Sets the active member and updates UI cards and history tab."""
        self.selected_member = member
        self._hide_member_suggestions()
        self.member_search_var.set(member['full_name'])
        self._update_selected_member_card(member)
        # Update tab 3 with this member's active loans
        self.load_selected_member_loans(member['member_id'], member['full_name'])

    def clear_selected_member(self):
        self.selected_member = None
        self.member_search_var.set("")
        self._hide_member_suggestions()
        self._build_empty_member_card()
        self.load_selected_member_loans(None)

    def select_book(self, book):
        """Sets the active book and updates UI availability cards."""
        self.selected_book = book
        self._hide_book_suggestions()
        self.book_search_var.set(book['title'])
        self._update_selected_book_card(book)

    def clear_selected_book(self):
        self.selected_book = None
        self.book_search_var.set("")
        self._hide_book_suggestions()
        self._build_empty_book_card()
        self.issue_btn.configure(state="normal", text="✅  Confirm & Issue Book", fg_color="#2fa572")

    # ──────────────────────────────────────────────────────────────────
    # Loan Duration & Due Date Calculator
    # ──────────────────────────────────────────────────────────────────
    def _set_loan_days(self, days):
        self.days_entry.delete(0, 'end')
        self.days_entry.insert(0, str(days))
        self._update_due_date_preview()

    def _update_due_date_preview(self):
        days_str = self.days_entry.get().strip()
        try:
            days = int(days_str) if days_str else 14
        except ValueError:
            days = 14
        due_date = datetime.now() + timedelta(days=days)
        self.due_date_label.configure(text=f"⏰ Due Date: {due_date.strftime('%d %b %Y (%a)')}")

    # ──────────────────────────────────────────────────────────────────
    # TAB 1: Book Catalog & Stock Explorer
    # ──────────────────────────────────────────────────────────────────
    def _build_books_catalog_tab(self):
        tab = self.tab_books

        # Search bar
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 8))

        self.catalog_search_entry = ctk.CTkEntry(
            top, placeholder_text="Search catalog by title, author, or ISBN...",
            width=280, height=32
        )
        self.catalog_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.catalog_search_entry.bind("<Return>", lambda e: self.load_catalog_books())

        ctk.CTkButton(
            top, text="Search", width=70, height=32,
            command=self.load_catalog_books
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            top, text="Reset", width=60, height=32,
            fg_color="gray45", hover_color="gray35",
            command=lambda: (self.catalog_search_entry.delete(0, 'end'), self.load_catalog_books())
        ).pack(side="left")

        # Table Header
        header = ctk.CTkFrame(tab, fg_color=("gray85", "gray25"), height=30, corner_radius=6)
        header.pack(fill="x", padx=10, pady=(0, 4))
        cols = ["ID", "Book Title", "Author", "Total", "Avail", "Issued", "Status", "Action"]
        weights = [1, 5, 3, 1, 1, 1, 2, 2]
        for i, (c, w) in enumerate(zip(cols, weights)):
            header.grid_columnconfigure(i, weight=w, minsize=40)
            ctk.CTkLabel(header, text=c, font=ctk.CTkFont(size=11, weight="bold")).grid(
                row=0, column=i, padx=6, pady=4, sticky="w"
            )

        # Scrollable rows
        self.catalog_table_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.catalog_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.catalog_table_frame.grid_columnconfigure(0, weight=1)

    def load_catalog_books(self):
        for w in self.catalog_table_frame.winfo_children():
            w.destroy()

        q = self.catalog_search_entry.get().strip()
        books = BookController.search_books(q) if q else BookController.get_all_books()

        if not books:
            ctk.CTkLabel(
                self.catalog_table_frame, text="No books found in catalog.",
                font=ctk.CTkFont(slant="italic"), text_color="gray60"
            ).pack(pady=20)
            return

        weights = [1, 5, 3, 1, 1, 1, 2, 2]

        for idx, b in enumerate(books):
            bg = ("gray92", "gray20") if idx % 2 == 0 else ("gray87", "gray23")
            row = ctk.CTkFrame(self.catalog_table_frame, fg_color=bg, corner_radius=4)
            row.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=4, pady=3)
            for ci, cw in enumerate(weights):
                inner.grid_columnconfigure(ci, weight=cw, minsize=40)

            total = b['total_copies']
            avail = b['available_copies']
            issued = b.get('issued_copies', max(0, total - avail))
            is_avail = avail > 0

            status_text = "🟢 In Stock" if is_avail else "🔴 Out of Stock"
            status_color = "#2fa572" if is_avail else "#c23b22"

            vals = [
                str(b['book_id']), b['title'][:28], (b['author'] or '')[:18],
                str(total), str(avail), str(issued), status_text
            ]

            for ci, val in enumerate(vals):
                color = status_color if ci == 6 else ("gray10", "gray90")
                bold = "bold" if ci in (0, 4, 6) else "normal"
                ctk.CTkLabel(
                    inner, text=val, font=ctk.CTkFont(size=11, weight=bold),
                    text_color=color, anchor="w"
                ).grid(row=0, column=ci, padx=6, pady=2, sticky="w")

            btn_state = "normal" if is_avail else "disabled"
            btn_color = "#1f538d" if is_avail else "gray50"
            ctk.CTkButton(
                inner, text="Select", width=55, height=26,
                fg_color=btn_color, state=btn_state,
                font=ctk.CTkFont(size=11),
                command=lambda bk=b: self.select_book(bk)
            ).grid(row=0, column=7, padx=6, pady=2, sticky="e")

    # ──────────────────────────────────────────────────────────────────
    # TAB 2: Member Directory Tab
    # ──────────────────────────────────────────────────────────────────
    def _build_members_directory_tab(self):
        tab = self.tab_members

        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 8))

        self.members_search_entry = ctk.CTkEntry(
            top, placeholder_text="Search members by name, email, or phone...",
            width=280, height=32
        )
        self.members_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.members_search_entry.bind("<Return>", lambda e: self.load_directory_members())

        ctk.CTkButton(
            top, text="Search", width=70, height=32,
            command=self.load_directory_members
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            top, text="Reset", width=60, height=32,
            fg_color="gray45", hover_color="gray35",
            command=lambda: (self.members_search_entry.delete(0, 'end'), self.load_directory_members())
        ).pack(side="left")

        # Table Header
        header = ctk.CTkFrame(tab, fg_color=("gray85", "gray25"), height=30, corner_radius=6)
        header.pack(fill="x", padx=10, pady=(0, 4))
        cols = ["ID", "Member Name", "Email", "Phone", "Active Loans", "Action"]
        weights = [1, 5, 4, 3, 2, 2]
        for i, (c, w) in enumerate(zip(cols, weights)):
            header.grid_columnconfigure(i, weight=w, minsize=45)
            ctk.CTkLabel(header, text=c, font=ctk.CTkFont(size=11, weight="bold")).grid(
                row=0, column=i, padx=6, pady=4, sticky="w"
            )

        self.members_table_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.members_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.members_table_frame.grid_columnconfigure(0, weight=1)

    def load_directory_members(self):
        for w in self.members_table_frame.winfo_children():
            w.destroy()

        q = self.members_search_entry.get().strip()
        members = MemberController.search_members(q) if q else MemberController.get_all_members()

        if not members:
            ctk.CTkLabel(
                self.members_table_frame, text="No members found in directory.",
                font=ctk.CTkFont(slant="italic"), text_color="gray60"
            ).pack(pady=20)
            return

        weights = [1, 5, 4, 3, 2, 2]

        for idx, m in enumerate(members):
            bg = ("gray92", "gray20") if idx % 2 == 0 else ("gray87", "gray23")
            row = ctk.CTkFrame(self.members_table_frame, fg_color=bg, corner_radius=4)
            row.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=4, pady=3)
            for ci, cw in enumerate(weights):
                inner.grid_columnconfigure(ci, weight=cw, minsize=45)

            loans = m.get('active_loans', 0)
            vals = [
                str(m['member_id']), m['full_name'][:25],
                (m.get('email') or '-')[:22], (m.get('phone') or '-')[:15],
                f"{loans} active"
            ]

            for ci, val in enumerate(vals):
                bold = "bold" if ci in (0, 4) else "normal"
                color = "#c23b22" if ci == 4 and loans > 2 else ("gray10", "gray90")
                ctk.CTkLabel(
                    inner, text=val, font=ctk.CTkFont(size=11, weight=bold),
                    text_color=color, anchor="w"
                ).grid(row=0, column=ci, padx=6, pady=2, sticky="w")

            ctk.CTkButton(
                inner, text="Select", width=55, height=26,
                fg_color="#1f538d", hover_color="#14375e",
                font=ctk.CTkFont(size=11),
                command=lambda mem=m: self.select_member(mem)
            ).grid(row=0, column=5, padx=6, pady=2, sticky="e")

    # ──────────────────────────────────────────────────────────────────
    # TAB 3: Selected Member's Active Loans
    # ──────────────────────────────────────────────────────────────────
    def _build_member_loans_tab(self):
        tab = self.tab_loans

        self.loans_header_label = ctk.CTkLabel(
            tab, text="No member currently selected.",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.loans_header_label.pack(anchor="w", padx=15, pady=(10, 6))

        # Table header
        header = ctk.CTkFrame(tab, fg_color=("gray85", "gray25"), height=30, corner_radius=6)
        header.pack(fill="x", padx=10, pady=(0, 4))
        cols = ["Txn ID", "Book Title", "Author", "Issue Date", "Due Date", "Status", "Action"]
        weights = [1, 5, 3, 2, 2, 2, 2]
        for i, (c, w) in enumerate(zip(cols, weights)):
            header.grid_columnconfigure(i, weight=w, minsize=40)
            ctk.CTkLabel(header, text=c, font=ctk.CTkFont(size=11, weight="bold")).grid(
                row=0, column=i, padx=6, pady=4, sticky="w"
            )

        self.member_loans_table = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.member_loans_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.member_loans_table.grid_columnconfigure(0, weight=1)

    def load_selected_member_loans(self, member_id, member_name=None):
        for w in self.member_loans_table.winfo_children():
            w.destroy()

        if not member_id:
            self.loans_header_label.configure(
                text="ℹ️ Select a member on the left to inspect their currently borrowed books."
            )
            ctk.CTkLabel(
                self.member_loans_table,
                text="No member selected. Pick a member from Directory or Search box.",
                font=ctk.CTkFont(slant="italic"), text_color="gray60"
            ).pack(pady=30)
            return

        name = member_name or f"Member #{member_id}"
        loans = TransactionController.get_member_active_loans(member_id)

        self.loans_header_label.configure(
            text=f"📋 Active Borrowed Books for {name} ({len(loans)} Active Loan{'s' if len(loans) != 1 else ''}):"
        )

        if not loans:
            ctk.CTkLabel(
                self.member_loans_table,
                text="✅ This member currently has no borrowed books (0 active loans).",
                font=ctk.CTkFont(size=12, slant="italic"), text_color="#2fa572"
            ).pack(pady=30)
            return

        weights = [1, 5, 3, 2, 2, 2, 2]

        for idx, t in enumerate(loans):
            bg = ("gray92", "gray20") if idx % 2 == 0 else ("gray87", "gray23")
            row = ctk.CTkFrame(self.member_loans_table, fg_color=bg, corner_radius=4)
            row.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=4, pady=3)
            for ci, cw in enumerate(weights):
                inner.grid_columnconfigure(ci, weight=cw, minsize=40)

            is_overdue = t['status'] == 'Overdue'
            status_color = "#c23b22" if is_overdue else "#2fa572"

            vals = [
                f"#{t['transaction_id']}", t['title'][:28], (t.get('author') or '')[:18],
                str(t['issue_date'])[:10], str(t['due_date'])[:10], t['status']
            ]

            for ci, val in enumerate(vals):
                color = status_color if ci == 5 else ("gray10", "gray90")
                bold = "bold" if ci in (0, 5) else "normal"
                ctk.CTkLabel(
                    inner, text=val, font=ctk.CTkFont(size=11, weight=bold),
                    text_color=color, anchor="w"
                ).grid(row=0, column=ci, padx=6, pady=2, sticky="w")

            # Instant Return Button directly from this tab
            ctk.CTkButton(
                inner, text="Return", width=60, height=26,
                fg_color="#1f538d", hover_color="#14375e",
                font=ctk.CTkFont(size=11),
                command=lambda tid=t['transaction_id']: self._quick_return(tid)
            ).grid(row=0, column=6, padx=6, pady=2, sticky="e")

    def _quick_return(self, transaction_id):
        if messagebox.askyesno("Confirm Return", f"Return book for transaction #{transaction_id} now?"):
            try:
                res = TransactionController.return_book(transaction_id)
                messagebox.showinfo("Success", f"'{res['book_title']}' successfully returned!")
                self.refresh_all_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ──────────────────────────────────────────────────────────────────
    # TAB 4: Overdue Loans Tab
    # ──────────────────────────────────────────────────────────────────
    def _build_overdue_tab(self):
        tab = self.tab_overdue

        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(
            top, text="⚠️ Overdue Books Requiring Immediate Action / Follow-Up",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#c23b22"
        ).pack(side="left")

        ctk.CTkButton(
            top, text="🔄 Refresh", width=75, height=28,
            command=self.load_overdue_loans
        ).pack(side="right")

        header = ctk.CTkFrame(tab, fg_color=("gray85", "gray25"), height=30, corner_radius=6)
        header.pack(fill="x", padx=10, pady=(0, 4))
        cols = ["Txn ID", "Book Title", "Member Name", "Phone", "Due Date", "Action"]
        weights = [1, 5, 4, 3, 2, 2]
        for i, (c, w) in enumerate(zip(cols, weights)):
            header.grid_columnconfigure(i, weight=w, minsize=40)
            ctk.CTkLabel(header, text=c, font=ctk.CTkFont(size=11, weight="bold")).grid(
                row=0, column=i, padx=6, pady=4, sticky="w"
            )

        self.overdue_table_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.overdue_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.overdue_table_frame.grid_columnconfigure(0, weight=1)

    def load_overdue_loans(self):
        for w in self.overdue_table_frame.winfo_children():
            w.destroy()

        overdue_list = TransactionController.get_overdue_transactions()
        if not overdue_list:
            ctk.CTkLabel(
                self.overdue_table_frame,
                text="🎉 Excellent! There are currently no overdue books in the library.",
                font=ctk.CTkFont(size=12, slant="italic"), text_color="#2fa572"
            ).pack(pady=30)
            return

        weights = [1, 5, 4, 3, 2, 2]

        for idx, t in enumerate(overdue_list):
            bg = ("gray92", "gray20") if idx % 2 == 0 else ("gray87", "gray23")
            row = ctk.CTkFrame(self.overdue_table_frame, fg_color=bg, corner_radius=4)
            row.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=4, pady=3)
            for ci, cw in enumerate(weights):
                inner.grid_columnconfigure(ci, weight=cw, minsize=40)

            vals = [
                f"#{t['transaction_id']}", t['title'][:28], t['full_name'][:20],
                t.get('phone') or 'No phone', str(t['due_date'])[:10]
            ]

            for ci, val in enumerate(vals):
                bold = "bold" if ci in (0, 4) else "normal"
                color = "#c23b22" if ci == 4 else ("gray10", "gray90")
                ctk.CTkLabel(
                    inner, text=val, font=ctk.CTkFont(size=11, weight=bold),
                    text_color=color, anchor="w"
                ).grid(row=0, column=ci, padx=6, pady=2, sticky="w")

            ctk.CTkButton(
                inner, text="Return", width=60, height=26,
                fg_color="#c23b22", hover_color="#8b2512",
                font=ctk.CTkFont(size=11),
                command=lambda tid=t['transaction_id']: self._quick_return(tid)
            ).grid(row=0, column=5, padx=6, pady=2, sticky="e")

    # ──────────────────────────────────────────────────────────────────
    # Global Refresh & Issue Book Execution
    # ──────────────────────────────────────────────────────────────────
    def refresh_all_data(self):
        self.load_catalog_books()
        self.load_directory_members()
        self.load_overdue_loans()
        if self.selected_member:
            # Re-fetch updated member info
            m = MemberController.get_member_by_id(self.selected_member['member_id'])
            if m:
                self.selected_member = m
                self._update_selected_member_card(m)
                self.load_selected_member_loans(m['member_id'], m['full_name'])
        if self.selected_book:
            b = BookController.get_book_by_id(self.selected_book['book_id'])
            if b:
                self.selected_book = b
                self._update_selected_book_card(b)

    def issue_book(self):
        # 1. Poka-Yoke Validation: Check Member
        if not self.selected_member:
            query = self.member_search_var.get().strip()
            if query:
                # Try finding by name or ID
                member = MemberController.get_member_by_name(query)
                if not member:
                    try:
                        member = MemberController.get_member_by_id(int(query))
                    except ValueError:
                        member = None
                if member:
                    self.select_member(member)
                else:
                    messagebox.showerror(
                        "Validation Error",
                        f"No registered member found matching '{query}'.\nPlease select a member from the directory."
                    )
                    return
            else:
                messagebox.showerror("Validation Error", "Please select or search for a Member first.")
                return

        # 2. Poka-Yoke Validation: Check Book
        if not self.selected_book:
            query = self.book_search_var.get().strip()
            if query:
                book = BookController.get_book_by_title(query)
                if not book:
                    try:
                        book = BookController.get_book_by_id(int(query))
                    except ValueError:
                        book = None
                if book:
                    self.select_book(book)
                else:
                    messagebox.showerror(
                        "Validation Error",
                        f"No book found in catalog matching '{query}'.\nPlease select a book from the catalog."
                    )
                    return
            else:
                messagebox.showerror("Validation Error", "Please select or search for a Book first.")
                return

        # 3. Poka-Yoke Validation: Check Availability
        if self.selected_book['available_copies'] <= 0:
            messagebox.showerror(
                "Book Unavailable",
                f"Cannot issue '{self.selected_book['title']}':\nAll {self.selected_book['total_copies']} copies are currently loaned out."
            )
            return

        # 4. Loan Duration Validation
        days_str = self.days_entry.get().strip()
        try:
            days = int(days_str) if days_str else 14
            if days <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Loan duration must be a positive number of days (e.g. 14).")
            return

        # 5. Execute Issue Transaction
        book_id = self.selected_book['book_id']
        member_id = self.selected_member['member_id']

        try:
            txn = TransactionController.issue_book(book_id, member_id, days_to_due=days)
            due_fmt = datetime.strptime(txn['due_date'], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
            messagebox.showinfo(
                "Book Issued Successfully!",
                f"Book: {txn['book_title']} (ID: #{txn['book_id']})\n"
                f"Member: {txn['member_name']} (ID: #{txn['member_id']})\n"
                f"Due Date: {due_fmt}\n"
                f"Remaining Available Copies: {txn['remaining_available']}\n\n"
                f"Transaction #{txn['transaction_id']} recorded."
            )

            # Reset Book selection for next issue (keep member selected for convenience if multiple books)
            self.clear_selected_book()
            self.refresh_all_data()

        except ValueError as e:
            messagebox.showerror("Issue Restriction", str(e))
        except Exception as e:
            messagebox.showerror("System Error", f"Unexpected error occurred:\n{e}")


# ════════════════════════════════════════════════════════════════════════
# ReturnBookView: Enhanced with Search & Filter by Member/Book Name
# ════════════════════════════════════════════════════════════════════════
class ReturnBookView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller

        # ── Breadcrumb ──
        BreadcrumbHeader(
            self, nav_controller,
            [("🏠 Home", "Dashboard"), ("Return Book", None)]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        # ── Header bar ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            header, text="Book Return Management",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="Search by Member Name, Book Title, ISBN, or Transaction ID",
            font=ctk.CTkFont(size=12), text_color="gray60"
        ).pack(side="right")

        # ── Top Control Bar: Search Filter & Direct Return ──
        ctrl_frame = ctk.CTkFrame(self, fg_color=("gray95", "gray18"), corner_radius=8)
        ctrl_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Search Bar
        ctk.CTkLabel(ctrl_frame, text="🔍 Filter:", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=(15, 5), pady=12
        )
        self.search_entry = ctk.CTkEntry(
            ctrl_frame, width=280, height=34,
            placeholder_text="Search by Member Name or Book Title..."
        )
        self.search_entry.pack(side="left", padx=(0, 8), pady=12)
        self.search_entry.bind("<Return>", lambda e: self.load_active_transactions())

        ctk.CTkButton(
            ctrl_frame, text="Search", width=75, height=34,
            command=self.load_active_transactions
        ).pack(side="left", padx=(0, 5), pady=12)

        ctk.CTkButton(
            ctrl_frame, text="Reset", width=65, height=34,
            fg_color="gray45", hover_color="gray35",
            command=self._reset_search
        ).pack(side="left", padx=(0, 15), pady=12)

        # Quick Manual Return by ID
        sep = ctk.CTkFrame(ctrl_frame, width=2, height=26, fg_color="gray50")
        sep.pack(side="left", padx=10, pady=12)

        ctk.CTkLabel(ctrl_frame, text="Txn ID:", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=(10, 5), pady=12
        )
        self.txn_entry = ctk.CTkEntry(ctrl_frame, width=90, height=34, placeholder_text="e.g. 1")
        self.txn_entry.pack(side="left", padx=(0, 8), pady=12)
        self.txn_entry.bind("<Return>", lambda e: self.return_book())

        ctk.CTkButton(
            ctrl_frame, text="↩️  Return", command=self.return_book,
            fg_color="#1f538d", hover_color="#14375e", width=85, height=34,
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=(0, 15), pady=12)

        # Refresh button
        ctk.CTkButton(
            ctrl_frame, text="🔄 Refresh", command=self.load_active_transactions,
            fg_color="gray50", hover_color="gray40", width=80, height=34
        ).pack(side="right", padx=15, pady=12)

        # ── Column Header ──
        col_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray25"), height=30, corner_radius=6)
        col_frame.pack(fill="x", padx=20, pady=(0, 4))
        headers = ["Txn ID", "Book Title", "Member Name", "Issue Date", "Due Date", "Status", "Action"]
        weights = [1, 5, 4, 2, 2, 2, 2]
        for i, (h, w) in enumerate(zip(headers, weights)):
            col_frame.grid_columnconfigure(i, weight=w, minsize=40)
            ctk.CTkLabel(col_frame, text=h, font=ctk.CTkFont(size=11, weight="bold")).grid(
                row=0, column=i, padx=8, pady=4, sticky="w"
            )

        # ── Scrollable Table ──
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.load_active_transactions()

    def _reset_search(self):
        self.search_entry.delete(0, 'end')
        self.load_active_transactions()

    def return_book(self):
        txn_id_text = self.txn_entry.get().strip()
        if not txn_id_text:
            messagebox.showerror("Validation Error", "Please enter a Transaction ID to return.")
            return
        try:
            txn_id = int(txn_id_text)
        except ValueError:
            messagebox.showerror("Validation Error", "Transaction ID must be a valid integer.")
            return

        try:
            res = TransactionController.return_book(txn_id)
            messagebox.showinfo(
                "Return Successful",
                f"Transaction #{res['transaction_id']} marked as returned!\n\n"
                f"Book: {res['book_title']}\n"
                f"Member: {res['member_name']}\n"
                f"Return Date: {res['return_date']}\n\n"
                f"Book inventory copy count has been automatically incremented."
            )
            self.txn_entry.delete(0, 'end')
            self.load_active_transactions()
        except ValueError as e:
            messagebox.showerror("Return Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", str(e))

    def load_active_transactions(self):
        if not self.winfo_exists() or not self.table_frame.winfo_children:
            return
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip()
        txns = TransactionController.get_active_transactions(query)

        if not txns:
            msg = f"No active transactions found matching '{query}'." if query else "✅ No active issues or overdue books found in the library."
            ctk.CTkLabel(
                self.table_frame, text=msg,
                font=ctk.CTkFont(size=13, slant="italic"), text_color="gray60"
            ).pack(pady=40)
            return

        weights = [1, 5, 4, 2, 2, 2, 2]

        for row_idx, txn in enumerate(txns):
            bg = ("gray92", "gray20") if row_idx % 2 == 0 else ("gray87", "gray23")
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg, corner_radius=4)
            row_frame.pack(fill="x", pady=1)

            inner = ctk.CTkFrame(row_frame, fg_color="transparent")
            inner.pack(fill="x", padx=4, pady=3)
            for ci, cw in enumerate(weights):
                inner.grid_columnconfigure(ci, weight=cw, minsize=40)

            is_overdue = txn.get('status') == 'Overdue'
            status_color = "#c23b22" if is_overdue else "#2fa572"

            vals = [
                f"#{txn['transaction_id']}",
                txn['title'][:28],
                txn['full_name'][:22],
                str(txn['issue_date'])[:10],
                str(txn['due_date'])[:10],
                txn['status']
            ]

            for ci, val in enumerate(vals):
                color = status_color if ci == 5 else ("gray10", "gray90")
                bold = "bold" if ci in (0, 5) else "normal"
                ctk.CTkLabel(
                    inner, text=val, font=ctk.CTkFont(size=11, weight=bold),
                    text_color=color, anchor="w"
                ).grid(row=0, column=ci, padx=8, pady=3, sticky="w")

            ctk.CTkButton(
                inner, text="Return", width=65, height=26,
                fg_color="#1f538d", hover_color="#14375e",
                font=ctk.CTkFont(size=11),
                command=lambda t=txn['transaction_id']: self.auto_return(t)
            ).grid(row=0, column=6, padx=8, pady=3, sticky="e")

    def auto_return(self, txn_id):
        self.txn_entry.delete(0, 'end')
        self.txn_entry.insert(0, str(txn_id))
        self.return_book()
