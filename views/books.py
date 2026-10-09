import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.book_controller import BookController
import tkinter.messagebox as messagebox

class BooksView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Books", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Books Management", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(header_frame, placeholder_text="Search Books... (Ctrl+F)", width=250)
        self.search_entry.pack(side="left", padx=(20, 10))
        self.search_entry.bind("<Return>", lambda e: self.load_books())
        
        ctk.CTkButton(header_frame, text="Search", width=80, command=self.load_books).pack(side="left")
        ctk.CTkButton(header_frame, text="Reset", width=70, fg_color="gray50", hover_color="gray40", command=self.reset_search).pack(side="left", padx=(5, 0))
        
        ctk.CTkButton(header_frame, text="+ Add New Book (Ctrl+N)", command=self.show_add_book_dialog).pack(side="right")
        
        # Table frame
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Setup safe shortcuts
        self._setup_shortcuts()
        self.load_books()

    def _setup_shortcuts(self):
        def _focus_search(e=None):
            if self.winfo_exists() and hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
                self.search_entry.focus_set()
                return "break"

        def _open_add(e=None):
            if self.winfo_exists():
                self.show_add_book_dialog()
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
        self.load_books()

    def load_books(self):
        if not self.winfo_exists() or not self.table_frame.winfo_exists():
            return

        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip()
        if search_query:
            books = BookController.search_books(search_query)
        else:
            books = BookController.get_all_books()
            
        headers = ["ID", "ISBN", "Title", "Author", "Category", "Copies (Total/Avail)", "Actions"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=10, pady=5, sticky="w")
            
        if not books:
            ctk.CTkLabel(self.table_frame, text="No books found.", font=ctk.CTkFont(slant="italic")).grid(row=1, column=0, columnspan=7, pady=20)
            return

        for row, book in enumerate(books, start=1):
            ctk.CTkLabel(self.table_frame, text=str(book['book_id'])).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=book['isbn']).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=book['title']).grid(row=row, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=book['author']).grid(row=row, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=book['category'] or "-").grid(row=row, column=4, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{book['total_copies']} / {book['available_copies']}").grid(row=row, column=5, padx=10, pady=5, sticky="w")
            
            # Actions: Edit and Delete
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=6, padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="Edit", width=55, fg_color="#1f538d", hover_color="#14375e",
                          command=lambda b=book: self.show_edit_book_dialog(b)).pack(side="left", padx=(0, 5))
            ctk.CTkButton(btn_frame, text="Delete", width=55, fg_color="#c23b22", hover_color="#8b2512", 
                          command=lambda b=book: self.delete_book(b['book_id'])).pack(side="left")

    def show_add_book_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Book")
        dialog.geometry("420x520")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        entries = {}
        fields = [
            ("ISBN *", "isbn"),
            ("Title *", "title"),
            ("Author *", "author"), 
            ("Category", "category"),
            ("Publisher", "publisher"),
            ("Total Copies *", "total_copies")
        ]
        
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).pack(pady=(8, 0))
            entry = ctk.CTkEntry(dialog, width=320)
            entry.pack(pady=4)
            if key == "total_copies":
                entry.insert(0, "1")
            entries[key] = entry
            if i == 0:
                entry.focus_set()
                
        def save():
            try:
                BookController.add_book(
                    entries["isbn"].get(),
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["category"].get(),
                    entries["publisher"].get(),
                    entries["total_copies"].get()
                )
                dialog.destroy()
                self.load_books()
            except Exception as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
                
        ctk.CTkButton(dialog, text="Save Book", command=save, fg_color="#2fa572").pack(pady=20)

    def show_edit_book_dialog(self, book):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Book #{book['book_id']}")
        dialog.geometry("420x520")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.bind("<Escape>", lambda e: dialog.destroy())

        entries = {}
        fields = [
            ("ISBN *", "isbn", book.get('isbn', '')),
            ("Title *", "title", book.get('title', '')),
            ("Author *", "author", book.get('author', '')),
            ("Category", "category", book.get('category', '') or ''),
            ("Publisher", "publisher", book.get('publisher', '') or ''),
            ("Total Copies *", "total_copies", str(book.get('total_copies', 1)))
        ]

        for i, (label, key, val) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).pack(pady=(8, 0))
            entry = ctk.CTkEntry(dialog, width=320)
            entry.insert(0, val)
            entry.pack(pady=4)
            entries[key] = entry
            if i == 0:
                entry.focus_set()

        def save_changes():
            try:
                BookController.update_book(
                    book['book_id'],
                    entries["isbn"].get(),
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["category"].get(),
                    entries["publisher"].get(),
                    entries["total_copies"].get()
                )
                dialog.destroy()
                self.load_books()
            except Exception as e:
                messagebox.showerror("Update Error", str(e), parent=dialog)

        ctk.CTkButton(dialog, text="Update Book", command=save_changes, fg_color="#1f538d").pack(pady=20)

    def delete_book(self, book_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?"):
            try:
                BookController.delete_book(book_id)
                self.load_books()
            except Exception as e:
                messagebox.showerror("Error", str(e))

