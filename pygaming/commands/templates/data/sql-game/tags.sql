INSERT INTO tags (phase_name, tag) VALUES
('lobby', 'settings'),
('playground', 'settings')
-- All localizations, sounds, fonts and speeches whose phase_name_or_tag is 'settings' will be loaded at the start of the both phases
-- All localizations, sounds, fonts and speeches whose phase_name_or_tag is 'all' are loaded at the beginning of the game
-- All localizations, sounds, fonts and speeches whose phase_name_or_tag is the name of one of the phase will be loaded at the start of the corresponding phase