# Test Cases

## UI & Navigation Tests
| Test ID | Test Case | Expected Result |
|---|---|---|
| TC-01 | Click "Dashboard" in sidebar | Dashboard view loads, sidebar button highlighted |
| TC-02 | Click "Books" breadcrumb from "Add Book" | Navigates back to Books View |
| TC-03 | Press `Ctrl + M` | Members view loads |
| TC-04 | Press `Ctrl + F` in Books View | Search bar gains focus |
| TC-05 | Click "Total Books" tile on Dashboard | Navigates to Books View |

## Core Logic Tests
| Test ID | Test Case | Expected Result |
|---|---|---|
| TC-06 | Add a Book | Book appears in DB and UI list |
| TC-07 | Register a Member | Member appears in DB and UI list |
| TC-08 | Issue a Book with 0 available copies | Displays error: "No available copies" |
| TC-09 | Return an issued book | Book copies increase by 1 |
| TC-10 | Issue a book already issued to the same member | Displays error: "Member already has a copy" |
| TC-11 | Update an existing book's details | Book updates in database and table reflects new values |
| TC-12 | Update an existing member's details | Member information updates in database and UI |
| TC-13 | Attempt to delete book with issued copies | Displays error: "Cannot delete book while copies are currently issued" |
| TC-14 | Attempt to delete member with active loans | Displays error: "Cannot delete member with currently issued or overdue books" |
| TC-15 | Overdue book detection and return | Active loan marked as Overdue, and can be returned cleanly |
