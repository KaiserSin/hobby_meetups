CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meetups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    event_time TIMESTAMP NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS join_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meetup_id INTEGER REFERENCES meetups(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meetup_categories (
    meetup_id INTEGER NOT NULL REFERENCES meetups(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    PRIMARY KEY (meetup_id, category_id)
);

CREATE INDEX IF NOT EXISTS idx_meetups_event_time
ON meetups(event_time, id);

CREATE INDEX IF NOT EXISTS idx_meetups_user_id
ON meetups(user_id);

CREATE INDEX IF NOT EXISTS idx_join_events_meetup_user_id
ON join_events(meetup_id, user_id);
