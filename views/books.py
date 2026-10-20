import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.book_controller import BookController
import tkinter.messagebox as messagebox


class BooksView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, open_add=False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller

        # ── Breadcrumb ──
        BreadcrumbHeader(
            self, nav_controller,
            [("🏠 Home", "Dashboard"), ("Books", None)]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        # ── Header bar ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            header, text="Books Management",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        # Right-side buttons
        ctk.CTkButton(
            header, text="+ Add New Book (Ctrl+N)",
            command=self.show_add_book_dialog,
            fg_color="#2fa572", hover_color="#238158",
            font=ctk.CTkFont(size=13, weight="bold"), height=36
        ).pack(side="right", padx=(10, 0))

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by title, author, ISBN or category... (Ctrl+F)",
            width=380, height=36
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self.load_books())

        ctk.CTkButton(
            search_frame, text="Search", width=90, height=36,
            command=self.load_books
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            search_frame, text="Reset", width=80, height=36,
            fg_color="gray45", hover_color="gray35",
            command=self.reset_search
        ).pack(side="left")

        # ── Column header row ──
        col_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"), corner_radius=6)
        col_frame.pack(fill="x", padx=20, pady=(0, 2))
        self._build_col_headers(col_frame)

        # ── Scrollable table body ──
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.load_books()

        if open_add:
            self.after(200, self.show_add_book_dialog)

    def focus_search(self):
        """Focus the search box and select existing text."""
        if self.winfo_exists() and hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
            self.search_entry.focus_set()
            self.search_entry.select_range(0, 'end')

    def open_add_dialog(self):
        """Open the Add New Book modal dialog."""
        if self.winfo_exists():
            self.show_add_book_dialog()

    def _build_col_headers(self, parent):
        headers = ["ID", "ISBN", "Title", "Author", "Category", "Copies (Total/Avail)", "Actions"]
        col_weights = [1, 2, 5, 4, 3, 3, 3]
        for i, w in enumerate(col_weights):
            parent.grid_columnconfigure(i, weight=w, minsize=60)
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                parent, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("gray20", "gray90")
            ).grid(row=0, column=i, padx=10, pady=6, sticky="w")

    def reset_search(self):
        self.search_entry.delete(0, "end")
        self.load_books()

    def load_books(self):
        if not self.winfo_exists() or not self.table_frame.winfo_exists():
            return

        # Clear rows
        for w in self.table_frame.winfo_children():
            w.destroy()

        query = self.search_entry.get().strip()
        try:
            books = BookController.search_books(query) if query else BookController.get_all_books()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books:\n{e}")
            return

        if not books:
            ctk.CTkLabel(
                self.table_frame,
                text="No books found. Click '+ Add New Book' to get started.",
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color="gray60"
            ).grid(row=0, column=0, pady=40)
            return

        col_weights = [1, 2, 5, 4, 3, 3, 3]

        for row_idx, book in enumerate(books):
            bg = ("gray92", "gray18") if row_idx % 2 == 0 else ("gray86", "gray22")
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg, corner_radius=4)
            row_frame.grid(row=row_idx, column=0, sticky="ew", padx=0, pady=1)
            row_frame.grid_columnconfigure(0, weight=1)

            inner = ctk.CTkFrame(row_frame, fg_color="transparent")
            inner.pack(fill="x")
            for ci, cw in enumerate(col_weights):
                inner.grid_columnconfigure(ci, weight=cw, minsize=60)

            values = [
                str(book['book_id']),
                book['isbn'] or "",
                book['title'] or "",
                book['author'] or "",
                book['category'] or "-",
                f"{book['total_copies']} / {book['available_copies']}",
            ]
            for ci, val in enumerate(values):
                ctk.CTkLabel(
                    inner, text=val,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                ).grid(row=0, column=ci, padx=10, pady=6, sticky="w")

            # Action buttons
            btn_cell = ctk.CTkFrame(inner, fg_color="transparent")
            btn_cell.grid(row=0, column=6, padx=6, pady=4, sticky="e")

            ctk.CTkButton(
                btn_cell, text="Edit", width=60, height=28,
                fg_color="#1f538d", hover_color="#14375e",
                font=ctk.CTkFont(size=12),
                command=lambda b=book: self.show_edit_book_dialog(b)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                btn_cell, text="Delete", width=60, height=28,
                fg_color="#c23b22", hover_color="#8b2512",
                font=ctk.CTkFont(size=12),
                command=lambda b=book: self.delete_book(b['book_id'])
            ).pack(side="left")

    def _make_dialog(self, title, geometry="460x560"):
        """Creates a properly sized, centered, modal CTkToplevel."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())

        dialog.update_idletasks()
        try:
            pw = self.winfo_toplevel().winfo_x()
            py = self.winfo_toplevel().winfo_y()
            pw2 = self.winfo_toplevel().winfo_width()
            py2 = self.winfo_toplevel().winfo_height()
            w = int(geometry.split("x")[0])
            h = int(geometry.split("x")[1])
            x = max(10, pw + (pw2 - w) // 2)
            y = max(10, py + (py2 - h) // 2)
            dialog.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            dialog.geometry(geometry)

        def _safe_grab():
            try:
                if dialog.winfo_exists():
                    dialog.grab_set()
            except Exception:
                pass

        dialog.after(150, _safe_grab)
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        return dialog

    def show_add_book_dialog(self):
        dialog = self._make_dialog("Add New Book", "460x560")

        ctk.CTkLabel(
            dialog, text="Add New Book",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 15))

        fields = [
            ("ISBN *", "isbn", ""),
            ("Title *", "title", ""),
            ("Author *", "author", ""),
            ("Category", "category", ""),
            ("Publisher", "publisher", ""),
            ("Total Copies *", "total_copies", "1"),
        ]

        entries = {}
        for label, key, default in fields:
            ctk.CTkLabel(dialog, text=label, anchor="w", font=ctk.CTkFont(size=12)).pack(
                fill="x", padx=30, pady=(6, 0)
            )
            entry = ctk.CTkEntry(dialog, width=380, height=34)
            if default:
                entry.insert(0, default)
            entry.pack(padx=30, pady=(2, 0))
            entries[key] = entry

        def _focus_first():
            try:
                if dialog.winfo_exists() and entries["isbn"].winfo_exists():
                    entries["isbn"].focus_set()
            except Exception:
                pass
        dialog.after(200, _focus_first)

        def save(event=None):
            try:
                BookController.add_book(
                    entries["isbn"].get(),
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["category"].get(),
                    entries["publisher"].get(),
                    entries["total_copies"].get(),
                )
                dialog.destroy()
                self.load_books()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error:\n{e}", parent=dialog)

        btn = ctk.CTkButton(
            dialog, text="Save Book", command=save,
            fg_color="#2fa572", hover_color="#238158",
            height=40, font=ctk.CTkFont(size=14, weight="bold")
        )
        btn.pack(pady=20, padx=30, fill="x")
        dialog.bind("<Return>", save)

    def show_edit_book_dialog(self, book):
        dialog = self._make_dialog(f"Edit Book  (ID: {book['book_id']})", "460x560")

        ctk.CTkLabel(
            dialog, text=f"Edit Book — {book.get('title', '')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400
        ).pack(pady=(20, 15))

        fields = [
            ("ISBN *", "isbn", book.get("isbn", "") or ""),
            ("Title *", "title", book.get("title", "") or ""),
            ("Author *", "author", book.get("author", "") or ""),
            ("Category", "category", book.get("category", "") or ""),
            ("Publisher", "publisher", book.get("publisher", "") or ""),
            ("Total Copies *", "total_copies", str(book.get("total_copies", 1))),
        ]

        entries = {}
        for label, key, default in fields:
            ctk.CTkLabel(dialog, text=label, anchor="w", font=ctk.CTkFont(size=12)).pack(
                fill="x", padx=30, pady=(6, 0)
            )
            entry = ctk.CTkEntry(dialog, width=380, height=34)
            entry.insert(0, default)
            entry.pack(padx=30, pady=(2, 0))
            entries[key] = entry

        def _focus_first():
            try:
                if dialog.winfo_exists() and entries["isbn"].winfo_exists():
                    entries["isbn"].focus_set()
            except Exception:
                pass
        dialog.after(200, _focus_first)

        def save_changes(event=None):
            try:
                BookController.update_book(
                    book["book_id"],
                    entries["isbn"].get(),
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["category"].get(),
                    entries["publisher"].get(),
                    entries["total_copies"].get(),
                )
                dialog.destroy()
                self.load_books()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error:\n{e}", parent=dialog)

        ctk.CTkButton(
            dialog, text="Update Book", command=save_changes,
            fg_color="#1f538d", hover_color="#14375e",
            height=40, font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20, padx=30, fill="x")
        dialog.bind("<Return>", save_changes)

    def delete_book(self, book_id):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this book?\nThis action cannot be undone."
        )
        if confirm:
            try:
                BookController.delete_book(book_id)
                self.load_books()
            except ValueError as e:
                messagebox.showerror("Cannot Delete", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))
