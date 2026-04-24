from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import sqlite3
import sys


USER_COUNT = 200
MEETUP_COUNT = 5000
JOIN_EVENT_COUNT = 20000

DATABASE_PATH = Path(__file__).resolve().parent / "instance" / "hobby_meetups.db"
SEED_PASSWORD = "seed123"
PASSWORD_ITERATIONS = 1_000_000
PASSWORD_SALT = "seeddata"
REQUIRED_TABLES = {
    "categories",
    "join_events",
    "meetup_categories",
    "meetups",
    "users",
}

MEETUP_TOPICS = (
    "Board game night",
    "Morning run",
    "Python study session",
    "Watercolor practice",
    "Open mic rehearsal",
    "Language exchange",
    "Photography walk",
    "Book discussion",
    "Cycling route",
    "Cooking workshop",
)

LOCATIONS = (
    "Central Library",
    "Community Hall",
    "University Cafe",
    "Harbor Park",
    "Arts Centre",
    "Startup Hub",
    "Sports Field",
    "Music Studio",
)

JOIN_COMMENTS = (
    "I am joining this meetup.",
    "Looking forward to meeting everyone.",
    "I can bring some materials.",
    "This fits my schedule well.",
    "Happy to help with setup.",
)


def main():
    database_path = _get_database_path()
    with _connect_database(database_path) as connection:
        _validate_database(connection)
        categories = _fetch_categories(connection)
        users = _seed_users(connection)
        meetups = _seed_meetups(connection, users, categories)
        _seed_join_events(connection, users, meetups)
        connection.commit()
        _print_summary(connection, database_path)


def _get_database_path():
    if len(sys.argv) > 2:
        raise SystemExit("Usage: python seed.py [database_path]")

    if len(sys.argv) == 2:
        return Path(sys.argv[1]).expanduser().resolve()

    return DATABASE_PATH


def _connect_database(database_path):
    if not database_path.exists():
        raise SystemExit(
            f"Database not found at {database_path}. Initialize the app database first."
        )

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _validate_database(connection):
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()
    table_names = {row["name"] for row in rows}
    missing_tables = sorted(REQUIRED_TABLES - table_names)

    if missing_tables:
        missing_table_list = ", ".join(missing_tables)
        raise SystemExit(f"Missing tables: {missing_table_list}. Initialize the app first.")


def _fetch_categories(connection):
    categories = connection.execute(
        """
        SELECT id, name
        FROM categories
        ORDER BY id
        """
    ).fetchall()

    if not categories:
        raise SystemExit("No categories found. Initialize the app database first.")

    return categories


def _seed_users(connection):
    password_hash = _generate_password_hash(SEED_PASSWORD)
    user_rows = [
        (_user_name(user_number), password_hash)
        for user_number in range(1, USER_COUNT + 1)
    ]
    connection.executemany(
        """
        INSERT OR IGNORE INTO users (username, password_hash)
        VALUES (?, ?)
        """,
        user_rows,
    )

    users = _fetch_seed_users(connection)
    if len(users) != USER_COUNT:
        raise SystemExit("Could not create or load the expected seed users.")

    return users


def _generate_password_hash(password):
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        PASSWORD_SALT.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2:sha256:{PASSWORD_ITERATIONS}${PASSWORD_SALT}${password_hash}"


def _fetch_seed_users(connection):
    expected_usernames = {_user_name(user_number) for user_number in range(1, USER_COUNT + 1)}
    rows = connection.execute(
        """
        SELECT id, username
        FROM users
        WHERE username LIKE 'seed_user_%'
        ORDER BY username
        """
    ).fetchall()
    return [row for row in rows if row["username"] in expected_usernames]


def _seed_meetups(connection, users, categories):
    existing_meetups = _fetch_seed_meetups(connection)
    meetup_rows = []
    first_event_time = datetime.now().replace(minute=0, second=0, microsecond=0)

    for meetup_number in range(1, MEETUP_COUNT + 1):
        title = _meetup_title(meetup_number)
        if title in existing_meetups:
            continue

        owner = users[(meetup_number - 1) % len(users)]
        category = categories[(meetup_number - 1) % len(categories)]
        event_time = first_event_time + timedelta(hours=meetup_number)
        topic = MEETUP_TOPICS[(meetup_number - 1) % len(MEETUP_TOPICS)]
        location = LOCATIONS[(meetup_number - 1) % len(LOCATIONS)]
        description = (
            f"{topic} generated for large dataset testing.\n"
            "This entry helps verify pagination and search performance."
        )
        meetup_rows.append(
            (
                owner["id"],
                category["id"],
                title,
                description,
                event_time.strftime("%Y-%m-%d %H:%M:%S"),
                f"{location}, room {(meetup_number % 30) + 1}",
            )
        )

    connection.executemany(
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
        meetup_rows,
    )

    meetups = _fetch_seed_meetups(connection)
    if len(meetups) != MEETUP_COUNT:
        raise SystemExit("Could not create or load the expected seed meetups.")

    _seed_meetup_categories(connection, meetups, categories)
    return meetups


