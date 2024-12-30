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
        - *texts_or_locs: multiple strings representing texts and localisations.
        - sep: str = '', the string to use to separete the multiple texts and localizations.
        """
        self.texts_or_locs = texts_or_locs
        self.sep = sep

class Texts:
    """
    The class Texts is used to manage the texts of the game, that might be provided in several languages.
    """

    def __init__(self, database: Database, settings: Settings, phase_name: str) -> None:
        self._db = database
        self._settings = settings
        self._last_language = settings.language
        texts_list = self._db.get_texts(self._last_language, phase_name)
        self._text_dict = {pos : txt for pos, txt in texts_list[0]}

    def get_positions(self):
        """Return all the positions (text keys)."""
        return list(self._text_dict.keys())

    def get(self, text_or_loc: str | TextFormatter):
        """Return a piece of text."""
        if self._settings.language != self._last_language:
            self._last_language = self._settings.language
            texts_list = self._db.get_texts(self._last_language)
            self._text_dict = {pos : txt for pos, txt in texts_list[0]}

        if isinstance(text_or_loc, TextFormatter):
            output = []
            for text_loc in text_or_loc:
                output.append(self.get(text_loc))
            return text_or_loc.sep.join(output)

        if text_or_loc in self._text_dict:
            return self._text_dict[text_or_loc]
        return text_or_loc
    
    def get_values(self, loc: str):
        """Return the longest text that can be obtain for the same localization given any language."""
        return self._db.get_texts(self, loc)
