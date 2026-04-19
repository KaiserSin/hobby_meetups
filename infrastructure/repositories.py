from domain.entities import Category, Meetup, User
from infrastructure.database import get_db


USER_SELECT_SQL = """
    SELECT id, username, password_hash
    FROM users
"""

MEETUP_SELECT_SQL = """
    SELECT
        meetups.id,
        meetups.user_id,
        meetups.title,
        meetups.description,
        meetups.event_time,
        meetups.location,
        GROUP_CONCAT(categories.id) AS category_ids,
        GROUP_CONCAT(categories.name, ', ') AS category_name,
        users.username
    FROM meetups
    LEFT JOIN users ON users.id = meetups.user_id
    LEFT JOIN meetup_categories ON meetup_categories.meetup_id = meetups.id
    LEFT JOIN categories ON categories.id = meetup_categories.category_id
"""

MEETUP_GROUP_BY_SQL = "\nGROUP BY meetups.id"


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
        return self._get_user("WHERE username = ?", (username,))

    def get_user_by_id(self, user_id):
        return self._get_user("WHERE id = ?", (user_id,))

    def _get_user(self, where_clause, params):
        cursor = get_db().execute(f"{USER_SELECT_SQL}\n{where_clause}", params)
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
        query = MEETUP_SELECT_SQL
        params = ()
        clean_search_query = (search_query or "").strip()
        if clean_search_query:
            like_query = f"%{clean_search_query}%"
            query += """
                WHERE
                    meetups.title LIKE ?
                    OR meetups.description LIKE ?
                    OR meetups.location LIKE ?
                    OR categories.name LIKE ?
            """
            params = (like_query, like_query, like_query, like_query)

        query += f"{MEETUP_GROUP_BY_SQL}\nORDER BY meetups.event_time"
        return self._list_meetups(query, params)

    def list_meetups_by_user(self, user_id):
        query = f"{MEETUP_SELECT_SQL}\nWHERE meetups.user_id = ?{MEETUP_GROUP_BY_SQL}\nORDER BY meetups.event_time"
        return self._list_meetups(query, (user_id,))

    def list_join_events_for_meetup(self, meetup_id):
        cursor = get_db().execute(
            """
            SELECT join_events.user_id, users.username, join_events.comment
            FROM join_events
            JOIN users ON users.id = join_events.user_id
            WHERE join_events.meetup_id = ?
            ORDER BY join_events.created_at, join_events.id
            """,
            (meetup_id,),
        )
        return [
            {
                "user_id": row["user_id"],
                "username": row["username"],
                "comment": row["comment"],
            }
            for row in cursor.fetchall()
        ]

    def get_meetup_by_id(self, meetup_id):
        cursor = get_db().execute(
            f"{MEETUP_SELECT_SQL}\nWHERE meetups.id = ?{MEETUP_GROUP_BY_SQL}",
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

    def create_meetup(self, user_id, category_ids, title, description, event_time, location):
        db = get_db()
        primary_category_id = category_ids[0]
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
            (user_id, primary_category_id, title, description, event_time, location),
        )
        self._replace_meetup_categories(db, cursor.lastrowid, category_ids)
        db.commit()
        return cursor.lastrowid

    def update_meetup(
        self,
        meetup_id,
        user_id,
        category_ids,
        title,
        description,
        event_time,
        location,
    ):
        db = get_db()
        primary_category_id = category_ids[0]
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
                primary_category_id,
                title,
                description,
                event_time,
                location,
                meetup_id,
                user_id,
            ),
        )
        if cursor.rowcount > 0:
            self._replace_meetup_categories(db, meetup_id, category_ids)
        db.commit()
        return cursor.rowcount

    def delete_meetup(self, meetup_id, user_id):
        db = get_db()
        db.execute(
            """
            DELETE FROM meetup_categories
            WHERE meetup_id = ?
            """,
            (meetup_id,),
        )
        db.execute(
            """
            DELETE FROM join_events
            WHERE meetup_id = ?
            """,
            (meetup_id,),
        )
        cursor = db.execute(
            """
            DELETE FROM meetups
            WHERE id = ? AND user_id = ?
            """,
            (meetup_id, user_id),
        )
        db.commit()
        return cursor.rowcount

    def get_user_profile_stats(self, user_id):
        cursor = get_db().execute(
            """
            SELECT
                (SELECT COUNT(*) FROM meetups WHERE user_id = ?) AS organized_count,
                (
                    SELECT COUNT(DISTINCT join_events.meetup_id)
                    FROM join_events
                    JOIN meetups ON meetups.id = join_events.meetup_id
                    WHERE join_events.user_id = ? AND meetups.user_id != ?
                ) AS joined_count
            """,
            (user_id, user_id, user_id),
        )
        row = cursor.fetchone()
        return row["organized_count"], row["joined_count"]

    def has_user_joined_meetup(self, meetup_id, user_id):
        cursor = get_db().execute(
            """
            SELECT 1
            FROM join_events
            WHERE meetup_id = ? AND user_id = ?
            """,
            (meetup_id, user_id),
        )
        return cursor.fetchone() is not None

    def create_join_event(self, meetup_id, user_id, comment):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO join_events (meetup_id, user_id, comment)
            VALUES (?, ?, ?)
            """,
            (meetup_id, user_id, comment),
        )
        db.commit()
        return cursor.lastrowid

    def _list_meetups(self, query, params):
        cursor = get_db().execute(query, params)
        return [self._map_meetup(row) for row in cursor.fetchall()]

    def _replace_meetup_categories(self, db, meetup_id, category_ids):
        db.execute(
            """
            DELETE FROM meetup_categories
            WHERE meetup_id = ?
            """,
            (meetup_id,),
        )
        db.executemany(
            """
            INSERT INTO meetup_categories (meetup_id, category_id)
            VALUES (?, ?)
            """,
            [(meetup_id, category_id) for category_id in category_ids],
        )

    def _map_category(self, row):
        return Category(
            id=row["id"],
            name=row["name"],
        )

    def _map_meetup(self, row):
        category_ids = self._parse_category_ids(row["category_ids"])
        return Meetup(
            id=row["id"],
            user_id=row["user_id"],
            category_id=category_ids[0] if category_ids else None,
            title=row["title"],
            description=row["description"],
            event_time=row["event_time"],
            location=row["location"],
            category_name=row["category_name"],
            username=row["username"],
            category_ids=category_ids,
        )

    def _parse_category_ids(self, raw_category_ids):
        if not raw_category_ids:
            return ()
        return tuple(int(category_id) for category_id in raw_category_ids.split(",") if category_id)
