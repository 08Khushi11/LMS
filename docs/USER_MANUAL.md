# User Manual - Library Management System

## Getting Started
1. Run `python main.py` to start the application.
2. The dashboard will appear as the default screen.

## Navigation Guide
- **Sidebar:** Use the buttons on the left sidebar to access different modules (Dashboard, Books, Members, Issue, Return, Reports).
- **Breadcrumbs:** Click any breadcrumb link at the top of the page to go back to a previous section.
- **Dashboard Tiles:** Click on the statistics tiles (e.g., "Total Books") or quick action tiles (e.g., "Add New Book") on the Dashboard to jump directly to the relevant screen.

## Keyboard Shortcuts
- `Ctrl + D`: Open Dashboard (Home)
- `Ctrl + B`: Open Books view
- `Ctrl + M`: Open Members view
- `Ctrl + I`: Open Issue Book view
- `Ctrl + R`: Open Return Book view
- `Ctrl + P`: Open Reports & Analytics view
- `Ctrl + F`: Focus on the search field (in Books or Members views)
- `Ctrl + N`: Open the Add New Book/Member dialog (in their respective views)
- `Esc`: Close open modal dialogs

## Core Operations
- **Add Book:** Go to Books -> Click "+ Add New Book" -> Fill details -> Save.
- **Edit Book:** Go to Books -> Click "Edit" next to any book -> Update fields -> Update Book.
- **Delete Book:** Go to Books -> Click "Delete" (cannot delete while copies are actively issued).
- **Register Member:** Go to Members -> Click "+ Register Member" -> Fill details -> Register.
- **Edit Member:** Go to Members -> Click "Edit" next to any member -> Update fields -> Update Member.
- **Delete Member:** Go to Members -> Click "Delete" (cannot delete member with active or overdue books).
- **Issue Book:** Go to Issue Book -> Enter Book ID, Member ID, and loan period -> Click Issue Book.
- **Return Book:** Go to Return Book -> Enter Transaction ID or click "Return" in the active loan table.
- **Reports:** Go to Reports to view real-time graphical status charts of library operations.
