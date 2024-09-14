-- In this file are created every tables. This sql file is the first executed at game launch.

CREATE TABLE localizations (
    position TEXT NOT NULL UNIQUE, --"LOC_..."
    language_code TEXT, --'en_US" for us english, "fr_FR" for french, "it_IT" for italian, "es_MX" for mexican spanish etc.
    text_value TEXT NOT NULL -- The value itself
);

CREATE TABLE speeches (
    position TEXT NOT NULL UNIQUE,
    language_code TEXT,
    sound_path TEXT NOT NULL
);
