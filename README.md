# Hobby Meetups

Hobby Meetups is a Flask web application for finding and organizing local
hobby events. Users can create meetup announcements, assign categories, search
the public meetup list, join other users' meetups with a short comment, and
view public profile pages with activity statistics.

The app uses server-rendered HTML, raw parameterized SQL, custom CSS, and no
JavaScript.

## Features

* **User authentication:** Users can register, log in, and log out.
* **Meetup management:** Logged-in users can create, edit, and delete their own
  meetup announcements.
* **Categories:** A meetup can have one or more categories, and category names
  are shown in listings and detail pages.
* **Search and pagination:** The front page supports keyword search by title,
  description, location, or category, and paginates the results.
* **Join events:** Logged-in users can join another user's meetup and leave a
  comment for the organizer.
* **Profiles:** Each user has a public profile with counts for organized
  meetups and joined meetups, plus a list of meetups they created.
* **Security controls:** Forms use CSRF tokens, owner-only actions are checked
  on the server, and passwords are stored as hashes.

## Local Setup

The project includes setup scripts that create a virtual environment, install
Flask, initialize the SQLite database, and start the development server.

For macOS and Linux:

```bash
bash setup.sh
```

For Windows:

```bat
setup.bat
```

After startup, open:

```text
http://127.0.0.1:5000
```

The database is stored at `instance/hobby_meetups.db`. The setup process also
adds demo users and demo meetups. Demo users use the password `demo123`.

## Manual Testing

Use the running local app to check the main workflows:

* Register a new account, log in, and log out.
* Create a meetup with one or more categories.
* Edit and delete a meetup that you own.
* Browse the front page, use pagination, and search with `search_query`.
* Open a meetup detail page and join another user's meetup with a comment.
* Open a user profile and verify organized and joined meetup counts.
* Confirm that non-owners cannot edit or delete another user's meetup.
* Confirm that users cannot join their own meetup or join the same meetup twice.
* Confirm that POST requests without a CSRF token return `403`.

## Large Dataset Testing

`seed.py` is an optional development script for testing the app with a larger
SQLite dataset. It uses only the Python standard library and assumes the schema
already exists.

Default generated data:

* `USER_COUNT = 200`
* `MEETUP_COUNT = 5000`
* `JOIN_EVENT_COUNT = 20000`

Run it against the default local database:

```bash
python seed.py
```

Run it against another SQLite database path:

```bash
python seed.py /path/to/hobby_meetups.db
```

The script is idempotent for its own generated records. It creates users named
`seed_user_0001` and onward, meetups named `Seed Meetup 00001` and onward, and
join events that never join a user to their own meetup. Seed users use the
password `seed123`.

## Performance Report

The following timings were measured locally on April 24, 2026 after running
`python seed.py`. The database contained 208 users, 5006 meetups, and 20011 join
events, including 5000 generated seed meetups and 20000 generated seed join
events.

The app was run with the Flask development server:

```bash
python app.py
```

Each route was measured with 10 warm `curl` requests using this pattern:

```bash
curl -s -o /dev/null -w "%{time_total}\n" "http://127.0.0.1:5000/?page=1"
```

Measured averages:

* `/?page=1`: `0.006049s` average, `0.005398s` min, `0.007112s` max
* `/?page=5`: `0.005768s` average, `0.005224s` min, `0.006512s` max
* `/?search_query=Python&page=2`: `0.005140s` average, `0.004895s` min,
  `0.005443s` max

The schema includes indexes for the listing, owner lookup, and join lookup
patterns used by these pages.
