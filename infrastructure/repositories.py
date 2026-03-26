from infrastructure.database import get_db


class UserRepository:
    def save_user(self, username, password_hash):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash),
        )
        db.commit()
        return cursor.lastrowid

    def find_by_username(self, username):
        db = get_db()
        cursor = db.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        return cursor.fetchone()
