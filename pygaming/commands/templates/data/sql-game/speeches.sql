--INSERT INTO speeches (position, phase_name_or_tag, language_code, sound_path) VALUES
--('LOC_SPEECH_WELCOME', 'phase1', 'en_US', 'welcome.ogg') -- just as an example, please refer to localizations.sqlite
-- The speech files should be saved in the assets/sounds folder. Please see pygame sounds to know what extension to use.
-- Example, ('LOC_WELCOME', 'phase1', 'en_US', 'welcome.ogg') means that the sound localized at assets/sounds/welcome.ogg will be
-- played every time self.soundbox.play('LOC_WELCOME) 
