INSERT OR IGNORE INTO users (username, password_hash)
VALUES (
    'demo_alina',
    'pbkdf2:sha256:1000000$y5LQ8l5AhWBIPKNi$ef0d64b99200d82ecc7df955ef1976bdaff6b3416cdc728d5a2e1f160e7f3902'
);

INSERT OR IGNORE INTO users (username, password_hash)
VALUES (
    'demo_boris',
    'pbkdf2:sha256:1000000$y5LQ8l5AhWBIPKNi$ef0d64b99200d82ecc7df955ef1976bdaff6b3416cdc728d5a2e1f160e7f3902'
);

INSERT OR IGNORE INTO users (username, password_hash)
VALUES (
    'demo_chris',
    'pbkdf2:sha256:1000000$y5LQ8l5AhWBIPKNi$ef0d64b99200d82ecc7df955ef1976bdaff6b3416cdc728d5a2e1f160e7f3902'
);

INSERT OR IGNORE INTO users (username, password_hash)
VALUES (
    'demo_daria',
    'pbkdf2:sha256:1000000$y5LQ8l5AhWBIPKNi$ef0d64b99200d82ecc7df955ef1976bdaff6b3416cdc728d5a2e1f160e7f3902'
);

INSERT OR IGNORE INTO users (username, password_hash)
VALUES (
    'demo_ella',
    'pbkdf2:sha256:1000000$y5LQ8l5AhWBIPKNi$ef0d64b99200d82ecc7df955ef1976bdaff6b3416cdc728d5a2e1f160e7f3902'
);

INSERT INTO meetups (
    user_id,
    category_id,
    title,
    description,
    event_time,
    location
)
SELECT
    users.id,
    categories.id,
    'Board Game Night',
    'Casual board games with a mix of quick party games and longer strategy tables.',
    datetime('now', '+7 days'),
    'Central Library, Helsinki'
FROM users
JOIN categories ON categories.name = 'Board Games'
WHERE users.username = 'demo_alina'
    AND NOT EXISTS (
        SELECT 1
        FROM meetups
        JOIN users AS organizers ON organizers.id = meetups.user_id
        WHERE meetups.title = 'Board Game Night'
            AND organizers.username = 'demo_alina'
    );

INSERT INTO meetups (
    user_id,
    category_id,
    title,
    description,
    event_time,
    location
)
SELECT
    users.id,
    categories.id,
    'Weekend Running Group',
    'A relaxed five kilometer run followed by coffee for anyone who wants to stay.',
    datetime('now', '+9 days'),
    'Toolonlahti Park, Helsinki'
FROM users
JOIN categories ON categories.name = 'Sports & Fitness'
WHERE users.username = 'demo_boris'
    AND NOT EXISTS (
        SELECT 1
        FROM meetups
        JOIN users AS organizers ON organizers.id = meetups.user_id
        WHERE meetups.title = 'Weekend Running Group'
            AND organizers.username = 'demo_boris'
    );

INSERT INTO meetups (
    user_id,
    category_id,
    title,
    description,
    event_time,
    location
)
SELECT
    users.id,
    categories.id,
    'Python Study Circle',
    'Bring a small Python project or tutorial and work through it together with others.',
    datetime('now', '+12 days'),
    'Maria 01, Helsinki'
FROM users
JOIN categories ON categories.name = 'Tech & Coding'
WHERE users.username = 'demo_chris'
    AND NOT EXISTS (
        SELECT 1
        FROM meetups
        JOIN users AS organizers ON organizers.id = meetups.user_id
        WHERE meetups.title = 'Python Study Circle'
            AND organizers.username = 'demo_chris'
    );

INSERT INTO meetups (
    user_id,
    category_id,
    title,
    description,
    event_time,
    location
)
SELECT
    users.id,
    categories.id,
    'Watercolor Workshop',
    'A beginner-friendly evening for sketching simple city scenes with watercolors.',
    datetime('now', '+15 days'),
    'Annantalo Arts Centre, Helsinki'
FROM users
JOIN categories ON categories.name = 'Arts & Crafts'
WHERE users.username = 'demo_daria'
    AND NOT EXISTS (
        SELECT 1
        FROM meetups
        JOIN users AS organizers ON organizers.id = meetups.user_id
        WHERE meetups.title = 'Watercolor Workshop'
            AND organizers.username = 'demo_daria'
    );

