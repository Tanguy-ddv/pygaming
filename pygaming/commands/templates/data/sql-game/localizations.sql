INSERT INTO localizations (position, phase_name_or_tag, language_code, text_value) VALUES 
('LOC_SELECT_COLOR', 'lobby', 'en_US', 'SELECT A COLOR'),
('LOC_SELECT_COLOR', 'lobby', 'fr_FR', 'SELECTIONNER UNE COULEUR'),
('LOC_SELECT_NAME' , 'lobby', 'en_US', 'SELECT A NAME'),
('LOC_SELECT_NAME' , 'lobby', 'fr_FR', 'SELECTIONNER UN NOM'),
('LOC_LETS_PLAY'   , 'lobby', 'en_US', 'LET''S PLAY!'),
('LOC_LETS_PLAY'   , 'lobby', 'fr_FR', 'C''EST PARTI!'),
('LOC_RETURN',  'playground', 'en_US', 'RETURN TO MENU'),
('LOC_RETURN',  'playground', 'fr_FR', 'RETOUR AU MENU'),
('LOC_SETTINGS','all', 'en_US', 'SETTINGS'),
('LOC_SETTINGS','all', 'fr_FR', 'PARAMETRES'),
('LOC_RESUME',  'playground', 'en_US', 'RESUME'),
('LOC_RESUME',  'playground', 'fr_FR', 'REPRENDRE'),
('LOC_VALIDATE_SETTINGS', 'settings', 'en_US', 'VALIDATE'),
('LOC_VALIDATE_SETTINGS', 'settings', 'fr_FR', 'VALIDER'),
('LOC_FULLSCREEN_ON',     'settings', 'en_US', 'FULLSCREEN: ON'),
('LOC_FULLSCREEN_ON',     'settings', 'fr_FR', 'ACTIVER PLEIN ECRAN'),
('LOC_FULLSCREEN_OFF',    'settings', 'en_US', 'FULLSCREEN: OFF'),
('LOC_FULLSCREEN_OFF',    'settings', 'fr_FR', 'DESACTIVER PLEIN ECRAN'),
('LOC_LANGUAGE_EN',       'settings', 'en_US', 'LANGUAGE: EN'),
('LOC_LANGUAGE_EN',       'settings', 'fr_FR', 'ANGLAIS'),
('LOC_LANGUAGE_FR',       'settings', 'en_US', 'LANGUAGE: FR'),
('LOC_LANGUAGE_FR',       'settings', 'fr_FR', 'FRANCAIS'),
('LOC_CONTROLS_NORMAL',   'settings', 'en_US', 'CONTROLS: NORMAL'),
('LOC_CONTROLS_NORMAL',   'settings', 'fr_FR', 'CONTROLES NORMAUX'),
('LOC_CONTROLS_INVERTED', 'settings', 'en_US', 'CONTROLS: INVERTED'),
('LOC_CONTROLS_INVERTED', 'settings', 'fr_FR', 'CONTROLES INVERSES')

-- Example of use of the localizations table
-- in the game, get the text via self.texts.get(position).
-- If it exist in the current language, it gets it
-- If it doesn't, it gets the text in the default language
-- If it doesn't exist in the default language, it gets the position instead
-- The current and default languages can be find in the config and settings files
-- You can delete these commented lines and add more entries