from domain.entities import Category, Meetup, User
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
        row = cursor.fetchone()
        if row is None:
            return None
        return self._map_user(row)

    def get_user_by_id(self, user_id):
        db = get_db()
        cursor = db.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._map_user(row)

    def _map_user(self, row):
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
        )


class MeetupRepository:
    def list_meetups(self, search_query=None):
        db = get_db()
        base_query = """
            SELECT
                meetups.id,
                meetups.user_id,
                meetups.category_id,
                meetups.title,
                meetups.description,
                meetups.event_time,
                meetups.location,
                categories.name AS category_name,
                users.username
            FROM meetups
            LEFT JOIN categories ON categories.id = meetups.category_id
            LEFT JOIN users ON users.id = meetups.user_id
        """

        clean_search_query = (search_query or "").strip()
        if clean_search_query:
            like_query = f"%{clean_search_query}%"
            cursor = db.execute(
                base_query
                + """
                WHERE
                    meetups.title LIKE ?
                    OR meetups.description LIKE ?
                    OR meetups.location LIKE ?
                ORDER BY meetups.event_time
                """,
                (like_query, like_query, like_query),
            )
            return [self._map_meetup(row) for row in cursor.fetchall()]

        cursor = db.execute(
            base_query
            + """
            ORDER BY meetups.event_time
            """
        )
        return [self._map_meetup(row) for row in cursor.fetchall()]

    def get_meetup_by_id(self, meetup_id):
        db = get_db()
        cursor = db.execute(
            """
            SELECT
                meetups.id,
                meetups.user_id,
                meetups.category_id,
                meetups.title,
                meetups.description,
                meetups.event_time,
                meetups.location,
                categories.name AS category_name,
                users.username
            FROM meetups
            LEFT JOIN categories ON categories.id = meetups.category_id
            LEFT JOIN users ON users.id = meetups.user_id
            WHERE meetups.id = ?
            """,
            (meetup_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._map_meetup(row)

    def list_categories(self):
        db = get_db()
        cursor = db.execute(
            """
            SELECT id, name
            FROM categories
            ORDER BY name
            """
        )
        return [self._map_category(row) for row in cursor.fetchall()]

    def create_meetup(self, user_id, category_id, title, description, event_time, location):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO meetups (
                user_id,
                category_id,
                title,
                description,
                event_time,
                location
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, category_id, title, description, event_time, location),
        )
        db.commit()
        return cursor.lastrowid

    def update_meetup(
        self,
        meetup_id,
        user_id,
        category_id,
        title,
        description,
        event_time,
        location,
    ):
        db = get_db()
        cursor = db.execute(
            """
            UPDATE meetups
            SET
                category_id = ?,
                title = ?,
                description = ?,
                event_time = ?,
                location = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                category_id,
                title,
                description,
                event_time,
                location,
                meetup_id,
                user_id,
            ),
        )
        db.commit()
        return cursor.rowcount

    def delete_meetup(self, meetup_id, user_id):
        db = get_db()
        cursor = db.execute(
            """
            DELETE FROM meetups
            WHERE id = ? AND user_id = ?
            """,
            (meetup_id, user_id),
        )
        db.commit()
        return cursor.rowcount

    def _map_category(self, row):
        return Category(
            id=row["id"],
            name=row["name"],
        )

    def _map_meetup(self, row):
        return Meetup(
            id=row["id"],
            user_id=row["user_id"],
            category_id=row["category_id"],
            title=row["title"],
            description=row["description"],
            event_time=row["event_time"],
            location=row["location"],
            category_name=row["category_name"],
            username=row["username"],
        )
