# User Manual - Library Management System
## Developed for Fundamentals of Total Quality Management (TQM) - Q14: Improve Navigation

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```
3. The dashboard will appear as the default screen with live statistics (Total Books, Members, Issued, Overdue).

## Navigation Guide
- **Sidebar:** Access any core module (Dashboard, Books, Members, Issue Book, Return Book, Reports).
- **Shortcuts & Help:** Click the `⌨️ Shortcuts & Help` button in the sidebar to review all keyboard shortcuts.
- **Breadcrumbs:** Click `🏠 Home` or any intermediate crumb in the top bar to jump back in the hierarchy.
- **Dashboard Tiles:** Click any of the 10 interactive tiles (e.g., "➕ Add New Book", "📤 Issue Book") to open that operation directly.

## Keyboard Shortcuts
- `Ctrl + D`: Open Dashboard (Home)
- `Ctrl + B`: Open Books Management view
- `Ctrl + M`: Open Members Management view
- `Ctrl + I`: Open Issue Book view
- `Ctrl + R`: Open Return Book view
- `Ctrl + P`: Open Reports & Analytics view
- `Ctrl + F`: Focus on the search field (in Books or Members views)
- `Ctrl + N`: Open the Add New Book/Member dialog (in their respective views)
- `Esc`: Close open modal dialogs or return to Dashboard

## Enhanced Book Issue Operations
The Book Issue module features real-time search, autocomplete, and live availability tracking:

1. **Selecting a Member by Name or ID:**
   - In the **Member Selection** field, start typing the member's name (e.g. `Kamlesh`).
   - A live suggestion box appears. Click the member or press Enter to select.
   - Alternatively, browse the **👥 Member Directory** tab on the right and click `Select`.
   - The **Selected Member Card** displays the member's ID badge, contact details, and their current active loan count.
   - The **📋 Member's Active Loans** tab on the right immediately updates to display all books currently loaned to that member.

2. **Selecting a Book by Title, Author, or ISBN:**
   - In the **Book Selection** field, start typing the book title (e.g. `Clean Code`).
   - A live suggestion box displays matching titles along with stock status (`🟢 Available` or `🔴 Out of Stock`).
   - Click the book to select it.
   - Alternatively, browse the **📚 Book Catalog & Stock** tab on the right and click `Select`.
   - The **Selected Book & Availability Card** displays:
     - Total inventory copies
     - Available copies ready for loan
     - Currently issued copies
     - Live stock status badge (Green if available, Red if out of stock).

3. **Setting Loan Duration & Confirming Issue:**
   - Click one of the duration preset buttons (`7d`, `14d`, `21d`, `30d`) or type custom days.
   - The live **Due Date** preview automatically recalculates the exact return deadline.
   - Click **`✅ Confirm & Issue Book`**.
   - If the book is available, the transaction is saved, available stock is reduced by 1, and a detailed confirmation appears.
   - If the book is out of stock or the member already has an active copy, the system blocks the transaction (Poka-Yoke).

4. **In-Context Returns from Issue View:**
   - If a member is borrowing a new book while returning an old one, navigate to the **📋 Member's Active Loans** tab on the right.
   - Click the **`Return`** button directly next to any of their borrowed books to return it instantly.

## Return Book Operations
1. Open **Return Book** from the sidebar or press `Ctrl + R`.
2. Use the **Filter / Search bar** to find transactions by **Member Name**, **Book Title**, **ISBN**, or **Transaction ID**.
3. Overdue books are highlighted with red status badges.
4. Click **`Return`** next to any transaction to complete the return and restore inventory stock.

## Core CRUD Operations
- **Add Book:** Go to Books (`Ctrl + B`) -> Click `+ Add New Book` (`Ctrl + N`) -> Fill details -> Save.
- **Edit Book:** Go to Books -> Click `Edit` next to any book -> Update fields -> Save Changes.
- **Delete Book:** Go to Books -> Click `Delete` (safeguarded: cannot delete if copies are actively loaned).
- **Register Member:** Go to Members (`Ctrl + M`) -> Click `+ Register Member` (`Ctrl + N`) -> Fill details -> Register.
- **Edit Member:** Go to Members -> Click `Edit` next to any member -> Update fields -> Save Changes.
- **Delete Member:** Go to Members -> Click `Delete` (safeguarded: cannot delete if member has active or overdue loans).
- **Reports:** Go to Reports (`Ctrl + P`) to view real-time graphical status charts of library operations.
