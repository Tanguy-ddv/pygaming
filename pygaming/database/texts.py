"""The Texts class is used to manage the texts of the game by returning strings taking automatically into account the language."""

from .database import Database
from ..settings import Settings


class Texts:
    """
    The class Texts is used to manage the texts of the game, that might be provided in several languages.
    """

    def __init__(self, database: Database) -> None:
        self._db = database
        self._text_dict = {}
    
    def get_positions(self):
        """Return all the positions (text keys)."""
        return list(self._text_dict.keys())

    def update_settings(self, settings: Settings):
        """Update the current languahe"""
        language = settings.language
        texts_list = self._db.get_texts(language)
        self._text_dict = {pos : txt for pos, txt in texts_list[0]}
    
    def get(self, position):
        """Return a piece of text."""
        if position in self._text_dict:
            return self._text_dict[position]
        return position