INSERT INTO meetups (
    user_id,
    category_id,
    title,
    description,
    event_time,
    location
)
SELECT
    users.id,
    categories.id,
    'Open Mic Practice',
    'A low-pressure practice session for songs, short sets, poetry, or spoken word.',
    datetime('now', '+18 days'),
    'Kallio Community Room, Helsinki'
FROM users
JOIN categories ON categories.name = 'Music & Entertainment'
WHERE users.username = 'demo_ella'
    AND NOT EXISTS (
        SELECT 1
        FROM meetups
        JOIN users AS organizers ON organizers.id = meetups.user_id
        WHERE meetups.title = 'Open Mic Practice'
            AND organizers.username = 'demo_ella'
    );

INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
SELECT meetups.id, categories.id
FROM meetups
JOIN users ON users.id = meetups.user_id
JOIN categories ON categories.name = 'Board Games'
WHERE meetups.title = 'Board Game Night'
    AND users.username = 'demo_alina';

INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
SELECT meetups.id, categories.id
FROM meetups
JOIN users ON users.id = meetups.user_id
JOIN categories ON categories.name = 'Sports & Fitness'
WHERE meetups.title = 'Weekend Running Group'
    AND users.username = 'demo_boris';

INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
SELECT meetups.id, categories.id
FROM meetups
JOIN users ON users.id = meetups.user_id
JOIN categories ON categories.name = 'Tech & Coding'
WHERE meetups.title = 'Python Study Circle'
    AND users.username = 'demo_chris';

INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
SELECT meetups.id, categories.id
FROM meetups
JOIN users ON users.id = meetups.user_id
JOIN categories ON categories.name = 'Arts & Crafts'
WHERE meetups.title = 'Watercolor Workshop'
    AND users.username = 'demo_daria';

INSERT OR IGNORE INTO meetup_categories (meetup_id, category_id)
SELECT meetups.id, categories.id
FROM meetups
JOIN users ON users.id = meetups.user_id
JOIN categories ON categories.name = 'Music & Entertainment'
WHERE meetups.title = 'Open Mic Practice'
    AND users.username = 'demo_ella';

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I can bring a couple of card games.'
FROM meetups
JOIN users ON users.username = 'demo_boris'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Board Game Night'
    AND organizers.username = 'demo_alina'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'Happy to teach a quick game to new players.'
FROM meetups
JOIN users ON users.username = 'demo_chris'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Board Game Night'
    AND organizers.username = 'demo_alina'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'Joining for the run and coffee after.'
FROM meetups
JOIN users ON users.username = 'demo_alina'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Weekend Running Group'
    AND organizers.username = 'demo_boris'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I will keep an easy pace.'
FROM meetups
JOIN users ON users.username = 'demo_daria'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Weekend Running Group'
    AND organizers.username = 'demo_boris'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I want to practice Flask basics.'
FROM meetups
JOIN users ON users.username = 'demo_ella'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Python Study Circle'
    AND organizers.username = 'demo_chris'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I can help review small scripts.'
FROM meetups
JOIN users ON users.username = 'demo_alina'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Python Study Circle'
    AND organizers.username = 'demo_chris'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I will bring extra brushes.'
FROM meetups
JOIN users ON users.username = 'demo_boris'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Watercolor Workshop'
    AND organizers.username = 'demo_daria'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'Looking forward to trying watercolor.'
FROM meetups
JOIN users ON users.username = 'demo_ella'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Watercolor Workshop'
    AND organizers.username = 'demo_daria'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I can test a short acoustic set.'
FROM meetups
JOIN users ON users.username = 'demo_chris'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Open Mic Practice'
    AND organizers.username = 'demo_ella'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );

INSERT INTO join_events (meetup_id, user_id, comment)
SELECT meetups.id, users.id, 'I might read a short poem.'
FROM meetups
JOIN users ON users.username = 'demo_daria'
JOIN users AS organizers ON organizers.id = meetups.user_id
WHERE meetups.title = 'Open Mic Practice'
    AND organizers.username = 'demo_ella'
    AND NOT EXISTS (
        SELECT 1
        FROM join_events
        WHERE join_events.meetup_id = meetups.id
            AND join_events.user_id = users.id
    );
