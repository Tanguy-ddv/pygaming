"""The Texts class is used to manage the texts of the game by returning strings taking automatically into account the language."""

from .database import Database
from ..settings import Settings

class TextFormatter:
    """A TextFormatter is an object used to concatenate several pieces of texts and localizations together."""

    def __init__(self, *texts_or_locs, sep=''):
        """
        Create the TextFormatter.
        
        Params:
        ----
        - *texts_or_locs: multiple strings representing texts and localizations.
        - sep: str = '', the string to use to separete the multiple texts and localizations.
        """
        self.texts_or_locs = texts_or_locs
        self.sep = sep

class Texts:
    """
    The class Texts is used to manage the texts of the game, that might be provided in several languages.
    """

    def __init__(self, database: Database, settings: Settings, first_phase: str) -> None:
        self._db = database
        self._settings = settings
        self._last_language = settings.language
        self._all_phases_dict = self._query_db(settings.language, 'all')
        self._this_phase_dict = self._query_db(settings.language, first_phase)

    def _query_db(self, language, phase_name):
        """Query the database for the texts"""
        texts_list = self._db.get_language_texts(language, phase_name)
        return {pos : txt for pos, txt in texts_list}

    def get_all_positions(self):
        """Return all the positions (text keys) in this phase."""
        return list(self._this_phase_dict.keys()) + list(self._all_phases_dict.keys())

    def update(self, settings: Settings, phase: str):
        """Update the texts based on the new settings (new language) and/or new phase."""
        if settings.language == self._last_language:
            self._this_phase_dict = self._query_db(settings.language, phase)
        else:
            self._all_phases_dict = self._query_db(settings.language, 'all')
            self._this_phase_dict = self._query_db(settings.language, phase)
            self._last_language = settings.language

    def get(self, text_or_loc: str | TextFormatter):
        """Return a piece of text."""
        if isinstance(text_or_loc, TextFormatter):
            output = []
            for text_loc in text_or_loc.texts_or_locs:
                output.append(self.get(text_loc))
            return text_or_loc.sep.join(output)

        text = self._this_phase_dict.get(text_or_loc, None)
        if text is None:
            text = self._all_phases_dict.get(text_or_loc, text_or_loc)
        return text

    def get_values(self, loc: str):
        """Return the longest text that can be obtained for the same localization given any language."""
        return self._db.get_loc_texts(self, loc)
