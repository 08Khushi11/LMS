from database.db_connection import execute_query

class MemberController:
    @staticmethod
    def get_all_members():
        cursor, conn = execute_query("SELECT * FROM members ORDER BY registration_date DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def add_member(full_name, email, phone, address):
        if not full_name:
            raise ValueError("Full name is required.")
        query = """
            INSERT INTO members (full_name, email, phone, address)
            VALUES (?, ?, ?, ?)
        """
        cursor, conn = execute_query(query, (full_name, email, phone, address), commit=True)
        conn.close()

    @staticmethod
    def update_member(member_id, full_name, email, phone, address):
        if not full_name:
            raise ValueError("Full name is required.")
        query = """
            UPDATE members SET
            full_name = ?, email = ?, phone = ?, address = ?
            WHERE member_id = ?
        """
        cursor, conn = execute_query(query, (full_name, email, phone, address, member_id), commit=True)
        conn.close()

    @staticmethod
    def delete_member(member_id):
        cursor, conn = execute_query("SELECT COUNT(*) as count FROM transactions WHERE member_id = ? AND status = 'Issued'", (member_id,))
        count = cursor.fetchone()['count']
        conn.close()
        if count > 0:
            raise ValueError("Cannot delete member with currently issued books.")
        cursor, conn = execute_query("DELETE FROM members WHERE member_id = ?", (member_id,), commit=True)
        conn.close()
