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
