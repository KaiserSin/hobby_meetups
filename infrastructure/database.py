from pathlib import Path
import sqlite3

from flask import current_app, g

INFRASTRUCTURE_DIR = Path(__file__).resolve().parent


def get_db():
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_sql = _read_sql_file("schema.sql")
    seed_categories_sql = _read_sql_file("seed_categories.sql")
    db.executescript(schema_sql)
    _migrate_meetup_categories(db)
    db.executescript(seed_categories_sql)
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)


def _read_sql_file(filename):
    sql_file_path = INFRASTRUCTURE_DIR / filename
    return sql_file_path.read_text(encoding="utf-8")


def _migrate_meetup_categories(db):
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS meetup_categories (
            meetup_id INTEGER NOT NULL REFERENCES meetups(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            PRIMARY KEY (meetup_id, category_id)
        )
        """
    )
    db.execute(
        """
        INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
        SELECT id, category_id
        FROM meetups
        WHERE category_id IS NOT NULL
        """
    )