def _fetch_seed_meetups(connection):
    expected_titles = {
        _meetup_title(meetup_number)
        for meetup_number in range(1, MEETUP_COUNT + 1)
    }
    rows = connection.execute(
        """
        SELECT id, title, user_id
        FROM meetups
        WHERE title LIKE 'Seed Meetup %'
        ORDER BY title
        """
    ).fetchall()
    return {row["title"]: row for row in rows if row["title"] in expected_titles}


def _seed_meetup_categories(connection, meetups, categories):
    category_rows = []
    for meetup_number in range(1, MEETUP_COUNT + 1):
        meetup = meetups[_meetup_title(meetup_number)]
        for category_id in _category_ids_for_meetup(meetup_number, categories):
            category_rows.append((meetup["id"], category_id))

    connection.executemany(
        """
        INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
        VALUES (?, ?)
        """,
        category_rows,
    )


def _category_ids_for_meetup(meetup_number, categories):
    primary_category = categories[(meetup_number - 1) % len(categories)]
    category_ids = [primary_category["id"]]

    if len(categories) > 1 and meetup_number % 4 == 0:
        secondary_category = categories[meetup_number % len(categories)]
        if secondary_category["id"] not in category_ids:
            category_ids.append(secondary_category["id"])

    return category_ids


def _seed_join_events(connection, users, meetups):
    maximum_join_events = MEETUP_COUNT * (USER_COUNT - 1)
    if JOIN_EVENT_COUNT > maximum_join_events:
        raise SystemExit("JOIN_EVENT_COUNT is higher than the available unique pairs.")

    existing_pairs = _fetch_existing_join_pairs(connection)
    user_index_by_id = {user["id"]: index for index, user in enumerate(users)}
    join_rows = []

    for join_number in range(JOIN_EVENT_COUNT):
        meetup_number = (join_number % MEETUP_COUNT) + 1
        meetup = meetups[_meetup_title(meetup_number)]
        owner_index = user_index_by_id[meetup["user_id"]]
        participant_index = (owner_index + (join_number // MEETUP_COUNT) + 1) % USER_COUNT
        participant = users[participant_index]
        pair = (meetup["id"], participant["id"])

        if meetup["user_id"] == participant["id"]:
            raise SystemExit("Seed data attempted to join a user to their own meetup.")

        if pair in existing_pairs:
            continue

        comment = JOIN_COMMENTS[join_number % len(JOIN_COMMENTS)]
        join_rows.append((meetup["id"], participant["id"], comment))

    connection.executemany(
        """
        INSERT INTO join_events (meetup_id, user_id, comment)
        VALUES (?, ?, ?)
        """,
        join_rows,
    )


def _fetch_existing_join_pairs(connection):
    rows = connection.execute(
        """
        SELECT join_events.meetup_id, join_events.user_id
        FROM join_events
        JOIN meetups ON meetups.id = join_events.meetup_id
        WHERE meetups.title LIKE 'Seed Meetup %'
        """
    ).fetchall()
    return {(row["meetup_id"], row["user_id"]) for row in rows}


def _print_summary(connection, database_path):
    seed_user_count = _count_rows(
        connection,
        """
        SELECT COUNT(*) AS row_count
        FROM users
        WHERE username LIKE 'seed_user_%'
        """,
    )
    seed_meetup_count = _count_rows(
        connection,
        """
        SELECT COUNT(*) AS row_count
        FROM meetups
        WHERE title LIKE 'Seed Meetup %'
        """,
    )
    seed_join_event_count = _count_rows(
        connection,
        """
        SELECT COUNT(*) AS row_count
        FROM join_events
        JOIN meetups ON meetups.id = join_events.meetup_id
        WHERE meetups.title LIKE 'Seed Meetup %'
        """,
    )

    print(f"Seeded database: {database_path}")
    print(f"Seed users: {seed_user_count}")
    print(f"Seed meetups: {seed_meetup_count}")
    print(f"Seed join events: {seed_join_event_count}")


def _count_rows(connection, query):
    return connection.execute(query).fetchone()["row_count"]


def _user_name(user_number):
    return f"seed_user_{user_number:04d}"


def _meetup_title(meetup_number):
    return f"Seed Meetup {meetup_number:05d}"


if __name__ == "__main__":
    main()
