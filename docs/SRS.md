# Software Requirements Specification (SRS)
## Library Management System (TQM - Q14)

### 1. Introduction
The Library Management System is a desktop application designed to manage books, members, and transactions. This project emphasizes TQM Q14: Improve Navigation, ensuring a seamless user experience.

### 2. Functional Requirements
- **FR1:** The system shall allow users to add, view, update, and delete books.
- **FR2:** The system shall allow users to register, view, update, and delete members.
- **FR3:** The system shall manage the issuing and returning of books, updating available stock automatically.
- **FR4:** The system shall provide a dashboard with real-time statistics.
- **FR5:** The system shall generate basic charts reflecting library status.

### 3. Non-Functional Requirements (TQM Q14)
- **NFR1 (Breadcrumbs):** Every view shall display its navigation hierarchy.
- **NFR2 (Global Navigation):** A persistent sidebar shall be available across all screens.
- **NFR3 (Shortcuts):** Keyboard shortcuts (Ctrl+D, Ctrl+B, etc.) must trigger view changes.
- **NFR4 (Dashboard Tiles):** Clickable dashboard statistics shall route users to related views.
- **NFR5 (Home Button):** Users shall have access to a Home/Dashboard button from any screen.

### 4. System Architecture
- **Language:** Python 3
- **GUI Framework:** CustomTkinter
- **Database:** SQLite3
- **Design Pattern:** MVC (Model-View-Controller)
