-- In this file are created every tables. This sql file is the first executed at game launch.

CREATE TABLE tags ( -- All the tags. Tag are used to group phases together
    phase_name TEXT NOT NULL, -- The name of the phase, as created in the source
    tag TEXT NOT NULL -- A tag to attribute to this phase
); -- You can add as many row as you want. Any localization, speech, sound or font whose phase_name_or_tag is a tag in this table
-- will be loaded in all phases having this tag.

CREATE TABLE localizations (
    position TEXT NOT NULL, --"LOC_..."
    phase_name_or_tag TEXT NOT NULL, -- the name of the phase or a tag. The text is loaded only on the corresponding phase(s) or in every phase if the tag is "all"
    language_code TEXT, --'en_US" for us english, "fr_FR" for french, "it_IT" for italian, "es_MX" for mexican spanish etc.
    text_value TEXT NOT NULL -- The value itself
);

CREATE TABLE speeches (
    position TEXT NOT NULL,
    phase_name_or_tag TEXT NOT NULL,
    language_code TEXT,
    sound_path TEXT NOT NULL
);

CREATE TABLE sounds (
    name TEXT NOT NULL UNIQUE,
    phase_name_or_tag TEXT NOT NULL,
    sound_path TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE fonts (
    name TEXT NOT NULL UNIQUE,
    phase_name_or_tag TEXT NOT NULL,
    font_path TEXT NOT NULL,
    size INTEGER NOT NULL,
    italic BOOLEAN DEFAULT FALSE,
    bold BOOLEAN DEFAULT FALSE,
    underline BOOLEAN DEFAULT FALSE,
    strikethrough BOOLEAN DEFAULT FALSE
)