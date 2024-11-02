-- In this file are created every tables. This sql file is the first executed at game launch.

CREATE TABLE localizations (
    position TEXT NOT NULL, --"LOC_..."
    phase_name TEXT NOT NULL, -- the name of the phase. The text is loaded only on the corresponding phase or in every phase if the phase name is "all"
    language_code TEXT, --'en_US" for us english, "fr_FR" for french, "it_IT" for italian, "es_MX" for mexican spanish etc.
    text_value TEXT NOT NULL -- The value itself
);

-- Example: see localizations.sql

CREATE TABLE speeches (
    position TEXT NOT, -- "LOC_..."
    phase_name TEXT NOT NULL, -- the name of the phase
    language_code TEXT, --'en_US" for us english, "fr_FR" for french, "it_IT" for italian, "es_MX" for mexican spanish etc.
    sound_path TEXT NOT NULL -- The path to the sound in this language in the folder assets/sounds
);

-- Example: see speeches.sql

CREATE TABLE sounds (
    name TEXT NOT NULL UNIQUE,
    phase_name TEXT NOT NULL,
    sound_path TEXT NOT NULL,
    category TEXT NOT NULL
);

-- Example: see sounds.sql

CREATE TABLE fonts (
    name TEXT NOT NULL UNIQUE,
    phase_name TEXT NOT NULL,
    font_path TEXT NOT NULL,
    size INTEGER NOT NULL,
    italic BOOLEAN DEFAULT FALSE,
    bold BOOLEAN DEFAULT FALSE,
    underline BOOLEAN DEFAULT FALSE
    strikethrough BOOLEAN DEFAULT FALSE,
)

-- Example: see fonts.sql
