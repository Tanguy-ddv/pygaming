-- In this file are created every tables. This sql file is the first executed at game launch.

CREATE TABLE localizations (
    position TEXT NOT NULL, --"LOC_..."
    language_code TEXT, --'en_US" for us english, "fr_FR" for french, "it_IT" for italian, "es_MX" for mexican spanish etc.
    text_value TEXT NOT NULL -- The value itself
);

CREATE TABLE speeches (
    position TEXT NOT NULL,
    language_code TEXT,
    sound_path TEXT NOT NULL
);

-- Exemple of table to store the users:

CREATE TABLE player(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    victories INTEGER DEFAULT 0
)
