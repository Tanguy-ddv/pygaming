-- Example of table to store the users:

CREATE TABLE player(
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    victories INTEGER DEFAULT 0
);

-- Example of table to store the playable characters:

CREATE TABLE character(
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    weight REAL,
    height REAL,
    color1 TEXT,
    color2 TEXT,
    locked BOOLEAN
);

-- Example of table to store levels.

CREATE TABLE levels(
    level_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_path TEXT NOT NULL,
    length INTEGER,
    difficulty INTEGER
)