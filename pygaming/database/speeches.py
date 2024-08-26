"""The Speeches class is used to manage the speeches of the game by returning SoundFile taking automatically into account the language, use it with the Soundbox."""

from .database import Database
from ..file import SoundFile
from ..settings import Settings
from ..error import PygamingException

class Speeches:
    """
    The class Speeches is used to manage the texts of the game, that might be provided in several languages.
    """

    def __init__(self, database: Database) -> None:
        self._db = database
        self._speeches_dict = {}
    
    def get_positions(self):
        """Return all the positions (text keys)."""
        return list(self._speeches_dict.keys())

    def update_settings(self, settings: Settings):
        """Update the current language."""
        language = settings.language
        speeches_list = self._db.get_speeches(language)
        self._speeches_dict = {pos : txt for pos, txt in speeches_list[0]}
    
    def get(self, position):
        """Return a piece of text."""
        if position in self._speeches_dict:
            return SoundFile(self._speeches_dict[position]).get()
        raise PygamingException(f"The position {position} does not exist as a speech.")