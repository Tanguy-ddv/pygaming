INSERT INTO speeches (position, language_code, sound_path) VALUES
('LOC_SPEECH_WELCOME', 'en_US', 'welcome.ogg') -- just as an example, please refer to localizations.sqlite_compileoption_get
-- The speech files should be saved in the assets/sounds folder. Please see pygame sounds to know what extension to use.
-- Example, ('LOC_WELCOME', 'en_US', 'welcome.ogg') means that the sound localized at assets/sounds/welcome.ogg will be
-- played every time self.soundbox.play(Speeches.get('LOC_WELCOME')) is called, having en_US as the current language.