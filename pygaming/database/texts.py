"""The Texts class is used to manage the texts of the game."""

from .database import Database

class Texts:
    """
    The class Texts is used to manage the texts of the game, that might be provided in several languages.
    """

    def __init__(self, language: str, database: Database) -> None:
        texts_list = database.get_texts(language)
        self._text_dict = {pos : txt for pos, txt in texts_list}
    
    def get_positions(self):
        """Return all the positions (text keys)."""
        return list(self._text_dict.keys())
    
    def get(self, position):
        """Return a piece of text."""
        if position in self._text_dict:
            return self._text_dict[position]
        return position