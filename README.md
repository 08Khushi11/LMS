# Library Management System
## Developed for Fundamentals of Total Quality Management (TQM) - Q14: Improve Navigation

A robust, modern desktop Library Management System built with Python, CustomTkinter, and SQLite.

### Features
- **Book Management:** Add, edit, search, and delete books with stock tracking.
- **Member Registration:** Register, edit, and manage library members with loan safeguards.
- **Transactions:** Issue and return books with automated stock adjustment and overdue tracking.
- **Dashboard & Analytics:** Real-time statistics tiles and embedded Matplotlib visual analytics.
- **Q14 Navigation Features:**
  1. Breadcrumbs for contextual navigation.
  2. Persistent Sidebar Navigation with active-state highlighting.
  3. Global Keyboard Shortcuts (`Ctrl+D`, `Ctrl+B`, `Ctrl+M`, `Ctrl+I`, `Ctrl+R`, `Ctrl+P`, `Ctrl+F`, `Ctrl+N`, `Esc`).
  4. Interactive Dashboard Quick Action and Stat Tiles.
  5. One-click Home navigation from anywhere in the application.

### How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```
   (The database will be automatically initialized on first run.)

### Testing
Run the test suite using pytest:
```bash
python -m pytest tests/
```

