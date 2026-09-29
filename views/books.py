import customtkinter as ctk
from views.components import BreadcrumbHeader
from controllers.book_controller import BookController
import tkinter.messagebox as messagebox

class BooksView(ctk.CTkFrame):
    def __init__(self, master, nav_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.nav_controller = nav_controller
        BreadcrumbHeader(self, nav_controller, [("Home", "Dashboard"), ("Books", None)]).pack(anchor="w", padx=20, pady=(20, 10))
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Books Management", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        self.search_entry = ctk.CTkEntry(header_frame, placeholder_text="Search Books... (Ctrl+F)", width=250)
        self.search_entry.pack(side="left", padx=(20, 10))
        ctk.CTkButton(header_frame, text="Search", width=80, command=self.load_books).pack(side="left")
        ctk.CTkButton(header_frame, text="+ Add New Book (Ctrl+N)", command=self.show_add_book_dialog).pack(side="right")
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.load_books()

    def load_books(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        search_query = self.search_entry.get().strip()
        books = BookController.search_books(search_query) if search_query else BookController.get_all_books()
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
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=6, padx=10, pady=5)
            ctk.CTkButton(btn_frame, text="Delete", width=60, fg_color="red", hover_color="darkred", command=lambda b=book: self.delete_book(b['book_id'])).pack(side="left")

    def show_add_book_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Book")
        dialog.geometry("400x500")
        entries = {}
        fields = [("ISBN", "isbn"), ("Title", "title"), ("Author", "author"), ("Category", "category"), ("Publisher", "publisher"), ("Total Copies", "total_copies")]
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).pack(pady=(10, 0))
            entry = ctk.CTkEntry(dialog, width=300)
            entry.pack(pady=5)
            entries[key] = entry
        def save():
            try:
                BookController.add_book(entries["isbn"].get(), entries["title"].get(), entries["author"].get(), entries["category"].get(), entries["publisher"].get(), entries["total_copies"].get())
                dialog.destroy()
                self.load_books()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ctk.CTkButton(dialog, text="Save Book", command=save).pack(pady=20)

    def delete_book(self, book_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?"):
            try:
                BookController.delete_book(book_id)
                self.load_books()
            except Exception as e:
                messagebox.showerror("Error", str(e))
