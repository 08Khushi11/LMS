import re
from database.db_connection import fetch_all, fetch_one, execute_write

class MemberController:
    @staticmethod
    def get_all_members():
        return fetch_all("SELECT * FROM members ORDER BY registration_date DESC")

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
        query = """
            SELECT * FROM members 
            WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR member_id = ?
            ORDER BY registration_date DESC
        """
        clean_text = str(query_text).strip()
        like_text = f"%{clean_text}%"
        try:
            member_id_val = int(clean_text)
        except ValueError:
            member_id_val = -1

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

