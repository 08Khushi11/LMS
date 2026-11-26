import re
from database.db_connection import fetch_all, fetch_one, execute_write

class MemberController:
    @staticmethod
    def get_all_members():
        query = """
            SELECT m.*, 
                   COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
            FROM members m
            LEFT JOIN transactions t ON m.member_id = t.member_id
            GROUP BY m.member_id
            ORDER BY m.registration_date DESC
        """
        return fetch_all(query)

    @staticmethod
    def get_member_by_id(member_id):
        try:
            mid = int(member_id)
        except (ValueError, TypeError):
            return None
        query = """
            SELECT m.*, 
                   COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
            FROM members m
            LEFT JOIN transactions t ON m.member_id = t.member_id
            WHERE m.member_id = ?
            GROUP BY m.member_id
        """
        return fetch_one(query, (mid,))

    @staticmethod
    def get_member_by_name(full_name):
        clean = str(full_name).strip()
        if not clean:
            return None
        query = """
            SELECT m.*, 
                   COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
            FROM members m
            LEFT JOIN transactions t ON m.member_id = t.member_id
            WHERE LOWER(m.full_name) = LOWER(?)
            GROUP BY m.member_id
            LIMIT 1
        """
        member = fetch_one(query, (clean,))
        if not member:
            # Partial match
            query_partial = """
                SELECT m.*, 
                       COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
                FROM members m
                LEFT JOIN transactions t ON m.member_id = t.member_id
                WHERE m.full_name LIKE ?
                GROUP BY m.member_id
                LIMIT 1
            """
            member = fetch_one(query_partial, (f"%{clean}%",))
        return member

    @staticmethod
    def search_members_autocomplete(query_text, limit=15):
        clean = str(query_text).strip()
        if not clean:
            query = """
                SELECT m.*, 
                       COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
                FROM members m
                LEFT JOIN transactions t ON m.member_id = t.member_id
                GROUP BY m.member_id
                ORDER BY m.full_name ASC
                LIMIT ?
            """
            return fetch_all(query, (limit,))
        else:
            like = f"%{clean}%"
            try:
                mid = int(clean)
            except ValueError:
                mid = -1
            query = """
                SELECT m.*, 
                       COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
                FROM members m
                LEFT JOIN transactions t ON m.member_id = t.member_id
                WHERE m.full_name LIKE ? OR m.email LIKE ? OR m.phone LIKE ? OR m.member_id = ?
                GROUP BY m.member_id
                ORDER BY 
                    CASE WHEN LOWER(m.full_name) LIKE LOWER(?) THEN 1 ELSE 2 END,
                    m.full_name ASC
                LIMIT ?
            """
            return fetch_all(query, (like, like, like, mid, f"{clean}%", limit))

    @staticmethod
    def add_member(full_name, email="", phone="", address=""):
        full_name = str(full_name).strip() if full_name else ""
        email = str(email).strip() if email else ""
        phone = str(phone).strip() if phone else ""
        address = str(address).strip() if address else ""

        if not full_name:
            raise ValueError("Full name is required.")

        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("Invalid email format.")

        query = """
            INSERT INTO members (full_name, email, phone, address)
            VALUES (?, ?, ?, ?)
        """
        return execute_write(query, (full_name, email, phone, address))

    @staticmethod
    def update_member(member_id, full_name, email="", phone="", address=""):
        full_name = str(full_name).strip() if full_name else ""
        email = str(email).strip() if email else ""
        phone = str(phone).strip() if phone else ""
        address = str(address).strip() if address else ""

        if not full_name:
            raise ValueError("Full name is required.")

        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("Invalid email format.")

        row = fetch_one("SELECT member_id FROM members WHERE member_id = ?", (member_id,))
        if not row:
            raise ValueError("Member not found.")

        query = """
            UPDATE members SET
            full_name = ?, email = ?, phone = ?, address = ?
            WHERE member_id = ?
        """
        execute_write(query, (full_name, email, phone, address, member_id))

    @staticmethod
    def search_members(query_text):
        clean_text = str(query_text).strip()
        like_text = f"%{clean_text}%"
        try:
            member_id_val = int(clean_text)
        except ValueError:
            member_id_val = -1

        query = """
            SELECT m.*, 
                   COUNT(CASE WHEN t.status IN ('Issued', 'Overdue') THEN 1 END) as active_loans
            FROM members m
            LEFT JOIN transactions t ON m.member_id = t.member_id
            WHERE m.full_name LIKE ? OR m.email LIKE ? OR m.phone LIKE ? OR m.member_id = ?
            GROUP BY m.member_id
            ORDER BY m.registration_date DESC
        """
        return fetch_all(query, (like_text, like_text, like_text, member_id_val))

    @staticmethod
    def delete_member(member_id):
        row = fetch_one("SELECT member_id FROM members WHERE member_id = ?", (member_id,))
        if not row:
            raise ValueError("Member not found.")

        active = fetch_one(
            "SELECT COUNT(*) as count FROM transactions WHERE member_id = ? AND status IN ('Issued', 'Overdue')",
            (member_id,)
        )
        if active and active['count'] > 0:
            raise ValueError("Cannot delete member with currently issued or overdue books.")

        execute_write("DELETE FROM members WHERE member_id = ?", (member_id,))
